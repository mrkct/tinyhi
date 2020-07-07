import pytest
from tinyhi.parser import ASTNode, ParseError, check_ast_coherence


def test_fail_doublefunction():
    # Should fail because there are 2 functions with the same name
    func = ASTNode({
        'type': 'function', 
        'name': 'f', 
        'params': []
    })
    main = ASTNode({
        'type': 'function', 
        'name': 'main', 
        'params': []
    }, [func, func])
    with pytest.raises(ParseError):
        check_ast_coherence(main)

def test_fail_wrongparams():
    func = ASTNode({
        'type': 'function', 
        'name': 'f', 
        'params': ['x1', 'x2']
    })
    func_call = ASTNode({
        'type': 'functionCall', 
        'functionName': 'f'
    }, [1, 2, 3])
    main = ASTNode({
        'type': 'function', 
        'name': 'main', 
        'params': []
    }, [func, func_call])
    with pytest.raises(ParseError):
        check_ast_coherence(main)