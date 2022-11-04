# Copyright 2022 Sciforce Ukraine. All rights reserved.
import random
from typing import Optional, Iterable

import antlr4

import core.expression
from antlr_generated.SNOMEDLexer import SNOMEDLexer
from antlr_generated.SNOMEDListener import SNOMEDListener
from antlr_generated.SNOMEDParser import SNOMEDParser
from core import data_model


def _new_concept_id() -> Iterable[int]:
    """Generates a temporary SCTID for nested subexpressions so that parent expressions can use it"""
    i = 0
    while True:
        i -= 1
        yield i


# Construct the concept from nodes
class Processor(SNOMEDListener):

    def __init__(self) -> None:
        super().__init__()

        # Context flags and stacks
        self._parent_flag: bool = False
        self._attribute_list: list = list()
        self._awaiting_attribute: bool = False
        self._awaiting_value: bool = False
        self._current_attribute, self._current_value = 0, 0
        self._concrete_relationship: bool = False
        self._set_counter_stack: list[int] = []
        self._expecting_numeric_value: bool = False

        # Expression stack for complex expressions with subexpressions
        self.expression_stack = []
        self.expression_store = []

        # Custom concept identfier to use inside the complex expression
        self.custom_concept_id: Optional[int] = None

    def enterSubExpression(self, ctx: SNOMEDParser.SubExpressionContext):
        e = core.expression.Expression()
        e.concept_id = next(_new_concept_id())  # type: ignore
        self._set_counter_stack.append(0)
        self.expression_stack.append(e)
        return super().enterSubExpression(ctx)
    
    def exitSubExpression(self, ctx: SNOMEDParser.SubExpressionContext):
        e = self.expression_stack.pop()
        self.expression_store.append(e)
        self._set_counter_stack.pop()
        if self.expression_stack and self.expression_stack[0] != e:
            self._current_value = e.concept_id
        return super().exitSubExpression(ctx)

    # Get parent_concepts from the SCTID nodes
    def enterFocusConcept(self, ctx: SNOMEDParser.FocusConceptContext):
        self._parent_flag = True
        # Iterate over immediate children and add them to the parent_concepts
        return super().enterFocusConcept(ctx)

    def exitFocusConcept(self, ctx: SNOMEDParser.FocusConceptContext):
        self._parent_flag = False
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
        if self._set_counter_stack[-1] < 1:
            empty_ungroupped_attributes = data_model.RelationshipGroup(tuple())
            self.expression_stack[-1].add_relationship_group(empty_ungroupped_attributes)
        return super().enterAttributeGroup(ctx)

    # Attribute sets contain one or more attributes and are separated by groups
    def enterAttributeSet(self, ctx: SNOMEDParser.AttributeSetContext):
        self._set_counter_stack[-1] += 1
        self._attribute_list = list()
        return super().enterAttributeSet(ctx)
    
    def exitAttributeSet(self, ctx: SNOMEDParser.AttributeSetContext):
        rel_group = data_model.RelationshipGroup.freeze(self._attribute_list)
        self.expression_stack[-1].add_relationship_group(rel_group)
        return super().exitAttributeSet(ctx)

    # On entering an attribute, look for attribute SCTID or value
    def enterAttributeName(self, ctx: SNOMEDParser.AttributeNameContext):
        self._concrete_relationship = True
        self._awaiting_attribute = True
        return super().enterAttributeName(ctx)

    def exitAttributeValue(self, ctx: SNOMEDParser.AttributeValueContext):
        # Always reset the value flag
        self._awaiting_value = False

        # Create the relationship object
        if self._concrete_relationship:
            rel = data_model.ConcreteRelationship(
                typeId=self._current_attribute,
                concreteValue=self._current_value
                )
        else:
            rel = data_model.Relationship(
                typeId=self._current_attribute,
                destinationId=self._current_value  # type: ignore
                )
        
        self._attribute_list.append(rel)
        return super().exitAttributeValue(ctx)

    # Process different Value types    
    def enterStringValue(self, ctx: SNOMEDParser.StringValueContext):
        self._current_value = ctx.getText()
        return super().enterStringValue(ctx)
    
    def enterBooleanValue(self, ctx: SNOMEDParser.BooleanValueContext):
        text = ctx.getText().lower()
        self._current_value = (text == 'true')
        return super().enterBooleanValue(ctx)

    def enterNumericValue(self, ctx: SNOMEDParser.NumericValueContext):
        self._expecting_numeric_value = True
        return super().enterNumericValue(ctx)
        
    def enterDecimal(self, ctx: SNOMEDParser.DecimalContext):
        self._current_value = float(ctx.getText())
        self._expecting_numeric_value = False
        return super().enterDecimal(ctx)
    
    def enterInteger(self, ctx: SNOMEDParser.IntegerContext):
        # Only process integer values that were not part of decimal definition
        if self._expecting_numeric_value:
            self._current_value = int(ctx.getText())
        return super().enterInteger(ctx)
    
    def enterExpressionValue(self, ctx: SNOMEDParser.ExpressionValueContext):
        # Rest is handled by entering ConceptId and exiting Subexpression
        self._concrete_relationship = False
        return super().enterExpressionValue(ctx)

    def enterConceptId(self, ctx: SNOMEDParser.ConceptIdContext):
        sctid = int(ctx.getText())
        if self._parent_flag:
            self.expression_stack[-1].add_parent(sctid)
        elif self._awaiting_attribute:
            self._current_attribute, self._awaiting_attribute, self._awaiting_value = sctid, False, True
        elif self._awaiting_value:
            self._current_value = sctid

        return super().enterConceptId(ctx)
    
    def process(self, expression) -> list[core.expression.Expression]:
        
        def parse(expr: str):
            lexer = SNOMEDLexer(antlr4.InputStream(expr))
            stream = antlr4.CommonTokenStream(lexer)
            parser = SNOMEDParser(stream)
            return parser.expression()
        
        walker = antlr4.ParseTreeWalker()
        tree = parse(expression)
        walker.walk(self, tree)
        return self.expression_store
