from .symboltable import SymbolTable
from .functiontable import FunctionTable
from .errors import ExecutionError, strtype
from .undefined import Undefined
from tinyhi.parser import parse
from tinyhi.threader import thread_ast
from .expressions import binary_expression, unary_expression, array_index


def run_from_thread(thread, functions, start):
    IP = functions[start]
    
    # The top of the stack contains a function table that represents the 
    # functions in scope. Since we don't run the first block declaration 
    # node we need to add that one manually
    functiontable_stack = []
    first_table = FunctionTable()
    first_table.declare(start, [])    
    functiontable_stack.append(first_table)

    # The top of this stack contains the symbol table that represents the 
    # current scope of the functions
    symboltable_stack = []
    return_stack = [-1]     # Contains the return IP for each function call
    stack = []              # Contains the actual values for the computations

    def handle_skip(node):
        """Handles those nodes that do nothing and are only used to join 
        branches in the thread"""
        return node.root['next']
    
    def handle_function(node):
        """Handles the node that represents when we enter a called function"""
        # In a function we don't care about the scope of who called us
        # But we do care about the scope of functions declared before
        symbol_table = SymbolTable()
        functions_table = FunctionTable(parent=functiontable_stack[-1])
        functiontable_stack.append(functions_table)

        for param in reversed(node.root['params']):
            symbol_table.put(param, stack.pop(), immutable=True)
        # We also need to put the function name, even without a value 
        # because if we were to set it first in a block scope it would 
        # end up in a SymbolTable that would be thrown away at the end 
        # of that scope
        symbol_table.put(node.root['name'], Undefined)
        symboltable_stack.append(symbol_table)
        
        return node.root['next']

    def handle_function_call(node):
        """Handles a function call node, checks if the scope is right and 
        manages how to return after the call ends"""
        # Care, we need to save the IP just after this node or we would run 
        # this node again after we return from a function
        function_name = node.root["functionName"]
        table = functiontable_stack[-1]
        if not table.isVisible(function_name):
            raise ExecutionError(
                f'Function "{function_name}" is not in scope'
            )
        return_stack.append(node.root["next"])
        return functions[function_name]
    
    def handle_return(node):
        """Handles the end of a function call, returning to the point before 
        the call and handling the return value of the function"""
        functiontable_stack.pop()
        # We throw away the symbol table for the function
        # but we also need to check if a return value was set. 
        st = symboltable_stack.pop()
        func_name = node.root["functionName"]
        x = st.get(func_name)
        # We append even if its None. If it's a useless value it will 
        # be thrown away in the print node
        # ATTENTION: DO NOT CHANGE THIS TO 'if x'. If the function returns a 0
        # then it would evaluate to false and return Undefined instead
        stack.append(x if x != None else Undefined)
        return return_stack.pop()

    def handle_const(node):
        """Pushes a generic constant to the stack. Used for ints and strings"""
        stack.append(node.root['value'])
        return node.root['next']

    def handle_variable(node):
        var_name = node.root['name']
        symbol_table = symboltable_stack[-1]
        value = symbol_table.get(var_name)
        if value == None:
            raise ExecutionError(f'Name "{var_name}" is not defined')
        stack.append(value)
        return node.root['next']
    
    def handle_binary_expr(node):
        right, left = stack.pop(), stack.pop()
        op = node.root['op']
        result = binary_expression(left, op, right)
        stack.append(result)
        return node.root['next']

    def handle_assignment(node):
        table = symboltable_stack[-1]
        var_name = node.root['variable']
        # If it is an assignment to clear the variable
        if len(node.children) == 0:
            table.put(var_name, Undefined)
        else:
            table.put(var_name, stack.pop())
        return node.root['next']
    
    def handle_unary_expr(node):
        value = stack.pop()
        op = node.root['op']
        result = unary_expression(op, value)
        stack.append(result)
        return node.root['next']

    def handle_array_indexing(node):
        index = stack.pop()
        array = stack.pop()
        result = array_index(array, index)
        stack.append(result)
        return node.root['next']

    def handle_conditional_jump(node):
        cond = stack.pop()
        if type(cond) != bool:
            raise ExecutionError(
                f'stack.pop returned a non-bool value ({cond}) in a jump'
            )
        
        return node.root["nextTrue"] if cond else node.root["nextFalse"]

    def handle_print(node):
        value = stack.pop()
        if value == Undefined:
            return node.root["next"]
        if type(value) not in [int, str, list]:
            raise ExecutionError(
                f'PRINT: Invalid value on the stack {value} ({type(value)})'
            )
        
        if type(value) == list:
            print(' '.join([str(i) for i in value]))
        else:
            print(value)
        return node.root["next"]

    def handle_enter_block_scope(node):
        """Handles a special node added before entering a block scope 
        (IF, WHILE, UNTIL). These scopes inherit all declaration from their 
        parent's scope"""
        symboltable_stack.append(
            SymbolTable(parent=symboltable_stack[-1])
        )
        return node.root["next"]
    
    def handle_exit_block_scope(node):
        """Handles a special node added before exiting a block scope"""
        symboltable_stack.pop()
        return node.root["next"]

    def handle_function_declaration(node):
        table = functiontable_stack[-1]
        table.declare(node.root['name'], node.root['params'])
        return node.root['next']

    NODE_FUNCTIONS = {
        'skip': handle_skip, 
        'function': handle_function, 
        'functionDeclaration': handle_function_declaration, 
        'number': handle_const, 
        'string': handle_const, 
        'variable': handle_variable, 
        'binaryExpr': handle_binary_expr, 
        'unaryExpr': handle_unary_expr, 
        'arrayIndexing': handle_array_indexing, 
        'assignment': handle_assignment, 
        'functionCall': handle_function_call,
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
            returned_value = stack.pop()
            if returned_value == Undefined:
                return None
            return returned_value
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
        throw_errors: If set to `False` any error will be ignored instead of 
        thrown as an exception(defaults=False)
    Throws:
        ParseError, ThreadError, ExecutionError
    """
    if throw_errors:
        ast = parse(source, throw_errors=True)
        thread, functions = thread_ast(ast)

        return run_from_thread(
            thread, 
            functions, 
            ast.root['name']
        )
    else:
        try:
            ast = parse(source, throw_errors=True)
            thread, functions = thread_ast(ast)

            return run_from_thread(
                thread, 
                functions, 
                ast.root['name']
            )
        except:
            return None