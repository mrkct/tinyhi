from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

from .TinyHiVisitor import TinyHiVisitor
from .TinyHiLexer import TinyHiLexer
from .TinyHiParser import TinyHiParser


class ASTNode():
    """Represents the generic node of the Abstract Syntax Tree. 

    This node contains its value in the `root` property and an ordered 
    list of its children in the `children` property.
    """
    
    def __init__(self, root, children=[]):
        self.root = root 
        self.children = list(children) if children else []
    
    def __repr__(self):
        if not self.children:
            return repr(self.root)
        
        children_repr = ', '.join([repr(child) for child in self.children])
        return f'({self.root}, [{children_repr}])'
    
    def __str__(self):
        return repr(self)
    
    def __eq__(self, other):
        if type(other) != ASTNode:
            return False
        return self.root == other.root and self.children == other.children

def _childrenToList(ctx):
    """Extracts all of an ANTLR Context children into a list"""
    return [ctx.getChild(i) for i in range(0, ctx.getChildCount())]

# TODO: Add info (e.g. line numbers) for printing error messages
class ASTBuilderVisitor(TinyHiVisitor):  
    def visitProgram(self, ctx):
        # TODO: Handle the case of an empty program
        # TODO: Handle better the case of many unnamed blocks
        # FIXME: The spec says to run the first UNNAMED block, not the first
        return ASTNode(self.visit(ctx.block()[0]))
    
    def visitBlock(self, ctx):
        children = _childrenToList(ctx)
        # If it's a named block
        if len(children) == 6:
            _, identifier, params, _, statements, _ = children
            return ASTNode({
                "type": "function", 
                "name": identifier.getText(), 
                "params": self.visit(params)
            }, self.visit(statements))
        
        # Or an unnamed block
        _, _, statements, _ = children
        return ASTNode({
            "type": "block"
        }, self.visit(statements))
    
    def visitFormalparams(self, ctx):
        # We return a list of string directly
        # Feels a bit overkill to have ASTNodes here too
        children = _childrenToList(ctx)
        _, *params_and_commas, _ = children
        params = params_and_commas[::2]
        return [p.getText() for p in params]



def parse(source, rule="program"):
    """Generates the AST from a string containing the source code.
    Args:
        source: A string containing the source code of the program to parse
        rule: The name of the rule from which to start building the AST, defaults to 'program'
    Returns:
        An ``ASTNode`` representing the whole AST on success, ``None`` if an error occurred
    """
    lexer = TinyHiLexer(InputStream(source))
    stream = CommonTokenStream(lexer)
    parser = TinyHiParser(stream)
    if not hasattr(parser, rule):
        raise ValueError(f'There is no rule "{rule}" in the grammar')
    parse_tree = getattr(parser, rule)()
    return ASTBuilderVisitor().visit(parse_tree)