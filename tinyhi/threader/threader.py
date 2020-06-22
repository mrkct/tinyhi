from collections import defaultdict
from tinyhi.parser import ASTNode


def thread_ast(ast):
    NEXT_IDENTIFIER = 2
    LAST = 0
    NODES = {
        0: ASTNode({'type': 'start', 'id': 0})
    }

    def assign_identifier(ast):
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
    
    def ifStat(ast):
        nonlocal LAST
        dispatch(ast.root["cond"])

        assign_identifier(ast)
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]

        join_node = ASTNode({"type": "join"})
        assign_identifier(join_node)

        for stat in ast.root["onTrue"]:
            dispatch(stat)
        ast.root["nextTrue"] = ast.root["next"]
        NODES[LAST].root["next"] = join_node.root["id"]

        if len(ast.root["onFalse"]) == 0:
            ast.root["nextFalse"] = join_node.root["id"]
        else:
            LAST = ast.root["id"]
            for stat in ast.root["onFalse"]:
                dispatch(stat)
            ast.root["nextFalse"] = ast.root["next"]
            NODES[LAST].root["next"] = join_node.root["id"]
        del ast.root["next"]

    
    def catchall(ast):
        nonlocal LAST
        assign_identifier(ast)
        
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]

    def dispatch(ast):
        FUNCTION_TABLE = {
            'binaryExpr': binaryExpr, 
            'if': ifStat
        }
        if ast.root["type"] in FUNCTION_TABLE:
            FUNCTION_TABLE[ast.root["type"]](ast)
        else:
            catchall(ast)
    dispatch(ast)
    return NODES