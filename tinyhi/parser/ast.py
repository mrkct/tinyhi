from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from antlr4.tree.Tree import TerminalNodeImpl
from antlr4.error.ErrorListener import ErrorListener

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
    """Extracts all of an ANTLR Context children into a list, 
    removing all the None in the list"""
    # FIXME: Rename in something better
    return [ctx.getChild(i) for i in range(0, ctx.getChildCount())]

def remove_whitespace(children):
    """Takes a list of ANTLR Context and TerminalNodeImpl and removes 
    those tokens that represent whitespace"""
    result = []
    for child in children:
        if type(child) == TerminalNodeImpl:
            name = TinyHiLexer.ruleNames[child.getSymbol().type - 1]
            if name in ["WS", "NEWLINE"]:
                continue
        result.append(child)
    return result


# TODO: Add info (e.g. line numbers) for printing error messages
class ASTBuilderVisitor(TinyHiVisitor):  
    def visitProgram(self, ctx):
        # TODO: Handle the case of an empty program
        # TODO: Handle better the case of many unnamed blocks
        # FIXME: The spec says to run the first UNNAMED block, not the first
        blocks = remove_whitespace(_childrenToList(ctx))
        if len(blocks) == 0: return None
        
        blocks = [self.visit(b) for b in blocks]

        def find_first_unnamed_block():
            """Returns the index and value of the first unnamed block"""
            for i, block in enumerate(blocks):
                # If it's an unnamed block
                if block.root["type"] == "block":
                    return i, block
            return -1, None
        
        index, first_block = find_first_unnamed_block()    
        return ASTNode({
            "type": "start", 
            "start": first_block if index != -1 else None
        }, blocks[:index] + blocks[index+1:])
    
    def visitBlock(self, ctx):
        children = remove_whitespace(_childrenToList(ctx))
        # If it's a named block
        if len(children) == 5:
            _, identifier, params, statements, _ = children
            return ASTNode({
                "type": "function", 
                "name": self.visit(identifier), 
                "params": self.visit(params)
            }, self.visit(statements))
        
        # Or an unnamed block
        _, statements, _ = children
        return ASTNode({
            "type": "block"
        }, self.visit(statements))
    
    def visitFormalparams(self, ctx):
        # We return a list of string directly
        # Feels a bit overkill to have ASTNodes here too
        children = _childrenToList(ctx)
        _, *params_and_commas, _ = children
        params = params_and_commas[::2]
        return [self.visit(p) for p in params]
    
    def visitStatements(self, ctx):
        # A statement is a stat with a NEWLINE at the end
        # We remove the NEWLINE and return a list of statements
        children = remove_whitespace(_childrenToList(ctx))
        return [self.visit(stat) for stat in children]
    
    def visitAssignStat(self, ctx):
        identifier, _, *expr = _childrenToList(ctx)
        # An assignment can also have no right side ('A <-' is valid)
        var_name = self.visit(identifier)
        if expr:
            return ASTNode({
                "type": "assignment", 
                "variable": var_name
            }, [self.visit(expr[0])])
        else:
            return ASTNode({
                "type": "assignment", 
                "variable": var_name
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
        # This is separate because since the operator is whitespace it gets filtered
        left, _, right = _childrenToList(ctx)
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
    
    def visitIndexExpr(self, ctx):
        left, _, expr, _ = _childrenToList(ctx)
        return ASTNode({
            "type": "arrayIndexing"
        }, [self.visit(left), self.visit(expr)])
    
    def visitNumber(self, ctx):
        return ASTNode({
            "type": "number", 
            "value": int(ctx.NUMBER().getText())
        })
    
    def visitVarExpr(self, ctx):
        return ASTNode({
            "type": "variable", 
            "value": self.visit(ctx.identifier())
        })
    
    def visitIdentifier(self, ctx):
        return ctx.IDENTIFIER().getText()
    
    def visitString(self, ctx):
        return ASTNode({
            "type": "string", 
            "value": ctx.STRING().getText()[1:-1]
        })
    
    def visitParenExpr(self, ctx):
        children = remove_whitespace(_childrenToList(ctx))
        _, expr, _ = children
        return self.visit(expr)
