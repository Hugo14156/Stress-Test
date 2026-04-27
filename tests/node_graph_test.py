"""Standalone smoke test for node-graph shortest-path behaviour."""

from pathlib import Path
import sys

# Allow running this test file directly from inside the tests directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.node_graph import Node, Edge, Graph

node_1 = Node((0, 0))
node_2 = Node((3, 0))
node_3 = Node((0, 2))
node_4 = Node((2, 2))
node_5 = Node((7, 3))

edge_1 = Edge(node_1, node_2)
edge_2 = Edge(node_2, node_3)
edge_3 = Edge(node_3, node_4)
edge_4 = Edge(node_4, node_5)
edge_5 = Edge(node_1, node_4)
edge_6 = Edge(node_4, node_5)
graph = Graph()

print(graph.find_shortest_path(node_1, node_5))
