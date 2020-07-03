from antlr4.error.ErrorListener import ErrorListener


class ParseError(Exception):
    """A generic error that occurred while parsing a program"""
    pass

class ParseErrorThrowListener(ErrorListener):
    """An ANTLR ErrorListener that, on any syntax error, throws a ParseError 
    error"""
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        message = f"line {line}:{column}: {msg}"
        raise ParseError(message)
