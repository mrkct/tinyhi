grammar TinyHi;

program: (NEWLINE|WS)* block (NEWLINE|WS)* EOF;

statements: (statement NEWLINE (WS|NEWLINE)*)* ;

statement: WS? stat WS? ;

stat: identifier '<-' expression?       #assignStat
    | ifstat                            #ifStat
    | whilestat                         #whileStat
    | untilstat                         #untilStat
    | expression                        #printStat
    ;

blocks: (WS? block WS? NEWLINE (WS|NEWLINE)*)* ;
block: BEGIN WS identifier formalparams? WS? NEWLINE (WS|NEWLINE)* blocks statements END; 

ifstat: IF WS expression BOOLOP expression NEWLINE (WS|NEWLINE)* statements (ELSE WS? NEWLINE (WS|NEWLINE)* statements)? END; 
whilestat: WHILE WS expression BOOLOP expression NEWLINE (WS|NEWLINE)* statements END;
untilstat: UNTIL WS expression BOOLOP expression NEWLINE (WS|NEWLINE)* statements END;

expression: WS? expr WS? ;

expr: functioncall                      #callExpr
    | expr '[' expression ']'           #indexExpr
    | expr WS expr                      #concatExpr
    | LENGTH WS? expr                   #lengthExpr
    | NEGATE WS? expr                   #negateVectorExpr
    | expr WS? (MUL|DIVIDE) WS? expr    #mulDivExpr
    | expr WS? (PLUS|MINUS) WS? expr    #addSubExpr
    | '(' expression ')'                #parenthesizedExpr
    | MINUS expr                        #negatedExpr
    | atom                              #atomExpr
    ;

atom: NUMBER | STRING | variable ;

// This is so that we can distinguish between identifiers used for 
// functions and actual variable references
variable: IDENTIFIER ;

functioncall: IDENTIFIER actualparams ;
actualparams: '(' (expression (',' expression)*)? ')';
formalparams: '(' (identifier (',' identifier)*)? ')' ;

identifier: WS? IDENTIFIER WS? ;
number: WS? NUMBER WS? ;
string: WS? STRING WS? ;

COMMENT: ('//' ~[\n]) -> skip ;

PLUS: '+' ;
MINUS: '-' ;
MUL: '*' ;
DIVIDE: '/' ;
NEGATE: '~' ;
LENGTH: '#' ;

BOOLOP: '='|'<'|'>'|'<='|'>=' | '<>';

IF: 'IF';
ELSE: 'ELSE';
END: 'END';
WHILE: 'WHILE';
UNTIL: 'UNTIL';
BEGIN: 'BEGIN';

IDENTIFIER: [a-zA-Z_.] [a-zA-Z0-9_]* ;
NUMBER: '0' | ([1-9] [0-9]*) ;

STRING: '"' ~('"')* '"' ;
WS: ' '+ ;
NEWLINE: ('\r'? '\n')+ ;
TABS: [\t] -> skip ;