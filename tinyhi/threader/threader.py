from collections import defaultdict
from tinyhi.parser import ASTNode


def thread_ast(ast):
    """Modifies the AST roots with new fields that allow to follow the 
    execution of the program. In particular this function will add:
    - A `nextTrue` and `nextFalse` field for IF, WHILE, UNTIL that contains 
    the ID of the node to follow based on the result of the value on the top 
    of the stack
    - A `next` field for all the other nodes, containing the ID of the next 
    node to be executed
    - An `id` field for all nodes that can be used to quickly access that node
    in the returned `NODES` dictionary

    In some points a new node with type `skip` is added. These can be skipped 
    and are only useful for simplifying the execution

    Returns:
        NODES: A dictionary that allows to access quickly any node in the AST 
        using their ID
        FUNCTIONS: A dictionary that maps each function name to the ID of the 
        node where their code starts
    Throws:
        ValueError if 2 functions with the same name appear in the AST
    
    """
    NEXT_IDENTIFIER = 2
    LAST = 0
    NODES = {
        0: ASTNode({'type': 'start', 'id': 0})
    }
    FUNCTIONS = {}

    # Here we also set for some nodes  what functions they can call from their 
    # block. The nodes have different scopes are :
    # functionDeclaration, if, while, until
    scope_stack = [[]]

    def find_declared_functions(nodes):
        """Finds the names of all functions declared in a list of nodes. 
        This search is not recursive, if a function is declared in a branch 
        of one of the top nodes it won't be returned. 

        Args:  
            nodes: A list of `ASTNodes` representing each a statement
        Returns:  
            A list of string representing the functions declared without 
            visiting the children of those nodes
        
        Example:  
            For example, given a list of 

                [block f1, (if [block f2] [block f3]), block f4]
            
            This will return ['f1', 'f4']
        """
        return [n.root['name'] for n in nodes if n.root['type'] == 'function']

    def append_node(node, key='next'):
        """Appends a node to the current last node visited by setting 
        a key in the last node's root to the node's id. If the node 
        doesn't have an id it will be assigned to it. This will move the 
        current last node to the newly attached one

        Params:
            node: The ASTNode that will be appended to the current last node
            key: The key to use in the last node's root to append the node
        """
        nonlocal LAST
        if 'id' not in node.root:
            assign_identifier(node)
        NODES[LAST].root[key] = node.root["id"]
        LAST = node.root["id"]

    def assign_identifier(ast):
        '''Registers the AST in the NODES dict and gives it a numeric id
        in the 'id' field in the root'''
        nonlocal NEXT_IDENTIFIER
        ast.root["id"] = NEXT_IDENTIFIER
        NODES[ast.root["id"]] = ast
        NEXT_IDENTIFIER += 1

    def function_declaration(ast):
        nonlocal LAST
        if ast.root['name'] in FUNCTIONS:
            # TODO: Maybe change with a custom exception?
            message = f'Function name "{ast.root["name"]}" was already used'
            raise ValueError(message)
        # A function declaration could happen in the middle of another function
        # We need to save the previous LAST so that it can pass through the 
        # declaration
        saved_last = LAST

        assign_identifier(ast)
        LAST = ast.root["id"]
        FUNCTIONS[ast.root["name"]] = ast.root["id"]
        
        function_name = ast.root['name']
        declared_functions = find_declared_functions(ast.children)
        scope = list(set(scope_stack[-1] + [function_name] + declared_functions))
        append_node(ASTNode({
            'type': 'setInScopeFunctions', 
            'functions': scope
        }))
        
        scope_stack.append(scope)
        for stat in ast.children:
            dispatch(stat)
        scope_stack.pop()
        
        return_node = ASTNode({
            'type': 'return', 
            # This is useful for when we run the program
            'functionName': ast.root['name']
        })
        assign_identifier(return_node)
        NODES[LAST].root['next'] = return_node.root['id']
        
        LAST = saved_last

    def binary_expr(ast):
        nonlocal LAST
        left, right = ast.children
        dispatch(left)
        dispatch(right)
        
        append_node(ast)
    
    def unary_expr(ast):
        nonlocal LAST
        op = ast.root["op"]
        operand = ast.children[0]
        dispatch(operand)
        
        append_node(ast)
    
    def array_indexing(ast):
        nonlocal LAST
        left, index = ast.children
        dispatch(left)
        dispatch(index)
        
        append_node(ast)

    def function_call(ast):
        nonlocal LAST
        params = ast.children
        for p in params:
            dispatch(p)
        append_node(ast)

    def if_stat(ast):
        nonlocal LAST
        dispatch(ast.root["cond"])

        append_node(ASTNode({"type": "enterBlockScope"}))
        append_node(ast)
        
        exit_block_scope = ASTNode({"type": "exitBlockScope"})
        assign_identifier(exit_block_scope)

        if len(ast.root["onTrue"]) == 0:
            ast.root["nextTrue"] = exit_block_scope.root["id"]
        else:
            declared_functions = find_declared_functions(ast.root["onTrue"])
            scope = scope_stack[-1] + declared_functions
            append_node(ASTNode({
                'type': 'setInScopeFunctions', 
                'functions': scope
            }))

            scope_stack.append(scope)
            for stat in ast.root["onTrue"]:
                dispatch(stat)
            scope_stack.pop()

            ast.root["nextTrue"] = ast.root["next"]
            NODES[LAST].root["next"] = exit_block_scope.root["id"]

        if len(ast.root["onFalse"]) == 0:
            ast.root["nextFalse"] = exit_block_scope.root["id"]
        else:
            LAST = ast.root["id"]
            
            declared_functions = find_declared_functions(ast.root["onFalse"])
            scope = scope_stack[-1] + declared_functions
            append_node(ASTNode({
                'type': 'setInScopeFunctions', 
                'functions': scope
            }))

            scope_stack.append(scope)
            for stat in ast.root["onFalse"]:
                dispatch(stat)
            scope_stack.pop()

            ast.root["nextFalse"] = ast.root["next"]
            NODES[LAST].root["next"] = exit_block_scope.root["id"]
        
        LAST = exit_block_scope.root["id"]
        del ast.root["next"]

    def while_stat(ast):
        nonlocal LAST

        node_before_condition = NODES[LAST]
        dispatch(ast.root['cond'])
        start_of_cond_node_id = node_before_condition.root['next']

        append_node(ASTNode({'type': 'enterBlockScope'}))
        append_node(ast)

        # The 'cond == True' case
        declared_functions = find_declared_functions(ast.root['onTrue'])
        scope = scope_stack[-1] + declared_functions
        append_node(ASTNode({
            'type': 'setInScopeFunctions', 
            'functions': scope
        }))

        scope_stack.append(scope)
        for stat in ast.root['onTrue']: 
            dispatch(stat)
        scope_stack.pop()

        ast.root['nextTrue'] = ast.root['next']
        del ast.root['next']

        append_node(ASTNode({'type': 'exitBlockScope'}))
        go_back_node = ASTNode({
            'type': 'skip', 
            'next': start_of_cond_node_id
        })
        assign_identifier(go_back_node)
        NODES[LAST].root['next'] = go_back_node.root['id']

        # Why are you putting 2 exitBlockScope nodes?
        # Because if we don't add another one after the WHILE block then when 
        # we exit we would still be in the block scope just entered
        # We could handle that in the WHILE but I think it's cleaner this way
        exit_block_scope = ASTNode({'type': 'exitBlockScope'})
        assign_identifier(exit_block_scope)
        ast.root['nextFalse'] = exit_block_scope.root['id']
        LAST = exit_block_scope.root['id']

    def until_stat(ast):
        nonlocal LAST

        enter_block_scope = ASTNode({'type': 'enterBlockScope'})
        append_node(enter_block_scope)
        
        declared_functions = find_declared_functions(ast.root['onFalse'])
        scope = scope_stack[-1] + declared_functions
        append_node(ASTNode({
            'type': 'setInScopeFunctions', 
            'functions': scope
        }))

        scope_stack.append(scope)
        for stat in ast.root['onFalse']:
            dispatch(stat)
        scope_stack.pop()
        append_node(ASTNode({'type': 'exitBlockScope'}))

        dispatch(ast.root['cond'])
        append_node(ast)

        join_node = ASTNode({'type': 'skip'})
        assign_identifier(join_node)
        ast.root['nextTrue'] = join_node.root['id']
        ast.root['nextFalse'] = enter_block_scope.root['id']
        LAST = join_node.root['id']
        
    def assignment(ast):
        nonlocal LAST

        if len(ast.children) > 0:
            value = ast.children[0]
            dispatch(value)
        append_node(ast)
    
    def print_stat(ast):
        nonlocal LAST

        dispatch(ast.children[0])
        append_node(ast)

    def catchall(ast):
        print('WARN:', ast.root['type'])
        append_node(ast)

    def dispatch(ast):
        FUNCTION_TABLE = {
            'binaryExpr': binary_expr,
            'unaryExpr': unary_expr,
            'arrayIndexing': array_indexing, 
            'functionCall': function_call, 
            'if': if_stat, 
            'while': while_stat, 
            'until': until_stat, 
            'assignment': assignment, 
            'function': function_declaration, 
            'print': print_stat, 

            'variable': append_node, 
            'number': append_node, 
            'string': append_node
        }
        if ast.root["type"] in FUNCTION_TABLE:
            FUNCTION_TABLE[ast.root["type"]](ast)
        else:
            catchall(ast)
    dispatch(ast)
    return NODES, FUNCTIONS