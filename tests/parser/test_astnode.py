from tinyhi.parser import ASTNode

def test_init():

def test_repr():
    assert repr(ASTNode(1)) == '1'
    add_node = ASTNode('+', [ASTNode(1), ASTNode(2)])
    assert repr(add_node) == '(+, [1, 2])'
    complex_node = ASTNode('*', [ASTNode(3), add_node])
    assert repr(complex_node) == '(*, [3, (+, [1, 2])])'