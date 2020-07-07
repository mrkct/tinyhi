"""This module contains some coherence checks that can be done on 
the AST such as checking that all function calls have the right 
number of parameters or that a function is not declared twice
"""
from tinyhi.parser import ASTNode
from .errors import ParseError


def check_ast_coherence(ast):
    """Visits an AST and makes a series of coherence checks:
        - Checks that the outermost function has no parameters
        - Checks that all function calls have the right number of parameters
        - Check that no function is declared twice
    If any of these checks fails this raises ParseError
    Args:
        ast: An ASTNode representing the root of a tree
    Returns:
        None
    Raises:
        ParseError: A coherence check fails
    """
    if len(ast.root['params']) != 0:
        raise ParseError(f'The outermost function cannot have parameters')
    # Contains, for each declared function, how many parameters it expects
    # This is used to check that all function calls have the right number 
    # of parameters and to check that a function is not declared twice
    FUNCTIONS_PARAMS = {}
    def first_visit(ast):
        """Visits the AST and builds all the info necessary for the coherence 
        check"""
        if not isinstance(ast, ASTNode):
            return 
        if ast.root['type'] == 'function':
            function_name = ast.root['name']
            if function_name in FUNCTIONS_PARAMS:
                raise ParseError(
                    f'Function name "{function_name}" was already used'
                ) 
            FUNCTIONS_PARAMS[function_name] = len(ast.root['params'])
        for c in ast.children: first_visit(c)
    first_visit(ast)

    def check(ast):
        """Visits the AST and actually checks that the AST makes sense"""
        if not isinstance(ast, ASTNode):
            return
        if ast.root['type'] == 'functionCall':
            actual_params = ast.children 
            function_name = ast.root['functionName']
            if len(actual_params) != FUNCTIONS_PARAMS[function_name]:
                expected = FUNCTIONS_PARAMS[function_name]
                raise ParseError(
                    f'Function "{function_name}" expected {expected} params,' \
                        f' {len(actual_params)} received'
                )
        for c in ast.children: check(c)
    check(ast)