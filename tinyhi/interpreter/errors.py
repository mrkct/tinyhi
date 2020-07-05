from .undefined import Undefined


class ExecutionError(Exception):
    """Represents an error that occurred while executing a program. These type 
    of errors are logical ones, such as type mismatches or divisions by zero"""
    pass

def strtype(x):
    """Returns a string representation of the type of the value for use 
    in error messages
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