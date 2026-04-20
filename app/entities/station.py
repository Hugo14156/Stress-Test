"""
Base station entity for Stress Test.

Defines the Station class, which serves as the parent for all station
types including Cities, Businesses, and Depots. Manages the association
between a node in the track graph and its graphical avatar.
"""


class Station:
    """Parent class for Cities, Businesses, and Depots.

    Binds a graph node to a visual avatar, providing a named location
    on the track network. Intended to be subclassed rather than
    instantiated directly.
    """

    def __init__(self, node, avatar):
        """Initialise the station with a node and avatar.

        Args:
            node (Node): The graph node representing this station's position
                in the track network.
            avatar (Avatar): The graphical representation of this station.

        Raises:
            ValueError: If node is not a Node instance.
            ValueError: If avatar is not an Avatar instance.
        """
        from app.core.node_graph import Node
        from app.avatars.avatar import Avatar

        if isinstance(node, Node):
            self._node = node
        else:
            raise ValueError("node must be a Node object")
        if isinstance(avatar, Avatar):
            self.avatar = avatar
        else:
            raise ValueError("avatar must be an Avatar object")
        self._name = None
