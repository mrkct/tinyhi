class ExecutionError(Exception):
    pass

def run_from_thread(thread, functions, start):
    pass


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
    pass