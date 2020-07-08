from .astnode import ASTNode
from .errors import ParseError
from .TinyHiVisitor import TinyHiVisitor
from .TinyHiLexer import TinyHiLexer
from .TinyHiParser import TinyHiParser
from antlr4.tree.Tree import TerminalNodeImpl


def get_context_children(ctx):
    """Extracts all of an ANTLR Context children into a list
    Params:
        ctx: An ANTLR SomethingContext object
    Returns:
        A list of all children of the context object
    """
    return [ctx.getChild(i) for i in range(0, ctx.getChildCount())]

def get_lexer_rule(token):
    """Returns the name of the lexer rule that generated the token
    Args:
        token: A `TerminalNodeImpl` object, which represents a token
    Returns:
        A string with the name of the lexer rule that generated the token
    """
    return TinyHiLexer.ruleNames[token.getSymbol().type - 1]


def remove_whitespace(children):
    """Takes a list of ANTLR Context and TerminalNodeImpl and removes 
    those tokens that represent whitespace"""
    result = []
    for child in children:
        if isinstance(child, TerminalNodeImpl):
            if get_lexer_rule(child) in ["WS", "NEWLINE"]:
                continue
        result.append(child)
    return result


class ASTBuilderVisitor(TinyHiVisitor):  
    def visitProgram(self, ctx):
        blocks = remove_whitespace(get_context_children(ctx))
        if len(blocks) == 0: return None
        
        main_block = self.visit(blocks[0])
        if main_block.root['params']:
            raise ParseError(
                'The outermost function cannot have parameters'
            )
        return main_block
    
    def visitBlock(self, ctx):
        children = remove_whitespace(get_context_children(ctx))
        # If it has params
        if len(children) == 6:
            _, identifier, params, blocks, statements, _ = children
            params = self.visit(params)
        else:
            # Or if it has none
            _, identifier, blocks, statements, _ = children
            params = []
        
        function_name = self.visit(identifier)
        if function_name in params:
            raise ParseError(
                f'The name of the function ({function_name}) cannot be '\
                'the same as one of the parameters'
            )

        instructions = self.visit(blocks) + self.visit(statements)
        return ASTNode({
            "type": "function", 
            "name": function_name, 
            "params": params
        }, instructions)
    
    def visitBlocks(self, ctx):
        """This rule contains a list of 'block', handling the possible 
        whitespace between each other"""
        blocks = remove_whitespace(get_context_children(ctx))
        return [self.visit(b) for b in blocks]
    
    def visitFormalparams(self, ctx):
        """This rule handles the parameters in a function declaration"""
        # We return a list of string directly
        # Feels a bit overkill to have ASTNodes here too
        children = remove_whitespace(get_context_children(ctx))
        _, *params_and_commas, _ = children
        params = params_and_commas[::2]
        return [self.visit(p) for p in params]
    
    def visitStatements(self, ctx):
        """This rule contains a list of 'statements', handling the possible 
        whitespace between each other"""
        children = remove_whitespace(get_context_children(ctx))
        return [self.visit(stat) for stat in children]

    def visitStatement(self, ctx):
        """A statement is just a generic 'stat' that handles possible 
        whitespace before or after the 'stat'"""
        # This looks useless but is actually necessary
        # If there is whitespace at the end of a statement ANTLR's default 
        # implementation returns the result of the last children of the context
        # (which would be whitespace in that case)
        child = remove_whitespace(get_context_children(ctx))[0]
        return self.visit(child)
    
    def visitAssignStat(self, ctx):
        identifier, _, *expr = remove_whitespace(get_context_children(ctx))
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
        children = remove_whitespace(get_context_children(ctx))
        _, left, bool_op, right, true_stats, *rest = children
        cond = ASTNode({
            "type": "binaryExpr", 
            "op": bool_op.getText()
        }, [self.visit(left), self.visit(right)])
        # If it doesn't have an ELSE
        if len(children) == 6:
            return ASTNode({
                "type": "if", 
                "cond": cond, 
                "onTrue": self.visit(true_stats), 
                "onFalse": []
            })
        else:
            _, else_stats, _ = rest
            return ASTNode({
                "type": "if", 
                "cond": cond, 
                "onTrue": self.visit(true_stats), 
                "onFalse": self.visit(else_stats)
            })
    
    def visitWhilestat(self, ctx):
        children = remove_whitespace(get_context_children(ctx))
        _, left, bool_op, right, stats, _ = children
        cond = ASTNode({
            "type": "binaryExpr", 
            "op": bool_op.getText()
        }, [self.visit(left), self.visit(right)])
        return ASTNode({
            "type": "while", 
            "cond": cond, 
            "onTrue": self.visit(stats)
        })
    
    def visitUntilstat(self, ctx):
        children = remove_whitespace(get_context_children(ctx))
        _, left, bool_op, right, stats, _ = children
        cond = ASTNode({
            "type": "binaryExpr", 
            "op": bool_op.getText()
        }, [self.visit(left), self.visit(right)])
        return ASTNode({
            "type": "until", 
            "cond": cond, 
            "onFalse": self.visit(stats)
        })


    """
    DO NOT EXTRACT A FUNCTION FOR THESE OPERATIONS:
    Python does no tail call optimizations, therefore extracting a function 
    and making so that all operations call the same function means that the 
    call stack is doubled. 
    Try parsing an expression with a lot of operands (try 800) and the parsing 
    fails because we reach the recursion limit. Duplicating the code without
    having a function call makes the stack a little lower.
    """

    def visitNegateVectorExpr(self, ctx):
        op, expr = remove_whitespace(get_context_children(ctx))
        return ASTNode({
            "type": "unaryExpr", 
            "op": op.getText()
        }, [self.visit(expr)])
    
    def visitNegatedExpr(self, ctx):
        op, expr = remove_whitespace(get_context_children(ctx))
        return ASTNode({
            "type": "unaryExpr", 
            "op": op.getText()
        }, [self.visit(expr)])

    def visitLengthExpr(self, ctx):
        op, expr = remove_whitespace(get_context_children(ctx))
        return ASTNode({
            "type": "unaryExpr", 
            "op": op.getText()
        }, [self.visit(expr)])

    def visitConcatExpr(self, ctx):
        # This is separate because since the operator is whitespace it gets filtered
        left, _, right = get_context_children(ctx)
        return ASTNode({
            "type": "binaryExpr", 
            "op": " "
        }, [self.visit(left), self.visit(right)])
    
    def visitMulDivExpr(self, ctx):
        left, op, right = remove_whitespace(get_context_children(ctx))
        return ASTNode({
            "type": "binaryExpr", 
            "op": op.getText()
        }, [self.visit(left), self.visit(right)])

    def visitAddSubExpr(self, ctx):
        left, op, right = remove_whitespace(get_context_children(ctx))
        return ASTNode({
            "type": "binaryExpr", 
            "op": op.getText()
        }, [self.visit(left), self.visit(right)])

    def visitFunctioncall(self, ctx):
        func_identifier, actual_params = remove_whitespace(get_context_children(ctx))
        return ASTNode({
            "type": "functionCall", 
            "functionName": func_identifier.getText()
        }, self.visit(actual_params))
    
    def visitPrintStat(self, ctx):
        return ASTNode({
            'type': 'print'
        }, [self.visitChildren(ctx)])

    def visitActualparams(self, ctx):
        # This is a list of expr with commas in between enclosed in parenthesis
        _, *params_and_commas, _ = remove_whitespace(get_context_children(ctx))
        return [self.visit(child) for child in params_and_commas[::2]]
    
    def visitIndexExpr(self, ctx):
        left, _, expr, _ = remove_whitespace(get_context_children(ctx))
        return ASTNode({
            "type": "arrayIndexing"
        }, [self.visit(left), self.visit(expr)])
    
    def visitExpression(self, ctx):
        # This looks useless but it's actually necessary
        # The default implementation of ParseTreeVisitor delegates this to 
        # visitChildren, which then uses aggregateResult, which by default
        # returns the last child of all, which in our case is whitespace
        expr = remove_whitespace(get_context_children(ctx))[0]
        return self.visit(expr)

    def visitAtom(self, ctx):
        node = ctx.getChild(0)
        if isinstance(node, TerminalNodeImpl):
            token_rule = get_lexer_rule(node)
            if token_rule == 'NUMBER':
                return ASTNode({
                    "type": "number", 
                    "value": int(ctx.getText())
                })
            elif token_rule == 'STRING':
                return ASTNode({
                    "type": "string", 
                    "value": ctx.getText()[1:-1]
                })
        # Otherwise it's an identifier which we need to visit to remove 
        # the whitespace
        return self.visit(node)
    
    def visitVariable(self, ctx):
        return ASTNode({
            "type": "variable", 
            "name": ctx.getText()
        })
    
    def visitIdentifier(self, ctx):
        return ctx.IDENTIFIER().getText()
    
    def visitParenthesizedExpr(self, ctx):
        children = remove_whitespace(get_context_children(ctx))
        _, expr, _ = children
        return self.visit(expr)
