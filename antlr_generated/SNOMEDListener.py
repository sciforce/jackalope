# Generated from SNOMED.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SNOMEDParser import SNOMEDParser
else:
    from SNOMEDParser import SNOMEDParser

# This class defines a complete listener for a parse tree produced by SNOMEDParser.
class SNOMEDListener(ParseTreeListener):

    # Enter a parse tree produced by SNOMEDParser#expression.
    def enterExpression(self, ctx:SNOMEDParser.ExpressionContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#expression.
    def exitExpression(self, ctx:SNOMEDParser.ExpressionContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#subExpression.
    def enterSubExpression(self, ctx:SNOMEDParser.SubExpressionContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#subExpression.
    def exitSubExpression(self, ctx:SNOMEDParser.SubExpressionContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#focusConcept.
    def enterFocusConcept(self, ctx:SNOMEDParser.FocusConceptContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#focusConcept.
    def exitFocusConcept(self, ctx:SNOMEDParser.FocusConceptContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#refinement.
    def enterRefinement(self, ctx:SNOMEDParser.RefinementContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#refinement.
    def exitRefinement(self, ctx:SNOMEDParser.RefinementContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#attributeGroup.
    def enterAttributeGroup(self, ctx:SNOMEDParser.AttributeGroupContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#attributeGroup.
    def exitAttributeGroup(self, ctx:SNOMEDParser.AttributeGroupContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#attributeSet.
    def enterAttributeSet(self, ctx:SNOMEDParser.AttributeSetContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#attributeSet.
    def exitAttributeSet(self, ctx:SNOMEDParser.AttributeSetContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#attributeName.
    def enterAttributeName(self, ctx:SNOMEDParser.AttributeNameContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#attributeName.
    def exitAttributeName(self, ctx:SNOMEDParser.AttributeNameContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#attribute.
    def enterAttribute(self, ctx:SNOMEDParser.AttributeContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#attribute.
    def exitAttribute(self, ctx:SNOMEDParser.AttributeContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#stringValue.
    def enterStringValue(self, ctx:SNOMEDParser.StringValueContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#stringValue.
    def exitStringValue(self, ctx:SNOMEDParser.StringValueContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#attributeValue.
    def enterAttributeValue(self, ctx:SNOMEDParser.AttributeValueContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#attributeValue.
    def exitAttributeValue(self, ctx:SNOMEDParser.AttributeValueContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#booleanValue.
    def enterBooleanValue(self, ctx:SNOMEDParser.BooleanValueContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#booleanValue.
    def exitBooleanValue(self, ctx:SNOMEDParser.BooleanValueContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#expressionValue.
    def enterExpressionValue(self, ctx:SNOMEDParser.ExpressionValueContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#expressionValue.
    def exitExpressionValue(self, ctx:SNOMEDParser.ExpressionValueContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#conceptreference.
    def enterConceptreference(self, ctx:SNOMEDParser.ConceptreferenceContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#conceptreference.
    def exitConceptreference(self, ctx:SNOMEDParser.ConceptreferenceContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#conceptId.
    def enterConceptId(self, ctx:SNOMEDParser.ConceptIdContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#conceptId.
    def exitConceptId(self, ctx:SNOMEDParser.ConceptIdContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#numericValue.
    def enterNumericValue(self, ctx:SNOMEDParser.NumericValueContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#numericValue.
    def exitNumericValue(self, ctx:SNOMEDParser.NumericValueContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#decimal.
    def enterDecimal(self, ctx:SNOMEDParser.DecimalContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#decimal.
    def exitDecimal(self, ctx:SNOMEDParser.DecimalContext):
        pass


    # Enter a parse tree produced by SNOMEDParser#integer.
    def enterInteger(self, ctx:SNOMEDParser.IntegerContext):
        pass

    # Exit a parse tree produced by SNOMEDParser#integer.
    def exitInteger(self, ctx:SNOMEDParser.IntegerContext):
        pass



del SNOMEDParser