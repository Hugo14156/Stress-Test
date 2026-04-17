import heapq
from typing import Optional

class Node:
    """
    """

    def __init__(self, position, node_type = None, edges = []):
        self.type = node_type
        self.position = position
        self.edges = edges
    
    def add_edge(self, new_edge):
        if new_edge not in self.edges:
            self.edges.append(new_edge)
    


class Edge:
    def __init__(self, start_node, end_node):
        self.start = start_node
        self.end = end_node
        self.length = ((self.end.position[0] - self.start.position[0]) ** 2 + (self.end.position[1] - self.start.position[1]) ** 2) ** 0.5
        self.start.add_edge(self)
        self.end.add_edge(self)

class Graph:
    """
    Combine the two classes that can create a node graph using edges and nodes

    Given starting node and an end node, return a list of nodes and edges that get you from the
    starting node to the end node.
    """

    def __init__(self, nodes = []):
        self.nodes = nodes

    def find_shortest_path(self, start: "Node", end: "Node") -> tuple[float, list["Node"]]:
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
    
