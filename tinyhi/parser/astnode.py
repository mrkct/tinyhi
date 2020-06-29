class ASTNode():
    """Represents a generic node of the Abstract Syntax Tree. 

    This node contains its value in the `root` property and an ordered 
    list of its children in the `children` property.

    Args:
        root: The root's content value (any type)
        children: An ordered list of other ASTNodes
    """
    
    def __init__(self, root, children=[]):
        self.root = root 
        self.children = list(children) if children else []
    
    def __repr__(self):
        if not self.children:
            return repr(self.root)
        
        children_repr = ', '.join([repr(child) for child in self.children])
        return f'({self.root}, [{children_repr}])'
    
    def __str__(self):
        return repr(self)
    
    def __eq__(self, other):
        if type(other) != ASTNode:
            return False
        return self.root == other.root and self.children == other.children