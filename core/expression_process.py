import random
from typing import Optional, Iterable

import antlr4

import core.expression
from antlr_generated.SNOMEDLexer import SNOMEDLexer
from antlr_generated.SNOMEDListener import SNOMEDListener
from antlr_generated.SNOMEDParser import SNOMEDParser
from core import data_model


def _new_concept_id() -> Iterable[int]:
    """Generates a temporary concept_id for nested subexpressions so that parent expressions can use it"""
    i = 0
    while True:
        i -= random.randint(1, 100)
        yield i


# Specific processing errors
class SNOMEDExpressionsError(Exception):
    pass


# Construct the concept from nodes
class Processor(SNOMEDListener):

    def __init__(self) -> None:
        super().__init__()

        # Context flags and lists
        self.parent_flag: bool = False
        self.attribute_list: list = list()
        self.awaiting_attribute: bool = False
        self.awaiting_value: bool = False
        self.current_attribute, self.current_value = 0, 0
        self.concrete_relationship: bool = False
        self.set_counter_stack: list[int] = []
        self.expect_numeric_value: bool = False

        # Expression stack for complex expressions with subexpressions
        self.expression_stack = []
        self.expression_store = []

        # Custom concept identfier to use inside the complex expression
        self.custom_concept_id: Optional[int] = None

    def enterSubExpression(self, ctx: SNOMEDParser.SubExpressionContext):
        e = core.expression.Expression()
        e.concept_id = next(_new_concept_id())  # type: ignore
        self.set_counter_stack.append(0)
        self.expression_stack.append(e)
        return super().enterSubExpression(ctx)
    
    def exitSubExpression(self, ctx: SNOMEDParser.SubExpressionContext):
        e = self.expression_stack.pop()
        self.expression_store.append(e)
        self.set_counter_stack.pop()
        if self.expression_stack and self.expression_stack[0] != e:
            self.current_value = e.concept_id
        return super().exitSubExpression(ctx)

    # Get parent_concepts from the SCTID nodes
    def enterFocusConcept(self, ctx: SNOMEDParser.FocusConceptContext):
        self.parent_flag = True
        # Iterate over immediate children and add them to the parent_concepts
        return super().enterFocusConcept(ctx)

    def exitFocusConcept(self, ctx: SNOMEDParser.FocusConceptContext):
        self.parent_flag = False
        return super().exitFocusConcept(ctx)
    
    # Get definition status. Defaults to equivalence.
    def exitExpression(self, ctx: SNOMEDParser.ExpressionContext):
        if ctx.DEFINITIONSTATUS() is None or ctx.DEFINITIONSTATUS() == '===':
            self.expression_store[0].definition_status = True
        else:
            self.expression_store[0].definition_status = False
        super().exitExpression(ctx)

    # Group counter
    def enterAttributeGroup(self, ctx: SNOMEDParser.AttributeGroupContext):
        # If there are no ungroupped attributes, append an empty group at index 0
        if self.set_counter_stack[-1] < 1:
            empty_ungroupped_attributes = data_model.RelationshipGroup(tuple())
            self.expression_stack[-1].add_relationship_group(empty_ungroupped_attributes)
        return super().enterAttributeGroup(ctx)

    # Attribute sets contain one or more attributes and are separated by groups
    def enterAttributeSet(self, ctx: SNOMEDParser.AttributeSetContext):
        self.set_counter_stack[-1] += 1
        self.attribute_list = list()
        return super().enterAttributeSet(ctx)
    
    def exitAttributeSet(self, ctx: SNOMEDParser.AttributeSetContext):
        rel_group = data_model.RelationshipGroup.freeze(self.attribute_list)
        self.expression_stack[-1].add_relationship_group(rel_group)
        return super().exitAttributeSet(ctx)

    # On entering an attribute, look for attribute SCTID or value
    def enterAttributeName(self, ctx: SNOMEDParser.AttributeNameContext):
        self.concrete_relationship = True
        self.awaiting_attribute = True
        return super().enterAttributeName(ctx)

    def exitAttributeValue(self, ctx: SNOMEDParser.AttributeValueContext):
        # Always reset the value flag
        self.awaiting_value = False

        # Create the relationship object
        if self.concrete_relationship:
            rel = data_model.ConcreteRelationship(
                typeId=self.current_attribute,
                concreteValue=self.current_value
                )
        else:
            rel = data_model.Relationship(
                typeId=self.current_attribute,
                destinationId=self.current_value  # type: ignore
                )
        
        self.attribute_list.append(rel)        
        return super().exitAttributeValue(ctx)

    # Process different Value types    
    def enterStringValue(self, ctx: SNOMEDParser.StringValueContext):
        self.current_value = ctx.getText()
        return super().enterStringValue(ctx)
    
    def enterBooleanValue(self, ctx: SNOMEDParser.BooleanValueContext):
        text = ctx.getText().lower()
        self.current_value = (text == 'true')
        return super().enterBooleanValue(ctx)

    def enterNumericValue(self, ctx: SNOMEDParser.NumericValueContext):
        self.expect_numeric_value = True
        return super().enterNumericValue(ctx)
        
    def enterDecimal(self, ctx: SNOMEDParser.DecimalContext):
        self.current_value = float(ctx.getText())
        self.expect_numeric_value = False
        return super().enterDecimal(ctx)
    
    def enterInteger(self, ctx: SNOMEDParser.IntegerContext):
        # Only process integer values that were not part of decimal definition
        if self.expect_numeric_value:
            self.current_value = int(ctx.getText())
        return super().enterInteger(ctx)
    
    def enterExpressionValue(self, ctx: SNOMEDParser.ExpressionValueContext):
        # Rest is handled by entering ConceptId and exiting Subexpression
        self.concrete_relationship = False
        return super().enterExpressionValue(ctx)

    def enterConceptId(self, ctx: SNOMEDParser.ConceptIdContext):
        sctid = int(ctx.getText())
        if self.parent_flag:
            self.expression_stack[-1].add_parent(sctid)
        elif self.awaiting_attribute:
            self.current_attribute, self.awaiting_attribute, self.awaiting_value = sctid, False, True
        elif self.awaiting_value:
            self.current_value = sctid

        return super().enterConceptId(ctx)
    
    def process(self, expression):
        
        def parse(expr: str):
            lexer = SNOMEDLexer(antlr4.InputStream(expr))
            stream = antlr4.CommonTokenStream(lexer)
            parser = SNOMEDParser(stream)
            return parser.expression()
        
        walker = antlr4.ParseTreeWalker()
        tree = parse(expression)
        walker.walk(self, tree)
        return self.expression_store
