import heapq
import pygame
from typing import Optional
import math


class Node:
    """
    A class used to location information for stations, depots, waypoints, and cities for
    graph representation and wayfinding.

    Attributes:
        type: a string representing the type of the node (station, depot, etc.)
        position: a tuple containing two double entries representing the cartesian coordinates of the node
        edges: a list containing the edges attatched to the node
    """

    def __init__(self, position, node_type=None, edges=[]):
        """
        Initializes the node and node information

        Args:
            position: a tuple containing two double entries representing the cartesian coordinates of the node
            node_type: a string (or None if not specified) representing the type of the node (station, depot, etc.)
            edges: a list containing the edges attatched to the node

        Returns: nothing
        """
        self.type = node_type
        self.position = position
        self.render_position = (position[0] - 5, position[1] - 5)
        self.edges = []
        self.surface = pygame.Surface((5 * 2, 5 * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, (255, 0, 0), (5, 5), 5)

    def add_edge(self, new_edge):
        """
        Adds an edge to a node

        Args:
            new_edge: an edge that is to be added the list of edges of the node

        Returns: nothing
        """
        if new_edge not in self.edges:
            self.edges.append(new_edge)

    # def __repr__(self):
    # """
    # Define the representation of the node instance as its position

    # Args:
    #    none

    # Returns:
    #    A string containing the coordinates of the node
    # """

    # return f"{self.position}"

    # unwanted functionality. commented out if future use is needed


class Edge:
    """
    A class used for edges that represent "links" between two nodes that trains can travel between. Used in
    wayfinding between two nodes.

    Attributes:
        start: a node representing the node at the start of the edge
        end: a node representing the node at the end of the edge
        length: a double representing the distance between `start` and `end`
    """

    def __init__(self, start_node, end_node):
        """
        Initalizes the edge type and automatically edges the new edge its respective nodes

        Args:
            start_node: the node at the start of the edge
            end_node: the node at the end of the edge

        Returns: nothing
        """
        self.start = start_node
        self.end = end_node
        self.trains = []
        self._x_diff = self.end.position[0] - self.start.position[0]
        self._y_diff = self.end.position[1] - self.start.position[1]
        self.length = (self._x_diff**2 + self._y_diff**2) ** 0.5
        start_node.add_edge(self)
        end_node.add_edge(self)
        self.angle = self.angle_between_points()
        self.surface = pygame.Surface(
            (abs(self._x_diff), abs(self._y_diff)), pygame.SRCALPHA
        )
        if self._x_diff >= 0:
            if self._y_diff >= 0:
                self.position = (start_node.position[0], start_node.position[1])
                pygame.draw.line(
                    self.surface,
                    (255, 0, 0),
                    (0, 0),
                    (self._x_diff, self._y_diff),
                    width=10,
                )
            else:
                self.position = (start_node.position[0], end_node.position[1])
                pygame.draw.line(
                    self.surface,
                    (255, 0, 0),
                    (0, -self._y_diff),
                    (self._x_diff, 0),
                    width=10,
                )
        else:
            if self._y_diff >= 0:
                self.position = (end_node.position[0], start_node.position[1])
                pygame.draw.line(
                    self.surface,
                    (255, 0, 0),
                    (0, self._y_diff),
                    (-self._x_diff, 0),
                    width=10,
                )
            else:
                self.position = (end_node.position[0], end_node.position[1])
                pygame.draw.line(
                    self.surface,
                    (255, 0, 0),
                    (0, 0),
                    (-self._x_diff, -self._y_diff),
                    width=10,
                )

    def angle_between_points(self):
        """
        Calculate the angle in degrees between two points relative to the origin (0,0).
        The angle is measured from p1 to p2 in counterclockwise direction.

        Parameters:
            p1 (tuple): First point (x1, y1)
            p2 (tuple): Second point (x2, y2)

        Returns:
            float: Angle in degrees (0 to 360)
        """
        # Vector from origin to p1 and p2
        x1, y1 = self.start.position
        x2, y2 = self.end.position

        # Calculate angles from origin
        dx = x2 - x1
        dy = y2 - y1

        # Difference in radians
        angle_rad = math.atan2(dy, dx)

        # Convert to degrees
        return -math.degrees(angle_rad) % 360

    def give_position(self, portion_traveled):
        if isinstance(portion_traveled, (int, float)):
            if portion_traveled < 0:
                portion_traveled = 0
            elif portion_traveled > 1:
                portion_traveled = 1
            return (
                self.start.position[0] + (self._x_diff * portion_traveled),
                self.start.position[1] + (self._y_diff * portion_traveled),
            )
        else:
            raise ValueError("portion_traveled must be an integer or float")

    def add_train(self, new_train):
        if new_train not in self.trains:
            self.trains.append(new_train)

    def remove_train(self, target_train):
        if target_train in self.trains:
            self.trains.remove(target_train)


class Graph:
    """
    Combine the two classes that can create a node graph using edges and nodes

    Given starting node and an end node, return a list of nodes and edges that get you from the
    starting node to the end node.

    Class used for wayfinding calculations between two nodes

    Attributes:
        nodes: a list of nodes
    """

    def __init__(self, nodes=[]):
        """
        Initializes the graph class

        Args:
            nodes: a list of nodes

        Returns: nothing
        """
        self.nodes = nodes

        # in the current implementation, this doesn't really do anything.
        # if it isn't broken, don't fix it (yet)

    def find_shortest_path(
        self, start: "Node", end: "Node"
    ) -> tuple[float, list["Node"]]:
        """
        Find the shortest path between two nodes using their edges using Dijkstra's algorithm

        Explores the graph outward from `start`, always expanding the
        cheapest-known frontier node first, and terminates as soon as `end` is
        popped from the heap — guaranteeing the returned path is optimal.
        Edge weights are taken from each edge's `length` attribute, and edges are
        treated as undirected (traversable in either direction).

        Args:
            start: a node representing the origin node (the starting node)
            end: a node representing the destination node (the ending node)

        Returns:
            a tuple formatted as follows: (distance, path), where
                distance: the total distance of the path
                path: [`start`, node, node, ..., `end`] represents the nodes along the path from `start` to `end`

        Raises:
            ValueError if no path exists.
        """
        # dist maps node -> best known cost to reach it
        dist: dict["Node", float] = {start: 0.0}
        # prev maps node -> the node we came from on the best path
        prev: dict["Node", Optional["Node"]] = {start: None}
        # Min-heap: (cost, node)
        heap: list[tuple[float, "Node"]] = [(0.0, start)]

        while heap:
            cost, node = heapq.heappop(heap)

            # Early exit
            if node is end:
                return cost, self._reconstruct_path(prev, end)

            # Skip stale heap entries
            if cost > dist.get(node, float("inf")):
                continue

            for edge in node.edges:
                neighbour = edge.end if edge.start is node else edge.start
                new_cost = cost + edge.length

                if new_cost < dist.get(neighbour, float("inf")):
                    dist[neighbour] = new_cost
                    prev[neighbour] = node
                    heapq.heappush(heap, (new_cost, neighbour))

        raise ValueError(f"No path exists between {start} and {end}")

    def _reconstruct_path(
        self,
        prev: dict["Node", Optional["Node"]],
        end: "Node",
    ) -> list["Node"]:
        """
        Reconstructs the shortest path from start to end using a predecessor map.

        Traces back through the `prev` dictionary from `end` to the start node
        (identified by its None predecessor), then reverses the result to return
        the path in start-to-end order.

        Args:
            prev: A mapping from each visited node to the node it was reached from.
                The start node maps to None, marking the beginning of the chain.
            end:  The destination node to trace back from.

        Returns:
            An ordered list of nodes representing the shortest path from start to
            end, inclusive of both endpoints.
        """
        path = []
        node: Optional["Node"] = end
        while node is not None:
            path.append(node)
            node = prev[node]
        return list(reversed(path))
