from app.core.node_graph import Node, Edge, Graph


class Line:
    """
    A line to which trains can be assigned to opperate on. Nessesary for train action and
    navigation.

    A more detailed description of what the class does, its purpose,
    and any important implementation details.

    :param param1: Description of the first parameter.
    :type param1: str
    :param param2: Description of the second parameter.
    :type param2: int
    :raises ValueError: If an invalid value is provided.
    :example:
        >>> obj = MyClass("name", 42)
        >>> obj.method()
        'result'
    """

    def __init__(self, nodes=None):
        if nodes:
            if isinstance(nodes, [list, tuple]):
                if all(isinstance(node, Node) for node in nodes):
                    self._main_nodes = nodes
                else:
                    raise ValueError("nodes must contain only Node objects")
            else:
                raise ValueError("nodes must be a list or turple")
        else:
            self._main_nodes = []
        
    def calculate_navigation_path(self):
        for 
        
