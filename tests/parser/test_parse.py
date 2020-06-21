from tinyhi.parser.ast import ASTBuilderVisitor
from tinyhi.parser import ASTNode, parse


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
    if type(expr) == int:
        expr = ASTNode({
            "type": "number", 
            "value": expr
        })
    return ASTNode({
        "type": "unaryExpr", 
        "op": op
    }, [expr])

def test_named_function_args():
    source = r"""BEGIN main(arg1, arg2, arg3)
    END"""
    result = parse(source, rule='block')
    assert result == ASTNode({
        "type": "function", 
        "name": "main",
        "params": ["arg1", "arg2", "arg3"] 
    }, [])

def test_named_function_noargs():
    source = r"""BEGIN My_Cool_Function2()
    END"""
    result = parse(source, rule='block')
    assert result == ASTNode({
        "type": "function", 
        "name": "My_Cool_Function2",
        "params": [] 
    }, [])

def test_unnamed_block():
    source = r"""BEGIN 
    END"""
    result = parse(source, rule='block')
    assert result == ASTNode({
        "type": "block"
    })

def test_empty_assignment():
    source = "A <-"
    result = parse(source, rule="stat")
    assert result == ASTNode({
        "type": "assignment", 
        "variable": "A"
    })

def test_simple_assignment():
    source = "A <- 1"
    result = parse(source, rule="stat")
    assert result == ASTNode({
        "type": "assignment", 
        "variable": "A"
    }, [ASTNode({"type": "number", "value": 1})])
    
    source = 'result <- "hello"\n'
    result = parse(source, rule="stat")
    assert result == ASTNode({
        "type": "assignment", 
        "variable": "result"
    }, [ASTNode({"type": "string", "value": "hello"})])
    
def test_complex_assignment():
    source = "A <- 1 + 2 * 3"
    result = parse(source, rule="stat")
    assert result == ASTNode({
        "type": "assignment", 
        "variable": "A"
    }, [binop(1, "+", binop(2, "*", 3))])

def test_basic_expr():
    source = "1"
    result = parse(source, rule="expr")
    assert result == ASTNode({
        "type": "number", 
        "value": 1
    })
    for operator in ['+', '-', '*', '/', ' ']:
        source = f"1 {operator} 2"
        result = parse(source, rule="expr")
        expected = ASTNode(
            {"type": "binaryExpr", "op": operator}, 
            [ASTNode({"type": "number", "value": 1}), ASTNode({"type": "number", "value": 2})]
        )
        assert result == expected
    
def test_complex_expr():
    source = "#~5 * (1 2 + 3 (1 + 6 / 3))"
    result = parse(source, rule="expr")
    right_vec = binop(3, " ", binop(1, "+", binop(6, "/", 3)))
    left_vec = binop(1, " ", 2)
    before_neg = binop(5, "*", binop(left_vec, "+", right_vec))
    expected = unaryop('#', unaryop('~', before_neg))
    assert result == expected