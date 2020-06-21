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
    # FIXME: Rename in something better
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
    
    def visitStatements(self, ctx):
        # A statement is a stat with a NEWLINE at the end
        # We remove the NEWLINE and return a list of statements
        children = _childrenToList(ctx)
        return [self.visit(stat) for stat in children[::2]]
    
    def visitAssignStat(self, ctx):
        identifier, _, *expr = _childrenToList(ctx)
        # An assignment can also have no right side ('A <-' is valid)
        if expr:
            return ASTNode({
                "type": "assignment", 
                "variable": identifier.getText()
            }, [self.visit(expr[0])])
        else:
            return ASTNode({
                "type": "assignment", 
                "variable": identifier.getText()
            })
    
    def visitIfstat(self, ctx):
        children = _childrenToList(ctx)
        _, left, bool_op, right, _, _, true_stats, *rest = children
        cond = ASTNode({
            "type": "binaryExpr", 
            "op": bool_op.getText()
        }, [self.visit(left), self.visit(right)])
        # If it doesn't have an ELSE
        if len(children) == 8:
            return ASTNode({
                "type": "if", 
                "cond": cond, 
                "onTrue": self.visit(true_stats), 
                "onFalse": []
            })
        else:
            _, _, else_stats, _ = rest
            return ASTNode({
                "type": "if", 
                "cond": cond, 
                "onTrue": self.visit(true_stats), 
                "onFalse": self.visit(else_stats)
            })


    def visitUnaryExpr(self, ctx):
        # This is not a rule, just a helper for unary expressions
        op, expr = _childrenToList(ctx)
        return ASTNode({
            "type": "unaryExpr", 
            "op": op.getText()
        }, [self.visit(expr)])

    def visitNegExpr(self, ctx):
        return self.visitUnaryExpr(ctx)

    def visitLenExpr(self, ctx):
        return self.visitUnaryExpr(ctx)

    def visitConcatExpr(self, ctx):
        left, right = _childrenToList(ctx)
        # FIXME: A blank space as an operator is really ugly
        return ASTNode({
            "type": "binaryExpr", 
            "op": " "
        }, [self.visit(left), self.visit(right)])

    def visitBinaryExpr(self, ctx):
        # This is not a rule, just a helper for binary expressions
        left, op, right = _childrenToList(ctx)
        return ASTNode({
            "type": "binaryExpr", 
            "op": op.getText()
        }, [self.visit(left), self.visit(right)])
    
    def visitMulDivExpr(self, ctx):
        return self.visitBinaryExpr(ctx)

    def visitAddSubExpr(self, ctx):
        return self.visitBinaryExpr(ctx)

    def visitFunctioncall(self, ctx):
        function_name, actual_params = _childrenToList(ctx)
        return ASTNode({
            "type": "functionCall", 
            "functionName": function_name.getText()
        }, self.visit(actual_params))
    
    def visitActualparams(self, ctx):
        # This is a list of expr with commas in between enclosed in parenthesis
        _, *params_and_commas, _ = _childrenToList(ctx)
        return [self.visit(child) for child in params_and_commas[::2]]
    
    def visitArrayindexing(self, ctx):
        left, _, expr, _ = _childrenToList(ctx)
        return ASTNode({
            "type": "arrayIndexing"
        }, [self.visit(left), self.visit(expr)])
    
    def visitNumExpr(self, ctx):
        return ASTNode({
            "type": "number", 
            "value": int(ctx.getText())
        })
    
    def visitIdExpr(self, ctx):
        return ASTNode({
            "type": "variable", 
            "value": ctx.getText()
        })
    
    def visitStrExpr(self, ctx):
        return ASTNode({
            "type": "string", 
            "value": ctx.getText()[1:-1]
        })
    
    def visitParenExpr(self, ctx):
        _, expr, _ = _childrenToList(ctx)
        return self.visit(expr)
    

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