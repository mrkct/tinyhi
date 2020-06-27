from .symboltable import SymbolTable
from .errors import ExecutionError
from .undefined import Undefined
from tinyhi.parser import parse
from tinyhi.threader import thread_ast


def strtype(x):
    """Returns a string representation of the type of the value
    """
    if type(x) == int:
        return 'INTEGER'
    elif type(x) == str:
        return 'STRING'
    elif type(x) == list:
        return 'LIST'
    elif x == Undefined:
        return 'UNDEFINED'
    else:
        return f'<INVALID: {x.__class__.__name__}>'

def run_from_thread(thread, functions, start, print_dbg=False):
    IP = functions[start]
    st_stack = []       # SymbolTable stack
    ret_stack = [-1]    # Contains the return IP address for functions
    stack = []          # Contains the actual values for the computations

    globals_table = SymbolTable()

    def handle_skip(node):
        return node.root['next']
    
    def handle_function(node):
        # This is called when we enter a function call
        # We are in a function therefore we don't care about the scope 
        # of who called us
        table = SymbolTable()
        # FIXME: Disallow using the function name as a param
        for param in reversed(node.root['params']):
            table.put(param, stack.pop(), immutable=True)
        # We also need to put the function name, even without a value 
        # because if we were to set it first in a block scope it would 
        # end up in a SymbolTable that would be thrown away at the end 
        # of that scope
        table.put(node.root['name'], Undefined)
        st_stack.append(table)
        
        return node.root['next']

    def handle_functionCall(node):
        # Care, we need to save the IP just after this node or we would run 
        # this node again after we return from a function
        ret_stack.append(node.root["next"])
        return functions[node.root["functionName"]]
    
    def handle_return(node):
        # We throw away the symbol table for the function
        # but we also need to check if a return value was set. 
        st = st_stack.pop()
        func_name = node.root["functionName"]
        x = st.get(func_name)
        # We append even if its None. If it's a useless value it will 
        # be thrown away in the print node
        stack.append(x if x != None else Undefined)
        return ret_stack.pop()

    def handle_const(node):
        stack.append(node.root['value'])
        return node.root['next']

    def handle_variable(node):
        var_name = node.root['value']
        if var_name[0] == '.':
            value = globals_table.get(var_name)
        else:
            symbol_table = st_stack[-1]
            value = symbol_table.get(var_name)
        if value == None:
            raise ExecutionError(f'Name "{var_name}" is not defined')
        stack.append(value)
        return node.root['next']
    
    def handle_binaryExpr(node):
        # TODO: Allow mixing strings and ints in vectors
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
                return left - right
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
        table = st_stack[-1]
        # If it's a global variable we use another table
        var_name = node.root['variable']
        if var_name[0] == '.':
            table = globals_table
        # If it is an assignment to clear the variable
        if len(node.children) == 0:
            table.put(var_name, Undefined)
        else:
            table.put(var_name, stack.pop())
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

    def handle_array_indexing(node):
        index = stack.pop()
        array = stack.pop()
        if type(array) not in [list, str]:
            raise ExecutionError(
                f'Type mismatch: cannot index {strtype(array)}'
            )
        if type(index) != list: index = [index]
        # TODO: This supports str arrays too, but currently we don't allow them
        values = []
        for i in index:
            if type(i) != int:
                raise ExecutionError(
                    f'Type mismatch: cannot use {strtype(i)} as an index'
                )
            if i < 1 or i > len(array):
                raise ExecutionError(
                    f'Index out of bounds: {i} is not in [1, {len(array)}]'
                )
            values.append(array[i - 1])
        # Here we merge adjacents lists
        for i in range(len(values) - 1, 0, -1):
            if type(values[i]) == str and type(values[i-1]) == str:
                values[i-1] += values[i]
                del values[i]
        if len(values) == 1:
            stack.append(values[0])
        else:
            stack.append(values)
        return node.root['next']

    def handle_conditional_jump(node):
        cond = stack.pop()
        if type(cond) != bool:
            raise ExecutionError(f'IF: stack.pop returned a non-bool value ({cond})')
        return node.root["nextTrue"] if cond else node.root["nextFalse"]

    def handle_print(node):
        value = stack.pop()
        if value == Undefined: 
            return node.root["next"]
        if type(value) not in [int, str, list]:
            raise ExecutionError(
                f'PRINT: Invalid value on the stack {value} ({type(value)})'
            )
        print(value)
        return node.root["next"]

    def handle_enter_block_scope(node):
        st_stack.append(
            SymbolTable(parent=st_stack[-1])
        )
        return node.root["next"]
    
    def handle_exit_block_scope(node):
        st_stack.pop()
        return node.root["next"]

    NODE_FUNCTIONS = {
        'skip': handle_skip, 
        'function': handle_function, 
        'number': handle_const, 
        'string': handle_const, 
        'variable': handle_variable, 
        'binaryExpr': handle_binaryExpr, 
        'unaryExpr': handle_unaryExpr, 
        'arrayIndexing': handle_array_indexing, 
        'assignment': handle_assignment, 
        'functionCall': handle_functionCall,
        'return': handle_return, 
        'print': handle_print, 
        'if': handle_conditional_jump, 
        'while': handle_conditional_jump, 
        'until': handle_conditional_jump, 
        'enterBlockScope': handle_enter_block_scope, 
        'exitBlockScope': handle_exit_block_scope
    }

    while True:
        # End the program
        if IP == -1:
            return_value = stack.pop()
            if return_value == Undefined:
                return None
            else:
                return return_value
        node = thread[IP]
        if node.root['type'] in NODE_FUNCTIONS:
            IP = NODE_FUNCTIONS[node.root['type']](node)
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

    return run_from_thread(
        thread, 
        functions, 
        ast.root['name']
    )