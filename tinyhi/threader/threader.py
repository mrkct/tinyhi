from collections import defaultdict
from tinyhi.parser import ASTNode


def thread_ast(ast):
    NEXT_IDENTIFIER = 2
    LAST = 0
    NODES = {
        0: ASTNode({'type': 'start', 'id': 0})
    }

    # TODO: Gestire il caso 'function'
    # Crea una nuova mappa FUNCTIONS (che verra ritornata dalla funzione)
    # che contiene NOME-ID INIZIO
    # Nel threading quando incontro la dichiarazione di una funzione
    # parto da un nuovo thread, come prima cosa faccio degli assegnamenti
    # alle variabili locali. In teoria sullo stack ci saranno già i parametri
    # però essendo uno stack devo fare al contrario gli assegnamenti
    # PROBLEMA: Come gestire poi la visibilità dei blocchi
    # Alla fine del thread di una funzione aggiungi un nodo speciale 'return'
    # Nell'interprete questo andrà a vedere se alla var con stesso nome della
    # funzione è stata assegnato qualcosa

    # TODO: Se scrivo su una riga tipo '1+1' il suo risultato finisce sullo stack
    # ma non verrà mai consumato. Non causa problemi in esecuzione ma è molto brutto
    # ed in teoria si può riempire lo stack facendo 'while true {1}'. Una possibilità
    # è modificare l'ast builder per segnalare quando un'espressione butta via il suo
    # valore di ritorno. Basta mettere una regola per exprStat

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

        assign_identifier(ast)
        NODES[LAST].root["next"] = ast.root["id"]
        LAST = ast.root["id"]

        join_node = ASTNode({"type": "skip"})
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
            'assignment': assignment
        }
        if ast.root["type"] in FUNCTION_TABLE:
            FUNCTION_TABLE[ast.root["type"]](ast)
        else:
            catchall(ast)
    dispatch(ast)
    return NODES