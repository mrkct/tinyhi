from .undefined import Undefined


class ExecutionError(Exception):
    pass

def strtype(x):
    """Returns a string representation of the type of the value
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