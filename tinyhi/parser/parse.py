from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from .ast import ASTBuilderVisitor
from .errors import ParseErrorThrowListener, ParseError
from .TinyHiVisitor import TinyHiVisitor
from .TinyHiLexer import TinyHiLexer
from .TinyHiParser import TinyHiParser
import sys


def parse(source, rule="program", throw_errors=False):
    """Generates the AST from a string containing the source code.
    Args:
        source: A string containing the source code of the program to parse
        rule: The name of the rule from which to start building the AST, defaults to ``program``
        throw_errors: If True this will throw ParseError on a parsing error, defaults to ``False``
    Returns:
        An ``ASTNode`` representing the whole AST on success, ``None`` if an error occurred
    """
    def _parse():
        lexer = TinyHiLexer(InputStream(source))
        lexer.removeErrorListeners()
        lexer.addErrorListener(ParseErrorThrowListener())

        stream = CommonTokenStream(lexer)
        parser = TinyHiParser(stream)

        parser.removeErrorListeners()
        parser.addErrorListener(ParseErrorThrowListener())

        if not hasattr(parser, rule):
            raise ValueError(f'There is no rule "{rule}" in the grammar')
        parse_tree = getattr(parser, rule)()
        return ASTBuilderVisitor().visit(parse_tree)
    
    if throw_errors:
        return _parse()
    
    try:
        return _parse()
    except ParseError as e:
        print(e, file=sys.stderr)