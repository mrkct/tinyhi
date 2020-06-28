from .errors import ExecutionError


class SymbolTable:
    """Represents the variables in scope in a point of the program."""
    def __init__(self, parent = None):
        """A symbol table starts empty but if a parent is set, if a variable 
        or is not found in this table, it will ask its parent before giving up
        """
        self.parent = parent
        self.variables = {}
        self.functions = {}
    
    def get(self, variable):
        """Returns the value of a variable given its name
        Args:
            variable: A string with the name of the variable to find
        Returns:
            The value previously stored or None if the variable was never set
        """
        if variable in self.variables:
            return self.variables[variable]['value']
        if self.parent:
            return self.parent.get(variable)
        return None
    
    def put(self, name, value, immutable=False):
        """Sets the value of a variable to a certain value
        Args:
            name: A string with the name of the variable to set
            value: The value to set the variable to
            immutable: If it is set to `True` then the variable won't be able 
            to change its value. Defaults to `False`
        Throws:
            `ExecutionError`: if you try to set a different value to a variable 
            that was set to be immutable
        """
        if name in self.variables and self.variables[name]["immutable"]:
            raise ExecutionError(f'Variable "{name}" is immutable!"')
        if self.parent == None or self.parent.get(name) == None:
            self.variables[name] = {
                'value': value,
                'immutable': immutable
            }
        else:
            self.parent.put(name, value)
    
    def __repr__(self):
        keyvals = ', '.join([f'{k}: {v}' for k, v in self.variables.items()])
        if self.parent:
            return f'[{repr(self.parent)} + {keyvals}]'
        return f'[{keyvals}]'