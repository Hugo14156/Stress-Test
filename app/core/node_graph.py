import heapq
import pygame
from typing import Optional
import math


class Node:

    def __init__(self, position, node_type=None):
        self.type = node_type
        self.position = position
        self.render_position = (position[0] - 5, position[1] - 5)
        self.edges = []
        self.surface = pygame.Surface((5 * 2, 5 * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, (255, 0, 0), (5, 5), 5)

    def add_edge(self, new_edge):
        if new_edge not in self.edges:
            self.edges.append(new_edge)


class Edge:

    def __init__(self, start_node, end_node):
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
    """

    def __init__(self, nodes=[]):
        self.nodes = nodes

    def find_shortest_path(
        self, start: "Node", end: "Node"
    ) -> tuple[float, list["Node"]]:
        """
        Returns (total_cost, [node, node, ...]) from start to end.
        Raises ValueError if no path exists.
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
        path = []
        node: Optional["Node"] = end
        while node is not None:
            path.append(node)
            node = prev[node]
        return list(reversed(path))
