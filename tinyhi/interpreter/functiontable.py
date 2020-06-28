from .errors import ExecutionError


class FunctionTable:
    """Represents the functions in scope in a point of the program. """
    def __init__(self, parent = None):
        """A function table starts empty but if a parent is set, if function is 
        not found in this table, it will ask its parent before giving up
        """
        self.parent = parent
        self.functions = {}
    
    def isVisible(self, function_name):
        """Returns whenever a function is visible in the current scope
        Params:
            function_name: A string with the name of the function to check
        Returns:
            `True` if the function is in scope, `False` otherwise
        """
        if function_name in self.functions:
            return True
        if self.parent:
            return self.parent.isVisible(function_name)
        return False
    
    def declare(self, name, params):
        """Declares that a function is visible in the current scope.
        Params:
            name: A string with the name of the function
            params: A list of strings with the name of the parameters
        """
        self.functions[name] = {
            'params': params
        }
    
    def __repr__(self):
        keyvals = ', '.join([f'{k}: {v}' for k, v in self.functions.items()])
        if self.parent:
            return f'[{repr(self.parent)} + {keyvals}]'
        return f'[{keyvals}]'