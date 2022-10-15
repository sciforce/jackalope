# Generated from SNOMED.g4 by ANTLR 4.11.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,24,139,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,1,0,3,0,36,8,0,1,0,1,0,1,0,1,1,1,1,
        1,1,3,1,44,8,1,1,2,1,2,1,2,5,2,49,8,2,10,2,12,2,52,9,2,1,3,1,3,3,
        3,56,8,3,1,3,3,3,59,8,3,1,3,5,3,62,8,3,10,3,12,3,65,9,3,1,4,1,4,
        1,4,1,4,1,5,1,5,1,5,5,5,74,8,5,10,5,12,5,77,9,5,1,6,1,6,1,7,1,7,
        1,7,1,7,1,8,4,8,86,8,8,11,8,12,8,87,1,9,1,9,1,9,1,9,1,9,1,9,1,9,
        1,9,3,9,98,8,9,1,10,1,10,1,11,1,11,1,11,1,11,1,11,3,11,107,8,11,
        1,12,1,12,3,12,111,8,12,1,13,1,13,1,14,3,14,116,8,14,1,14,1,14,3,
        14,120,8,14,1,15,1,15,1,15,4,15,125,8,15,11,15,12,15,126,1,16,1,
        16,1,16,5,16,132,8,16,10,16,12,16,135,9,16,3,16,137,8,16,1,16,0,
        0,17,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,0,3,1,0,7,7,1,
        0,22,23,2,0,2,2,11,11,139,0,35,1,0,0,0,2,40,1,0,0,0,4,45,1,0,0,0,
        6,55,1,0,0,0,8,66,1,0,0,0,10,70,1,0,0,0,12,78,1,0,0,0,14,80,1,0,
        0,0,16,85,1,0,0,0,18,97,1,0,0,0,20,99,1,0,0,0,22,106,1,0,0,0,24,
        108,1,0,0,0,26,112,1,0,0,0,28,115,1,0,0,0,30,121,1,0,0,0,32,136,
        1,0,0,0,34,36,5,17,0,0,35,34,1,0,0,0,35,36,1,0,0,0,36,37,1,0,0,0,
        37,38,3,2,1,0,38,39,5,0,0,1,39,1,1,0,0,0,40,43,3,4,2,0,41,42,5,1,
        0,0,42,44,3,6,3,0,43,41,1,0,0,0,43,44,1,0,0,0,44,3,1,0,0,0,45,50,
        3,24,12,0,46,47,5,2,0,0,47,49,3,24,12,0,48,46,1,0,0,0,49,52,1,0,
        0,0,50,48,1,0,0,0,50,51,1,0,0,0,51,5,1,0,0,0,52,50,1,0,0,0,53,56,
        3,10,5,0,54,56,3,8,4,0,55,53,1,0,0,0,55,54,1,0,0,0,56,63,1,0,0,0,
        57,59,5,3,0,0,58,57,1,0,0,0,58,59,1,0,0,0,59,60,1,0,0,0,60,62,3,
        8,4,0,61,58,1,0,0,0,62,65,1,0,0,0,63,61,1,0,0,0,63,64,1,0,0,0,64,
        7,1,0,0,0,65,63,1,0,0,0,66,67,5,4,0,0,67,68,3,10,5,0,68,69,5,5,0,
        0,69,9,1,0,0,0,70,75,3,14,7,0,71,72,5,3,0,0,72,74,3,14,7,0,73,71,
        1,0,0,0,74,77,1,0,0,0,75,73,1,0,0,0,75,76,1,0,0,0,76,11,1,0,0,0,
        77,75,1,0,0,0,78,79,3,24,12,0,79,13,1,0,0,0,80,81,3,12,6,0,81,82,
        5,6,0,0,82,83,3,18,9,0,83,15,1,0,0,0,84,86,8,0,0,0,85,84,1,0,0,0,
        86,87,1,0,0,0,87,85,1,0,0,0,87,88,1,0,0,0,88,17,1,0,0,0,89,98,3,
        22,11,0,90,91,5,19,0,0,91,92,3,16,8,0,92,93,5,19,0,0,93,98,1,0,0,
        0,94,98,3,20,10,0,95,96,5,8,0,0,96,98,3,28,14,0,97,89,1,0,0,0,97,
        90,1,0,0,0,97,94,1,0,0,0,97,95,1,0,0,0,98,19,1,0,0,0,99,100,7,1,
        0,0,100,21,1,0,0,0,101,107,3,24,12,0,102,103,5,9,0,0,103,104,3,2,
        1,0,104,105,5,10,0,0,105,107,1,0,0,0,106,101,1,0,0,0,106,102,1,0,
        0,0,107,23,1,0,0,0,108,110,3,26,13,0,109,111,5,24,0,0,110,109,1,
        0,0,0,110,111,1,0,0,0,111,25,1,0,0,0,112,113,5,16,0,0,113,27,1,0,
        0,0,114,116,7,2,0,0,115,114,1,0,0,0,115,116,1,0,0,0,116,119,1,0,
        0,0,117,120,3,30,15,0,118,120,3,32,16,0,119,117,1,0,0,0,119,118,
        1,0,0,0,120,29,1,0,0,0,121,122,3,32,16,0,122,124,5,12,0,0,123,125,
        5,15,0,0,124,123,1,0,0,0,125,126,1,0,0,0,126,124,1,0,0,0,126,127,
        1,0,0,0,127,31,1,0,0,0,128,137,5,13,0,0,129,133,5,14,0,0,130,132,
        5,15,0,0,131,130,1,0,0,0,132,135,1,0,0,0,133,131,1,0,0,0,133,134,
        1,0,0,0,134,137,1,0,0,0,135,133,1,0,0,0,136,128,1,0,0,0,136,129,
        1,0,0,0,137,33,1,0,0,0,16,35,43,50,55,58,63,75,87,97,106,110,115,
        119,126,133,136
    ]

class SNOMEDParser ( Parser ):

    grammarFileName = "SNOMED.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "':'", "'+'", "','", "'{'", "'}'", "'='", 
                     "'\"'", "'#'", "'('", "')'", "'-'", "'.'", "'0'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'==='", "'<<<'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "NONZERODIGIT", "DIGIT", 
                      "SCTID", "DEFINITIONSTATUS", "WS", "QM", "EQUIVALENTTO", 
                      "SUBTYPEOF", "TRUE", "FALSE", "CONCEPTNAME" ]

    RULE_expression = 0
    RULE_subExpression = 1
    RULE_focusConcept = 2
    RULE_refinement = 3
    RULE_attributeGroup = 4
    RULE_attributeSet = 5
    RULE_attributeName = 6
    RULE_attribute = 7
    RULE_stringValue = 8
    RULE_attributeValue = 9
    RULE_booleanValue = 10
    RULE_expressionValue = 11
    RULE_conceptreference = 12
    RULE_conceptId = 13
    RULE_numericValue = 14
    RULE_decimal = 15
    RULE_integer = 16

    ruleNames =  [ "expression", "subExpression", "focusConcept", "refinement", 
                   "attributeGroup", "attributeSet", "attributeName", "attribute", 
                   "stringValue", "attributeValue", "booleanValue", "expressionValue", 
                   "conceptreference", "conceptId", "numericValue", "decimal", 
                   "integer" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    NONZERODIGIT=14
    DIGIT=15
    SCTID=16
    DEFINITIONSTATUS=17
    WS=18
    QM=19
    EQUIVALENTTO=20
    SUBTYPEOF=21
    TRUE=22
    FALSE=23
    CONCEPTNAME=24

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.11.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def subExpression(self):
            return self.getTypedRuleContext(SNOMEDParser.SubExpressionContext,0)


        def EOF(self):
            return self.getToken(SNOMEDParser.EOF, 0)

        def DEFINITIONSTATUS(self):
            return self.getToken(SNOMEDParser.DEFINITIONSTATUS, 0)

        def getRuleIndex(self):
            return SNOMEDParser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)




    def expression(self):

        localctx = SNOMEDParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 35
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 34
                self.match(SNOMEDParser.DEFINITIONSTATUS)


            self.state = 37
            self.subExpression()
            self.state = 38
            self.match(SNOMEDParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SubExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def focusConcept(self):
            return self.getTypedRuleContext(SNOMEDParser.FocusConceptContext,0)


        def refinement(self):
            return self.getTypedRuleContext(SNOMEDParser.RefinementContext,0)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_subExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSubExpression" ):
                listener.enterSubExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSubExpression" ):
                listener.exitSubExpression(self)




    def subExpression(self):

        localctx = SNOMEDParser.SubExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_subExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self.focusConcept()
            self.state = 43
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 41
                self.match(SNOMEDParser.T__0)
                self.state = 42
                self.refinement()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FocusConceptContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conceptreference(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SNOMEDParser.ConceptreferenceContext)
            else:
                return self.getTypedRuleContext(SNOMEDParser.ConceptreferenceContext,i)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_focusConcept

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFocusConcept" ):
                listener.enterFocusConcept(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFocusConcept" ):
                listener.exitFocusConcept(self)




    def focusConcept(self):

        localctx = SNOMEDParser.FocusConceptContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_focusConcept)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45
            self.conceptreference()
            self.state = 50
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==2:
                self.state = 46
                self.match(SNOMEDParser.T__1)
                self.state = 47
                self.conceptreference()
                self.state = 52
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RefinementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attributeSet(self):
            return self.getTypedRuleContext(SNOMEDParser.AttributeSetContext,0)


        def attributeGroup(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SNOMEDParser.AttributeGroupContext)
            else:
                return self.getTypedRuleContext(SNOMEDParser.AttributeGroupContext,i)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_refinement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRefinement" ):
                listener.enterRefinement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRefinement" ):
                listener.exitRefinement(self)




    def refinement(self):

        localctx = SNOMEDParser.RefinementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_refinement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16]:
                self.state = 53
                self.attributeSet()
                pass
            elif token in [4]:
                self.state = 54
                self.attributeGroup()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 63
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==3 or _la==4:
                self.state = 58
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==3:
                    self.state = 57
                    self.match(SNOMEDParser.T__2)


                self.state = 60
                self.attributeGroup()
                self.state = 65
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttributeGroupContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attributeSet(self):
            return self.getTypedRuleContext(SNOMEDParser.AttributeSetContext,0)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_attributeGroup

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttributeGroup" ):
                listener.enterAttributeGroup(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttributeGroup" ):
                listener.exitAttributeGroup(self)




    def attributeGroup(self):

        localctx = SNOMEDParser.AttributeGroupContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_attributeGroup)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.match(SNOMEDParser.T__3)
            self.state = 67
            self.attributeSet()
            self.state = 68
            self.match(SNOMEDParser.T__4)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttributeSetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attribute(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SNOMEDParser.AttributeContext)
            else:
                return self.getTypedRuleContext(SNOMEDParser.AttributeContext,i)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_attributeSet

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttributeSet" ):
                listener.enterAttributeSet(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttributeSet" ):
                listener.exitAttributeSet(self)




    def attributeSet(self):

        localctx = SNOMEDParser.AttributeSetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_attributeSet)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            self.attribute()
            self.state = 75
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,6,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 71
                    self.match(SNOMEDParser.T__2)
                    self.state = 72
                    self.attribute() 
                self.state = 77
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttributeNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conceptreference(self):
            return self.getTypedRuleContext(SNOMEDParser.ConceptreferenceContext,0)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_attributeName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttributeName" ):
                listener.enterAttributeName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttributeName" ):
                listener.exitAttributeName(self)




    def attributeName(self):

        localctx = SNOMEDParser.AttributeNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_attributeName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.conceptreference()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttributeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attributeName(self):
            return self.getTypedRuleContext(SNOMEDParser.AttributeNameContext,0)


        def attributeValue(self):
            return self.getTypedRuleContext(SNOMEDParser.AttributeValueContext,0)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_attribute

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttribute" ):
                listener.enterAttribute(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttribute" ):
                listener.exitAttribute(self)




    def attribute(self):

        localctx = SNOMEDParser.AttributeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_attribute)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 80
            self.attributeName()
            self.state = 81
            self.match(SNOMEDParser.T__5)
            self.state = 82
            self.attributeValue()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StringValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SNOMEDParser.RULE_stringValue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStringValue" ):
                listener.enterStringValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStringValue" ):
                listener.exitStringValue(self)




    def stringValue(self):

        localctx = SNOMEDParser.StringValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_stringValue)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 84
                    _la = self._input.LA(1)
                    if _la <= 0 or _la==7:
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 87 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttributeValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expressionValue(self):
            return self.getTypedRuleContext(SNOMEDParser.ExpressionValueContext,0)


        def QM(self, i:int=None):
            if i is None:
                return self.getTokens(SNOMEDParser.QM)
            else:
                return self.getToken(SNOMEDParser.QM, i)

        def stringValue(self):
            return self.getTypedRuleContext(SNOMEDParser.StringValueContext,0)


        def booleanValue(self):
            return self.getTypedRuleContext(SNOMEDParser.BooleanValueContext,0)


        def numericValue(self):
            return self.getTypedRuleContext(SNOMEDParser.NumericValueContext,0)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_attributeValue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttributeValue" ):
                listener.enterAttributeValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttributeValue" ):
                listener.exitAttributeValue(self)




    def attributeValue(self):

        localctx = SNOMEDParser.AttributeValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_attributeValue)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [9, 16]:
                self.state = 89
                self.expressionValue()
                pass
            elif token in [19]:
                self.state = 90
                self.match(SNOMEDParser.QM)
                self.state = 91
                self.stringValue()
                self.state = 92
                self.match(SNOMEDParser.QM)
                pass
            elif token in [22, 23]:
                self.state = 94
                self.booleanValue()
                pass
            elif token in [8]:
                self.state = 95
                self.match(SNOMEDParser.T__7)
                self.state = 96
                self.numericValue()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BooleanValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TRUE(self):
            return self.getToken(SNOMEDParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(SNOMEDParser.FALSE, 0)

        def getRuleIndex(self):
            return SNOMEDParser.RULE_booleanValue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBooleanValue" ):
                listener.enterBooleanValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBooleanValue" ):
                listener.exitBooleanValue(self)




    def booleanValue(self):

        localctx = SNOMEDParser.BooleanValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_booleanValue)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 99
            _la = self._input.LA(1)
            if not(_la==22 or _la==23):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conceptreference(self):
            return self.getTypedRuleContext(SNOMEDParser.ConceptreferenceContext,0)


        def subExpression(self):
            return self.getTypedRuleContext(SNOMEDParser.SubExpressionContext,0)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_expressionValue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpressionValue" ):
                listener.enterExpressionValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpressionValue" ):
                listener.exitExpressionValue(self)




    def expressionValue(self):

        localctx = SNOMEDParser.ExpressionValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_expressionValue)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 106
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16]:
                self.state = 101
                self.conceptreference()
                pass
            elif token in [9]:
                self.state = 102
                self.match(SNOMEDParser.T__8)
                self.state = 103
                self.subExpression()
                self.state = 104
                self.match(SNOMEDParser.T__9)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConceptreferenceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conceptId(self):
            return self.getTypedRuleContext(SNOMEDParser.ConceptIdContext,0)


        def CONCEPTNAME(self):
            return self.getToken(SNOMEDParser.CONCEPTNAME, 0)

        def getRuleIndex(self):
            return SNOMEDParser.RULE_conceptreference

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConceptreference" ):
                listener.enterConceptreference(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConceptreference" ):
                listener.exitConceptreference(self)




    def conceptreference(self):

        localctx = SNOMEDParser.ConceptreferenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_conceptreference)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 108
            self.conceptId()
            self.state = 110
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==24:
                self.state = 109
                self.match(SNOMEDParser.CONCEPTNAME)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConceptIdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SCTID(self):
            return self.getToken(SNOMEDParser.SCTID, 0)

        def getRuleIndex(self):
            return SNOMEDParser.RULE_conceptId

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConceptId" ):
                listener.enterConceptId(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConceptId" ):
                listener.exitConceptId(self)




    def conceptId(self):

        localctx = SNOMEDParser.ConceptIdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_conceptId)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 112
            self.match(SNOMEDParser.SCTID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumericValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def decimal(self):
            return self.getTypedRuleContext(SNOMEDParser.DecimalContext,0)


        def integer(self):
            return self.getTypedRuleContext(SNOMEDParser.IntegerContext,0)


        def getRuleIndex(self):
            return SNOMEDParser.RULE_numericValue

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumericValue" ):
                listener.enterNumericValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumericValue" ):
                listener.exitNumericValue(self)




    def numericValue(self):

        localctx = SNOMEDParser.NumericValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_numericValue)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 115
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2 or _la==11:
                self.state = 114
                _la = self._input.LA(1)
                if not(_la==2 or _la==11):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


            self.state = 119
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,12,self._ctx)
            if la_ == 1:
                self.state = 117
                self.decimal()
                pass

            elif la_ == 2:
                self.state = 118
                self.integer()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DecimalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def integer(self):
            return self.getTypedRuleContext(SNOMEDParser.IntegerContext,0)


        def DIGIT(self, i:int=None):
            if i is None:
                return self.getTokens(SNOMEDParser.DIGIT)
            else:
                return self.getToken(SNOMEDParser.DIGIT, i)

        def getRuleIndex(self):
            return SNOMEDParser.RULE_decimal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDecimal" ):
                listener.enterDecimal(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDecimal" ):
                listener.exitDecimal(self)




    def decimal(self):

        localctx = SNOMEDParser.DecimalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_decimal)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 121
            self.integer()
            self.state = 122
            self.match(SNOMEDParser.T__11)
            self.state = 124 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 123
                self.match(SNOMEDParser.DIGIT)
                self.state = 126 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==15):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IntegerContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NONZERODIGIT(self):
            return self.getToken(SNOMEDParser.NONZERODIGIT, 0)

        def DIGIT(self, i:int=None):
            if i is None:
                return self.getTokens(SNOMEDParser.DIGIT)
            else:
                return self.getToken(SNOMEDParser.DIGIT, i)

        def getRuleIndex(self):
            return SNOMEDParser.RULE_integer

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInteger" ):
                listener.enterInteger(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInteger" ):
                listener.exitInteger(self)




    def integer(self):

        localctx = SNOMEDParser.IntegerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 136
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [13]:
                self.state = 128
                self.match(SNOMEDParser.T__12)
                pass
            elif token in [14]:
                self.state = 129
                self.match(SNOMEDParser.NONZERODIGIT)
                self.state = 133
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==15:
                    self.state = 130
                    self.match(SNOMEDParser.DIGIT)
                    self.state = 135
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





