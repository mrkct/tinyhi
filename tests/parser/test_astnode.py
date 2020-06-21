from tinyhi.parser import ASTNode, parse


def test_repr():
    assert repr(ASTNode(1)) == '1'
    add_node = ASTNode('+', [ASTNode(1), ASTNode(2)])
    assert repr(add_node) == '(+, [1, 2])'
    complex_node = ASTNode('*', [ASTNode(3), add_node])
    assert repr(complex_node) == '(*, [3, (+, [1, 2])])'

def test_eq():
    a = ASTNode({'a': 1, 'b': 2})
    b = ASTNode({'a': 1, 'b': 2})
    assert a == b
    c = ASTNode({'a': 2, 'b': 5})
    assert a != c and b != c
    assert a != None and a != 'random string'
    complex_a = ASTNode({'type': 'A', 'value': 1}, [a, b, c])
    complex_b = ASTNode({'type': 'A', 'value': 1}, [a, b, c])
    complex_c = ASTNode({'type': 'A', 'value': 1}, [a, a, b])
    assert complex_a == complex_b
    assert complex_a != complex_c