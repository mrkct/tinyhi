from tinyhi.threader import thread_ast
from tests.parser import binop, unaryop, ASTNode 


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
    ast = unaryop('~', binop(1, "+", binop(7, "*", 3)))
    thread, _ = thread_ast(ast)
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
    x = next(thread_iter)
    assert x.root['type'] == 'unaryExpr' and x.root['op'] == '~'

def test_arrayindexing():
    ast = ASTNode({
        'type': 'arrayIndexing'
    }, [ASTNode({'type': 'variable', 'name': 'arr'}), 
        binop(3, ' ', 5)]
    )
    thread, _ = thread_ast(ast)
    thread_iter = thread2iter(thread)
    x = next(thread_iter)
    assert x.root['type'] == 'start'
    x = next(thread_iter)
    assert x.root['type'] == 'variable' and x.root['name'] == 'arr'
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 3
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 5
    x = next(thread_iter)
    assert x.root['type'] == 'binaryExpr' and x.root['op'] == ' '
    x = next(thread_iter)
    assert x.root['type'] == 'arrayIndexing'

def test_ifelse():
    ast = ASTNode({
        'type': 'if', 
        'cond': binop(1, '<', 2), 
        'onTrue': [ASTNode({'type': 'number', 'value': 1})], 
        'onFalse': [ASTNode({'type': 'number', 'value': 0})]
    })
    thread, _ = thread_ast(ast)
    thread_iter = thread2iter(thread)
    x = next(thread_iter)
    assert x.root['type'] == 'start'
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 1
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 2
    x = next(thread_iter)
    assert x.root['type'] == 'binaryExpr' and x.root['op'] == '<'
    enter_scope = next(thread_iter)
    assert enter_scope.root['type'] == 'enterBlockScope'
    if_node = next(thread_iter)
    assert if_node.root['type'] == 'if'
    # True block
    next_true = thread[if_node.root['nextTrue']]
    assert next_true.root['type'] == 'setInScopeFunctions'
    next_true = thread[next_true.root['next']]
    assert next_true.root['type'] == 'number' and next_true.root['value'] == 1
    # False block
    next_false = thread[if_node.root['nextFalse']]
    assert next_false.root['type'] == 'setInScopeFunctions'
    next_false = thread[next_false.root['next']]
    assert next_false.root['type'] == 'number' and next_false.root['value'] == 0
    exit_scope_true = thread[next_true.root['next']]
    exit_scope_false = thread[next_false.root['next']]
    assert exit_scope_false == exit_scope_true
    assert exit_scope_true.root['type'] == 'exitBlockScope'

def test_while():
    ast = ASTNode({
        'type': 'while', 
        'cond': binop(3, '>', 5), 
        'onTrue': [ASTNode({'type': 'number', 'value': 1})]
    })
    thread, _ = thread_ast(ast)
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
    assert x.root['type'] == 'enterBlockScope'
    x = next(thread_iter)
    assert x.root['type'] == 'while'

    # Check that false leads to an exitBlockScope
    false_node = thread[x.root['nextFalse']]
    assert false_node.root['type'] == 'exitBlockScope'

    # Check the true branch 
    true_node = thread[x.root['nextTrue']]
    assert true_node.root['type'] == 'setInScopeFunctions'
    true_node = thread[true_node.root['next']]
    assert true_node.root['type'] == 'number' and true_node.root['value'] == 1
    true_node = thread[true_node.root['next']]
    assert true_node.root['type'] == 'exitBlockScope'
    jump_back = thread[true_node.root['next']]
    assert jump_back.root['type'] == 'skip'
    assert jump_back.root['next'] == cond_start.root['id']

def test_until():
    ast = ASTNode({
        'type': 'until', 
        'cond': binop(3, '>', 5), 
        'onFalse': [ASTNode({'type': 'number', 'value': 1})]
    })
    thread, _ = thread_ast(ast)
    thread_iter = thread2iter(thread)
    x = next(thread_iter)
    assert x.root['type'] == 'start'
    block_start = next(thread_iter)
    assert block_start.root['type'] == 'enterBlockScope'
    x = next(thread_iter)
    assert x.root['type'] == 'setInScopeFunctions' and x.root['functions'] == []
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 1
    x = next(thread_iter)
    assert x.root['type'] == 'exitBlockScope'
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 3
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 5
    x = next(thread_iter)
    assert x.root['type'] == 'binaryExpr' and x.root['op'] == '>'
    until_node = next(thread_iter)
    assert until_node.root['type'] == 'until'

    # On false it should go back to the first node
    assert thread[until_node.root['nextFalse']] == block_start
    
    # On true it should go to a skip node and on
    assert thread[until_node.root['nextTrue']].root['type'] == 'skip'

def test_empty_assignment():
    ast = ASTNode({
        'type': 'assignment', 
        'variable': 'pippo'
    })
    thread, _ = thread_ast(ast)
    thread_iter = thread2iter(thread)
    x = next(thread_iter)
    assert x.root['type'] == 'start'
    x = next(thread_iter)
    assert x.root['type'] == 'assignment' and x.root['variable'] == 'pippo'

def test_assignment():
    ast = ASTNode({
        'type': 'assignment', 
        'variable': 'pippo'
    }, [binop(1, '+', 2)])
    thread, _ = thread_ast(ast)
    thread_iter = thread2iter(thread)
    x = next(thread_iter)
    assert x.root['type'] == 'start'
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 1
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 2
    x = next(thread_iter)
    assert x.root['type'] == 'binaryExpr' and x.root['op'] == '+'
    x = next(thread_iter)
    assert x.root['type'] == 'assignment' and x.root['variable'] == 'pippo'

def test_functiondecl():
    ast = ASTNode({
        'type': 'function', 
        'name': 'main', 
        'params': []
    }, [ASTNode({'type': 'number', 'value': 1})])
    thread, functions = thread_ast(ast)
    assert 'main' in functions
    thread_iter = thread2iter(thread, start=functions['main'])
    x = next(thread_iter)
    assert x.root['type'] == 'function' and x.root['name'] == 'main'
    x = next(thread_iter)
    assert x.root['type'] == 'setInScopeFunctions'
    assert x.root['functions'] == ['main']
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 1
    x = next(thread_iter)
    assert x.root['type'] == 'return'
    assert 'next' not in x.root
    
def test_nested_functiondecl():
    nested_func = ASTNode({
        'type': 'function', 
        'name': 'nested', 
        'params': []
    }, [ASTNode({'type': 'number', 'value': 0})])
    ast = ASTNode({
        'type': 'function', 
        'name': 'main', 
        'params': []
    }, [ASTNode({'type': 'number', 'value': 1}), 
        nested_func, 
        ASTNode({'type': 'number', 'value': 1})]
    )
    thread, functions = thread_ast(ast)
    assert 'main' in functions
    thread_iter = thread2iter(thread, start=functions['main'])
    # Check that the execution of 'main' goes through the nested function
    x = next(thread_iter)
    assert x.root['type'] == 'function' and x.root['name'] == 'main'
    x = next(thread_iter)
    assert x.root['type'] == 'setInScopeFunctions' 
    assert 'main' in x.root['functions']
    assert 'nested' in x.root['functions']
    assert len(x.root['functions']) == 2
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 1
    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 1
    x = next(thread_iter)
    assert x.root['type'] == 'return'
    assert 'next' not in x.root
    # Check the nested function
    assert 'nested' in functions
    thread_iter = thread2iter(thread, start=functions['nested'])
    x = next(thread_iter)
    assert x.root['type'] == 'function' and x.root['name'] == 'nested'
    x = next(thread_iter)
    assert x.root['type'] == 'setInScopeFunctions'
    assert 'main' in x.root['functions']
    assert 'nested' in x.root['functions']
    assert len(x.root['functions']) == 2

    x = next(thread_iter)
    assert x.root['type'] == 'number' and x.root['value'] == 0
    x = next(thread_iter)
    assert x.root['type'] == 'return'
    assert 'next' not in x.root
