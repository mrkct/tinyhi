from .symboltable import SymbolTable
from .errors import ExecutionError
from tinyhi.parser import parse
from tinyhi.threader import thread_ast


# TODO: Handle the case of an expr in a single line
# TODO: Handle the case of a void call in an expr
# TODO: Handle the case of clearing a variable

def strtype(x):
    """Returns a string representation of the type of the value
    """
    if type(x) == int:
        return 'INTEGER'
    elif type(x) == str:
        return 'STRING'
    elif type(x) == list:
        return 'LIST'
    else:
        return f'<INVALID: {x.__class__.__name__}>'

def run_from_thread(thread, functions, start):
    IP = functions[start]
    st_stack = [] # SymbolTable stack
    stack = []

    def handle_skip(node):
        return node.root['next']
    
    def handle_function(node):
        # We are in a function therefore we don't care about the scope 
        # of who called us
        st = SymbolTable()
        # TODO: Pop all params in reverse order and set the params 
        # in the symboltable to those values & immutable
        st_stack.append(st)
        return node.root['next']

    def handle_const(node):
        stack.append(node.root['value'])
        return node.root['next']
    

    def handle_variable(node):
        symbol_table = st_stack[-1]
        var_name = node.root['value']
        value = symbol_table.get(var_name)
        if value == None:
            raise ExecutionError('Name "{var_name}" is not defined')
        stack.append(value)
        return node.root['next']
    
    def handle_binaryExpr(node):
        def handle_sum(left, right):
            # Simple sum of integers
            if type(left) == int and type(right) == int:
                return left + right
            # Sum of list and a single int
            if type(left) == list and type(right) == int:
                left, right = right, left
            if type(left) == int and type(right) == list:
                return [left + x for x in right]
            if type(left) == list and type(right) == list:
                if len(left) != len(right):
                    raise ExecutionError(
                        f'Type mismatch: cannot sum lists with different lengths'
                    )
                return [left[i] + right[i] for i in range(0, len(left))]
            raise ExecutionError(
                f'Type mismatch: cannot sum {strtype(left)} and {strtype(right)}'
            )

        def handle_mul(left, right):
            # Simple mul of integers
            if type(left) == int and type(right) == int:
                return left * right
            # Sum of list and a single int
            if type(left) == list and type(right) == int:
                left, right = right, left
            if type(left) == int and type(right) == list:
                return [left * x for x in right]
            raise ExecutionError(
                f'Type mismatch: cannot multiply {strtype(left)} and {strtype(right)}'
            )

        def handle_sub(left, right):
            # Simple sub of integers
            if type(left) == int and type(right) == int:
                return left + right
            # Int - List is different than List - Int
            if type(left) == list and type(right) == int:
                return [x - right for x in left]
            if type(left) == int and type(right) == list:
                return [left - x for x in right]
            raise ExecutionError(
                f'Type mismatch: cannot subtract {strtype(left)} and {strtype(right)}'
            )

        def handle_div(left, right):
            try:
                # Simple divison of integers
                if type(left) == int and type(right) == int:
                    return left // right
                # Int - List is different than List - Int
                if type(left) == list and type(right) == int:
                    return [x // right for x in left]
                if type(left) == int and type(right) == list:
                    return [left // x for x in right]
                raise ExecutionError(
                    f'Type mismatch: cannot divide {strtype(left)} and {strtype(right)}'
                )
            except ZeroDivisionError:
                raise ExecutionError(
                    f'Division by zero: {left} / {right}'
                )

        def handle_blank(left, right):
            if type(left) == str and type(right) == str:
                return left + right
            if type(left) == str or type(right) == str:
                raise ExecutionError(
                    f'Type mismatch: vectors can only contain integers'
                )
            if type(left) != list:
                left = [left]
            if type(right) != list:
                right = [right]
            return left + right

        def handle_greater(left, right):
            if type(left) == int and type(right) == int:
                return left > right
            raise ExecutionError(
                f'Type mismatch: cannot compare {strtype(left)} and {strtype(right)}'
            )
        
        def handle_less(left, right):
            if type(left) == int and type(right) == int:
                return left < right
            raise ExecutionError(
                f'Type mismatch: cannot compare {strtype(left)} and {strtype(right)}'
            )
        
        def handle_equal(left, right):
            if type(left) == type(right):
                return left == right
            raise ExecutionError(
                f'Type mismatch: cannot compare {strtype(left)} and {strtype(right)}'
            )
        
        def handle_notEqual(left, right):
            if type(left) == type(right):
                return left != right
            raise ExecutionError(
                f'Type mismatch: cannot compare {strtype(left)} and {strtype(right)}'
            )
        
        def handle_greaterEqual(left, right):
            return not handle_less(left, right)
        
        def handle_lessEqual(left, right):
            return not handle_greater(left, right)
        

        OPERATIONS = {
            '+': handle_sum, 
            '-': handle_sub, 
            '*': handle_mul, 
            '/': handle_div, 
            ' ': handle_blank, 
            '>': handle_greater,
            '<': handle_less,
            '>=': handle_greaterEqual,
            '<=': handle_lessEqual,
            '=': handle_equal,
            '<>': handle_notEqual
        }
        right, left = stack.pop(), stack.pop()
        op = node.root['op']
        stack.append(OPERATIONS[op](left, right))
        return node.root['next']

    def handle_assignment(node):
        # If it is an assignment to clear the variable
        if len(node.children) == 0:
            # TODO: Clear the value in the symbol table
            pass
        else:
            v = stack.pop()
            st = st_stack[-1]
            st.put(node.root['variable'], v)
        return node.root['next']
    
    def handle_unaryExpr(node):
        def handle_len(expr):
            if type(expr) in [list, str]:
                return len(expr)
            raise ExecutionError(
                f'Type mismatch: cannot get length of {strtype(expr)}'
            )
        
        def handle_listNegation(expr):
            if type(expr) == list:
                return [-x for x in expr]
            raise ExecutionError(
                f'Type mismatch: cannot apply ~ to type {strtype(expr)}'
            )
        
        def handle_negation(expr):
            if type(expr) == int:
                return -expr
            raise ExecutionError(
                f'Type mismatch: cannot negate type {strtype(expr)}'
            )
        
        OPERATIONS = {
            '#': handle_len, 
            '~': handle_listNegation, 
            '-': handle_negation
        }
        expr = stack.pop()
        op = node.root['op']
        stack.append(OPERATIONS[op](expr))
        return node.root['next']


    NODE_FUNCTIONS = {
        'skip': handle_skip, 
        'function': handle_function, 
        'number': handle_const, 
        'string': handle_const, 
        'variable': handle_variable, 
        'binaryExpr': handle_binaryExpr, 
        'unaryExpr': handle_unaryExpr, 
        'assignment': handle_assignment
    }
    while True:
        node = thread[IP]
        if node.root['type'] in NODE_FUNCTIONS:
            IP = NODE_FUNCTIONS[node.root['type']](node)
        elif node.root['type'] == 'return':
            # Return is a special case because it might end the program
            if len(stack) == 0: 
                # There is no return address, the program is over
                st = st_stack[-1]
                return st.get(node.root['functionName'])
            # The return address was stored on the stack
            IP = stack.pop()
            # We throw away the symbol table for the function
            # but we also need to check if a return value was set. 
            # In that case push that value on the stack
            st = st_stack.pop()
            if x := st.get(node.root['functionName']):
                stack.append(x)
        else:
            raise ExecutionError(
                f'WARN: Unknown node type "{node.root["type"]}"'
            )

def run(source, throw_errors=False):
    """Executes a program from its source code

    Returns:
        The value returned by the outermost function or None if nothing 
        is returned
    Args:
        source (str): The source code of the program to run
        throw_errors: If set to True any error will be thrown as an exception 
        instead of printed
    Throws:
        ParseError, ThreadError, ExecutionError
    """
    ast = parse(source, throw_errors=True)
    thread, functions = thread_ast(ast)
    return run_from_thread(thread, functions, ast.root['name'])