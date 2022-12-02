// Copyright 2022 Sciforce Ukraine. All rights reserved.
grammar SNOMED;

fragment T               : [Tt];
fragment R               : [Rr];
fragment U               : [Uu];
fragment E               : [Ee];

fragment F               : [Ff];
fragment A               : [Aa];
fragment L               : [Ll];
fragment S               : [Ss];

/* TOKENS */
NONZERODIGIT             : [1-9];
DIGIT                    : [0-9];
SCTID                    : NONZERODIGIT DIGIT+ ;
DEFINITIONSTATUS         : (EQUIVALENTTO|SUBTYPEOF) ;

WS                       : (' '|'\t'|'\n'|'\r') -> skip;
QM                       : ('"');

EQUIVALENTTO             : '===';
SUBTYPEOF                : '<<<';

TRUE                     : T R U E ;
FALSE                    : F A L S E ;

CONCEPTNAME              : '|'  ~'|'+  '|';

/* RULES */
expression               :  (DEFINITIONSTATUS  )? subExpression  EOF;
subExpression            : focusConcept ( ':'  refinement)? ;
focusConcept             : conceptreference ( '+'  conceptreference)* ;
refinement               : (attributeSet | attributeGroup) ( (',' )? attributeGroup)* ;
attributeGroup           : '{'  attributeSet  '}' ;
attributeSet             : attribute ( ','  attribute)* ;
attributeName            : conceptreference ;
attribute                : attributeName  '='  attributeValue ;
stringValue              : ~'"'+;
attributeValue           : (expressionValue | QM stringValue QM | booleanValue | '#' numericValue) ;
booleanValue             : (TRUE|FALSE);
expressionValue          : (conceptreference | '('  subExpression  ')');
conceptreference         : conceptId (CONCEPTNAME)? ;
conceptId                : SCTID ;


//Moved to the bottom to not interfere with SCTID
numericValue             : ('-'|'+')? (decimal|integer);
decimal                  : integer '.' (DIGIT)+;
integer                  : ('0' | NONZERODIGIT (DIGIT)*);
