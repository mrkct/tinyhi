class Value:
    """Represents a generic value in the interpreter. A value can only have 
    the following types: INTEGER, STRING, LIST
    """
    INTEGER = 'int'
    STRING = 'string'
    LIST = 'list'

    def __init__(self, datatype, value):
        if datatype not in [INTEGER, STRING, LIST]:
            raise ValueError(f'Invalid type "{datatype}"')
        self.datatype = datatype
        self.value = value

    def __repr__(self):
        return f'[{self.datatype}: {repr(self.value)}]'
    
    def __str__(self):
        return repr(self)
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.datatype == other.datatype and self.value == other.value