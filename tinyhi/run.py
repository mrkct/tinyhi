from tinyhi.parser import parse, check_ast_coherence
from tinyhi.threader import thread_ast
from tinyhi.interpreter import run_from_thread
import sys


def run(source, throw_errors=False):
    """Executes a program from its source code

    Returns:
        The value returned by the outermost function or None if nothing 
        is returned
    Args:
        source (str): The source code of the program to run
        throw_errors: If set to `True` any error will be thrown as an 
        exception instead of being printed on `stderr`
    Throws:
        ParseError, ThreadError, ExecutionError
    """
    def _run():
        ast = parse(source, throw_errors=True)
        check_ast_coherence(ast)
        thread, functions = thread_ast(ast)

        return run_from_thread(
            thread, 
            functions, 
            ast.root['name']
        )
    
    if throw_errors:
        return _run()
    
    try:
        return _run()
    except Exception as e:
        print(e, file=sys.stderr)