class ASTNode():
    """Represents the generic node of the Abstract Syntax Tree. 

    This node contains its value in the `root` property and an ordered 
    list of its children in the `children` property.
    """
    
    def __init__(self, root, children=[]):
        self.root = root 
        self.children = list(children) if children else []
    
    def __repr__(self):
        if not self.children:
            return repr(self.root)
        
        children_repr = ', '.join([repr(child) for child in self.children])
        return f"({self.root}, [{children_repr}])"