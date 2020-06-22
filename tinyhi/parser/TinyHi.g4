grammar TinyHi;

program: NEWLINE* block* ;

statements: (statement NEWLINE)* ;

statement: WS? stat WS? ;

stat: identifier '<-' expr? #assignStat
    | ifstat                #ifStat
    | whilestat             #whileStat
    | untilstat             #untilStat
    | block                 #blockStat
    | expr                  #exprStat
    ;

block: BEGIN (identifier formalparams)? NEWLINE statements END; 

ifstat: IF expr BOOLOP expr THEN NEWLINE statements (ELSE NEWLINE statements)? END; 
whilestat: WHILE expr BOOLOP expr NEWLINE statements END;
untilstat: UNTIL expr BOOLOP expr NEWLINE statements END;

expr: WS? '(' expr ')' WS?          #parenExpr
    | functioncall                  #callExpr
    | expr WS? '[' expr ']' WS?     #indexExpr
    | expr WS expr                  #concatExpr
    | '#' expr                      #lenExpr
    | '~' expr                      #negExpr
    | expr ('*'|'/') expr           #mulDivExpr
    | expr ('+'|'-') expr           #addSubExpr
    | number                        #numExpr
    | identifier                    #varExpr
    | string                        #strExpr
    ;

functioncall: identifier actualparams ;
actualparams: '(' (expr (',' expr)*)? ')';
formalparams: '(' (identifier (',' identifier)*)? ')' ;

identifier: WS? IDENTIFIER WS? ;
number: WS? NUMBER WS? ;
string: WS? STRING WS? ;

COMMENT: ('//' ~[\n]) -> skip ;

BOOLOP: '='|'<'|'>'|'<='|'>=' ;

IF: WS? 'IF' WS? ;
THEN: WS? 'THEN' WS? ;
ELSE: WS? 'ELSE' WS?;
END: WS? 'END' WS? ;
WHILE: WS? 'WHILE' WS? ;
UNTIL: WS? 'UNTIL' WS? ;
BEGIN: WS? 'BEGIN' WS? ;

IDENTIFIER: [a-zA-Z_] [a-zA-Z0-9_]* ;
NUMBER: '0' | ('+'|'-')? ([1-9] [0-9]*) ;

STRING: '"' ~('"')* '"' ;
WS: ' '+ ;
NEWLINE: ('\r'? '\n')+ ;
TABS: [\t] -> skip ;