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
    def functionDeclaration(ast):
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

    def assign_identifier(ast):
        '''Registers the AST in the NODES dict and gives it a numeric id
        in the 'id' field in the root'''
        nonlocal NEXT_IDENTIFIER
        ast.root["id"] = NEXT_IDENTIFIER
        NODES[ast.root["id"]] = ast
        NEXT_IDENTIFIER += 1

    def binaryExpr(ast):
        nonlocal LAST
        op = ast.root["op"]
        left, right = ast.children
        dispatch(left)
        dispatch(right)
        
        assign_identifier(ast)
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]
    
    def unaryExpr(ast):
        nonlocal LAST
        op = ast.root["op"]
        operand = ast.children[0]
        dispatch(operand)
        
        assign_identifier(ast)
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]
    
    def arrayIndexing(ast):
        nonlocal LAST
        left, index = ast.children
        dispatch(left)
        dispatch(index)
        
        assign_identifier(ast)
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]

    def functionCall(ast):
        nonlocal LAST
        params = ast.children
        for p in params:
            dispatch(p)
        assign_identifier(ast)
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]

    def ifStat(ast):
        nonlocal LAST
        dispatch(ast.root["cond"])

        enter_block_scope = ASTNode({"type": "enterBlockScope"})
        assign_identifier(enter_block_scope)
        NODES[LAST].root["next"] = enter_block_scope.root["id"]
        LAST = enter_block_scope.root["id"]

        assign_identifier(ast)
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]

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

    def whileStat(ast):
        nonlocal LAST

        node_before_condition = NODES[LAST]
        dispatch(ast.root['cond'])
        start_of_cond_node_id = node_before_condition.root['next']

        assign_identifier(ast)
        NODES[LAST].root['next'] = ast.root['id']
        LAST = ast.root['id']

        for stat in ast.root['onTrue']: 
            dispatch(stat)
        ast.root['nextTrue'] = ast.root['next']
        del ast.root['next']

        go_back_node = ASTNode({
            'type': 'skip', 
            'next': start_of_cond_node_id
        })
        assign_identifier(go_back_node)
        NODES[LAST].root['next'] = go_back_node.root['id']

        join_node = ASTNode({'type': 'skip'})
        assign_identifier(join_node)
        ast.root['nextFalse'] = join_node.root['id']
        LAST = join_node.root['id']

    def untilStat(ast):
        nonlocal LAST

        before_stats = NODES[LAST]
        for stat in ast.root['onFalse']:
            dispatch(stat)
        dispatch(ast.root['cond'])

        assign_identifier(ast)
        NODES[LAST].root['next'] = ast.root['id']
        LAST = ast.root['id']

        join_node = ASTNode({'type': 'skip'})
        assign_identifier(join_node)
        ast.root['nextTrue'] = join_node.root['id']
        ast.root['nextFalse'] = before_stats.root['next']
        LAST = join_node.root['id']
        
    def assignment(ast):
        nonlocal LAST

        if len(ast.children) > 0:
            value = ast.children[0]
            dispatch(value)
        assign_identifier(ast)
        NODES[LAST].root['next'] = ast.root['id']
        LAST = ast.root['id']
    
    def printStat(ast):
        nonlocal LAST

        dispatch(ast.children[0])
        assign_identifier(ast)
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]

    def catchall(ast):
        nonlocal LAST
        assign_identifier(ast)
        
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]

    def dispatch(ast):
        FUNCTION_TABLE = {
            'binaryExpr': binaryExpr,
            'unaryExpr': unaryExpr,
            'arrayIndexing': arrayIndexing, 
            'functionCall': functionCall, 
            'if': ifStat, 
            'while': whileStat, 
            'until': untilStat, 
            'assignment': assignment, 
            'function': functionDeclaration, 
            'print': printStat
        }
        if ast.root["type"] in FUNCTION_TABLE:
            FUNCTION_TABLE[ast.root["type"]](ast)
        else:
            catchall(ast)
    dispatch(ast)
    return NODES, FUNCTIONS