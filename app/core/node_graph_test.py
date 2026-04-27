from node_graph import Node, Edge, Graph

# This is sort of a unit test file for node_graph, but not really. Here for a quick check.

node_1 = Node((0,0))
node_2 = Node((3,0))
node_3 = Node((0,2))
node_4 = Node((2,2))
node_5 = Node((7,3))

edge_1 = Edge(node_1, node_2)
edge_2 = Edge(node_2, node_3)
edge_3 = Edge(node_3, node_4)
edge_4 = Edge(node_4, node_5)
edge_5 = Edge(node_1, node_4)
edge_6 = Edge(node_4, node_5)
graph = Graph()

print(graph.find_shortest_path(node_1, node_5))