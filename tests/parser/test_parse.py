from tinyhi.parser.ast import ASTBuilderVisitor
from tinyhi.parser import ASTNode, parse


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
    
