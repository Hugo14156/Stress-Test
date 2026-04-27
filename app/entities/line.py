"""
Line entity for Stress Test.

Defines the Line class, which represents a named train route connecting
a sequence of stations. Handles navigation path calculation between
stations, edge traversal, and distance queries for train routing logic.
"""

from app.core.node_graph import Node, Graph


class Line:
    """A route along which trains operate, defined by an ordered sequence of nodes.

    Computes a full navigation path between main stations using the graph's
    shortest path algorithm, and provides edge traversal utilities for trains
    moving along the line in either direction.
    """

    def __init__(self, nodes=None):
        """Initialise the line and compute its navigation path.

        Args:
            nodes (list[Node] | tuple[Node] | None): An ordered sequence of Node
                objects defining the main stations on this line. If None, the line
                starts empty.

        Raises:
            ValueError: If nodes is not a list or tuple.
            ValueError: If any element in nodes is not a Node instance.
        """
        if nodes:
            if isinstance(nodes, (list, tuple)):
                if all(isinstance(node, Node) for node in nodes):
                    self._main_nodes = nodes
                else:
                    raise ValueError("nodes must contain only Node objects")
            else:
                raise ValueError("nodes must be a list or turple")
        else:
            self._main_nodes = []
        self.graph = Graph()
        self.navigation_nodes = []
        self.edges = []
        self.color = (255, 0, 0)
        if self._main_nodes != []:
            self.calculate_navigation_path()

    def calculate_navigation_path(self):
        """Build the full ordered navigation node list between all main stations.

        Uses the graph's shortest path algorithm to fill in intermediate nodes
        between each consecutive pair of main stations, producing a complete
        traversal sequence stored in navigation_nodes.
        """
        self.navigation_nodes = []
        self.edges = []
        if len(self._main_nodes) > 1:
            self.navigation_nodes = [self._main_nodes[0]]
            for index, node in enumerate(self._main_nodes):
                if index != 0:
                    self.navigation_nodes += self.graph.find_shortest_path(
                        self._main_nodes[index - 1], node
                    )[1][1:]
            for index, node in enumerate(self.navigation_nodes):
                if index < len(self.navigation_nodes) - 1:
                    for edge in node.edges:
                        if edge.start == self.navigation_nodes[index + 1]:
                            self.edges.append([edge, -1])
                            edge.change_color(self.color)
                            break
                        elif edge.end == self.navigation_nodes[index + 1]:
                            self.edges.append([edge, 1])
                            edge.change_color(self.color)
                            break

    def distance_to_next_station(self, current_node, bound):
        """Calculate the total track distance from a node to the next main station.

        Walks forward along the navigation path in the given direction, summing
        edge lengths until a main station node is reached.

        Args:
            current_node (Node): The node to measure from.
            bound (int): Direction of travel; 1 for forward, -1 for reverse.

        Returns:
            float: The total distance in world units to the next main station.
        """
        current_node_index = self.navigation_nodes.index(current_node)
        i = 1
        current_edge, _ = self.next_edge(current_node, bound)
        distance = current_edge.length
        while True:
            target_node = self.navigation_nodes[current_node_index + (bound * i)]
            if target_node in self._main_nodes:
                break
            next_edge, _ = self.next_edge(target_node, bound)
            distance += next_edge.length
            i += 1
        return distance

    def next_edge(self, current_node, bound, last_station=None):
        """Return the next edge and travel direction from a given node.

        Handles direction reversal at the endpoints of non-looping lines,
        and wraps around for looping lines where the first and last main
        nodes are the same.

        Args:
            current_node (Node): The node to depart from.
            bound (int): Current direction of travel; 1 for forward, -1 for reverse.

        Returns:
            tuple[Edge, int]: The next Edge to travel along and the updated
                bound direction after any reversal.
        """

        if (
            last_station is None
            or len(self.navigation_nodes) <= 2
            or current_node == last_station
        ):
            nav_nodes = self.navigation_nodes
        elif bound == 1:
            nav_nodes = self.navigation_nodes[
                self.navigation_nodes.index(last_station) + 1 :
            ]
        else:
            nav_nodes = self.navigation_nodes[
                : self.navigation_nodes.index(last_station)
            ]

        node_index = nav_nodes.index(current_node)

        if self._main_nodes[0] != self._main_nodes[-1]:
            if node_index == 0:
                bound = 1
            elif node_index == len(nav_nodes) - 1:
                bound = -1

        elif node_index == len(nav_nodes) - 1:
            node_index = 0
        next_node = nav_nodes[node_index + bound]
        for edge in current_node.edges:
            if edge.start == next_node:
                return edge, bound, -1

            elif edge.end == next_node:
                return edge, bound, 1

    def toggle_station(self, station):
        from app.entities.city import City

        for edge in self.edges:
            edge[0].change_color((0, 0, 0))
        if station in self._main_nodes:
            self._main_nodes.remove(station)
            if isinstance(station.reference, City):
                station.reference.remove_line(self)
                for station in self._main_nodes:
                    if isinstance(station.reference, City):
                        station.reference.find_unique_connections()
        else:
            self._main_nodes.append(station)
            if isinstance(station.reference, City):
                station.reference.add_line(self)
                for station in self._main_nodes:
                    if isinstance(station.reference, City):
                        station.reference.find_unique_connections()
        self.calculate_navigation_path()

    def add_station(self, new_station):
        if new_station not in self._main_nodes:
            self._main_nodes.append(new_station)
        self.calculate_navigation_path()

    def remove_station(self, target_station):
        if target_station in self._main_nodes:
            self._main_nodes.remove(target_station)
        self.calculate_navigation_path()

    @property
    def stations(self):
        return self._main_nodes
