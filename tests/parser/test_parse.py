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