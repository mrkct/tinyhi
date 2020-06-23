from tinyhi.threader import thread_ast
from tests.parser import binop, ASTNode


def thread2iter(thread, start=0):
    """Utility to follow a thread. Will stop at the first non-linear path
    or at the end"""
    curr = start
    while curr in thread:
        if 'next' not in thread[curr].root:
            yield thread[curr]
            return
        yield thread[curr]
        curr = thread[curr].root['next']
    
def test_expr():
    ast = binop(1, "+", binop(7, "*", 3))
    thread = thread_ast(ast)
    thread_iter = thread2iter(thread)
    x = next(thread_iter)
    assert x.root['type'] == 'start'
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 1
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 7
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 3
    x = next(thread_iter)
    assert x.root['type'] == 'binaryExpr' and x.root['op'] == '*'
    x = next(thread_iter)
    assert x.root['type'] == 'binaryExpr' and x.root['op'] == '+'

def test_ifelse():
    ast = ASTNode({
        'type': 'if', 
        'cond': binop(1, '<', 2), 
        'onTrue': [ASTNode({'type': 'number', 'value': 1})], 
        'onFalse': [ASTNode({'type': 'number', 'value': 0})]
    })
    thread = thread_ast(ast)
    thread_iter = thread2iter(thread)
    x = next(thread_iter)
    assert x.root['type'] == 'start'
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 1
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 2
    x = next(thread_iter)
    assert x.root['type'] == 'binaryExpr' and x.root['op'] == '<'
    if_node = next(thread_iter)
    assert if_node.root['type'] == 'if'
    next_true = thread[if_node.root['nextTrue']]
    assert next_true.root['type'] == 'number' and next_true.root['value'] == 1
    next_false = thread[if_node.root['nextFalse']]
    assert next_false.root['type'] == 'number' and next_false.root['value'] == 0
    join_node_true = thread[next_true.root['next']]
    join_node_false = thread[next_false.root['next']]
    assert join_node_false == join_node_true
    assert join_node_true.root['type'] == 'skip'

def test_while():
    ast = ASTNode({
        'type': 'while', 
        'cond': binop(3, '>', 5), 
        'onTrue': [ASTNode({'type': 'number', 'value': 1})]
    })
    thread = thread_ast(ast)
    thread_iter = thread2iter(thread)
    x = next(thread_iter)
    assert x.root['type'] == 'start'
    cond_start = next(thread_iter)
    assert cond_start.root['type'] == 'number' and cond_start.root['value'] == 3
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 5
    x = next(thread_iter)
    assert x.root['type'] == 'binaryExpr' and x.root['op'] == '>'
    x = next(thread_iter)
    assert x.root['type'] == 'while'

    # Check that false leads to a skip node
    false_node = thread[x.root['nextFalse']]
    assert false_node.root['type'] == 'skip'

    # Check that true leads to a number and then a skip back node
    true_node = thread[x.root['nextTrue']]
    assert true_node.root['type'] == 'number' and true_node.root['value'] == 1
    jump_back = thread[true_node.root['next']]
    assert jump_back.root['type'] == 'skip'
    assert jump_back.root['next'] == cond_start.root['id']