from tinyhi.threader import thread_ast
from tests.parser import binop, ASTNode


def thread2iter(thread, start=0):
    """Utility to follow a thread. Will stop at the first non-linear path
    or at the end"""
    curr = start
    while curr in thread:
        if 'next' not in thread[curr].root:
            print('FINE ITER: ', thread[curr])
            yield thread[curr]
            return
        print('ITER:', thread[curr])
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
    assert join_node_true.root['type'] == 'join'
