from tinyhi.parser import ASTNode


def binop(left, op, right):
    """Utility for building ASTNodes expressions quickly"""
    if type(left) == int:
        left = ASTNode({
            "type": "number", 
            "value": left
        })
    if type(right) == int:
        right = ASTNode({
            "type": "number", 
            "value": right
        })
    return ASTNode({
        "type": "binaryExpr", 
        "op": op
    }, [left, right])

def unaryop(op, expr):
    """Utility for building ASTNodes expressions quickly"""
    if type(expr) == int:
        expr = ASTNode({
            "type": "number", 
            "value": expr
        })
    return ASTNode({
        "type": "unaryExpr", 
        "op": op
    }, [expr])