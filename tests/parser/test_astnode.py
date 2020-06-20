from tinyhi.parser import ASTNode


def test_repr():
    assert repr(ASTNode(1)) == '1'
    add_node = ASTNode('+', [ASTNode(1), ASTNode(2)])
    assert repr(add_node) == "(+, [1, 2])"