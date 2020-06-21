grammar TinyHi;

program: NEWLINE* block* ;

statements: (stat NEWLINE)* ;

stat: IDENTIFIER '<-' expr? #assignStat
    | ifstat                #ifStat
    | whilestat             #whileStat
    | untilstat             #untilStat
    | block                 #blockStat
    | expr                  #exprStat
    ;

block: BEGIN (IDENTIFIER formalparams)? NEWLINE statements END; 

ifstat: IF expr BOOLOP expr THEN NEWLINE statements (ELSE NEWLINE statements)? END; 
whilestat: WHILE expr BOOLOP expr NEWLINE statements END;
untilstat: UNTIL expr BOOLOP expr NEWLINE statements END;

expr: expr expr             #concatExpr
    | expr ('*'|'/') expr   #mulDivExpr
    | expr ('+'|'-') expr   #addSubExpr
    | functioncall          #callExpr
    | arrayindexing         #indexExpr
    | NUMBER                #numExpr
    | IDENTIFIER            #idExpr
    | STRING                #strExpr
    | '(' expr ')'          #parenExpr
    | '~' expr              #negExpr
    | '#' expr              #lenExpr
    ;

arrayindexing: (IDENTIFIER|STRING) '[' expr ']' ;
functioncall: IDENTIFIER actualparams ;
actualparams: '(' (expr (',' expr)*)? ')';
formalparams: '(' (IDENTIFIER (',' IDENTIFIER)*)? ')' ;

COMMENT: ('//' ~[\n]) -> skip ;

BOOLOP: '='|'<'|'>'|'<='|'>=' ;

IF: 'IF' ;
THEN: 'THEN' ;
ELSE: 'ELSE' ;
END: 'END' ;
WHILE: 'WHILE' ;
UNTIL: 'UNTIL' ;
BEGIN: 'BEGIN' ;

IDENTIFIER: [a-zA-Z_] [a-zA-Z0-9_]* ;
NUMBER: '0' | ('+'|'-')? ([1-9] [0-9]*) ;

STRING: '"' ~('"')* '"' ;
NEWLINE: ('\r'? '\n')+ ;
TABS: [ \t] -> skip ;