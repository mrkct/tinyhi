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

def printexpr(what):
    """Utility to return an ASTNode with type 'print' for a value"""
    if type(what) == int:
        what = ASTNode({
            'type': 'number', 
            'value': what
        }) 
    elif type(what) == str:
        what = ASTNode({
            'type': 'string', 
            'value': what
        })
    return ASTNode({
        'type': 'print'
    }, [what])