from tinyhi.parser import ASTNode
from .errors import ThreadError


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
        ThreadError if the syntax tree has problems that either makes the 
        code threading process impossible or create an invalid program
    """
    NEXT_IDENTIFIER = 2
    LAST = 0
    NODES = {
        0: ASTNode({'type': 'start', 'id': 0})
    }
    FUNCTIONS = {}
    # Contains, for each declared function, how many parameters it expects
    FUNCTIONS_PARAMS = {}

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
            raise ThreadError(message)
        
        # A special node that tells the interpreter to add this function to 
        # the symbol table. We need to add this before the function thread 
        # because we want this to execute in any case, even if the function 
        # is never called, to set the scope right
        append_node(ASTNode({
            "type": "functionDeclaration", 
            "name": ast.root["name"], 
            "params": ast.root["params"]
        }))

        # We need to create a different, non-connected thread for this function
        # Therefore we save the current last that will pass through this function 
        # code
        saved_last = LAST

        assign_identifier(ast)
        LAST = ast.root["id"]
        FUNCTIONS[ast.root["name"]] = ast.root["id"]
        FUNCTIONS_PARAMS[ast.root["name"]] = len(ast.root["params"])
                
        for stat in ast.children:
            dispatch(stat)
        
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
        
        function_name = ast.root['functionName']
        if len(params) != FUNCTIONS_PARAMS[function_name]:
            expected = FUNCTIONS_PARAMS[function_name]
            raise ThreadError(
                f'Function "{function_name}" expected {expected} params, ' \
                    f'{len(params)} received'
            )
        
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
            for stat in ast.root["onTrue"]:
                dispatch(stat)
            
            ast.root["nextTrue"] = ast.root["next"]
            NODES[LAST].root["next"] = exit_block_scope.root["id"]

        if len(ast.root["onFalse"]) == 0:
            ast.root["nextFalse"] = exit_block_scope.root["id"]
        else:
            LAST = ast.root["id"]
            for stat in ast.root["onFalse"]:
                dispatch(stat)
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

        for stat in ast.root['onTrue']: 
            dispatch(stat)

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

        for stat in ast.root['onFalse']:
            dispatch(stat)
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