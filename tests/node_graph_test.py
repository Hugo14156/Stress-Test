from pathlib import Path
import sys
import pygame
import unittest
import math

pygame.init()
pygame.display.set_mode((1, 1))
# Allow running this test file directly from inside the tests directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.node_graph import Node, Edge, Graph  # Replace with your actual filename

class TestGraphWayfinding(unittest.TestCase):

    def setUp(self):
        """Set up a simple graph for testing."""
        # Nodes in a 100x100 grid layout
        self.n_start = Node((0, 0))
        self.n_mid = Node((100, 0))
        self.n_end = Node((100, 100))
        self.n_isolated = Node((500, 500))
        
        # Edges
        self.e1 = Edge(self.n_start, self.n_mid)  # Length 100
        self.e2 = Edge(self.n_mid, self.n_end)    # Length 100
        self.graph = Graph([self.n_start, self.n_mid, self.n_end, self.n_isolated])

    ## --- Geometry & Structure Tests ---

    def test_edge_length_calculation(self):
        """Verify that edge length is calculated correctly using Pythagoras."""
        # Diagonal edge (3-4-5 triangle)
        n1 = Node((0, 0))
        n2 = Node((30, 40))
        edge = Edge(n1, n2)
        self.assertEqual(edge.length, 50.0)

    def test_node_edge_relationship(self):
        """Ensure adding an edge updates the nodes' edge lists."""
        self.assertIn(self.e1, self.n_start.edges)
        self.assertIn(self.e1, self.n_mid.edges)

    def test_angle_calculation(self):
        """Verify the angle logic (Pygame's coordinate system usually has Y increasing downwards)."""
        # (0,0) to (100, 0) is 0 degrees (Right)
        self.assertEqual(self.e1.angle_between_points(), 0.0)
        
        # (100, 0) to (100, 100) is 270 degrees (Down in Pygame coords)
        # Note: Your code uses -math.degrees, which aligns with Pygame's rotation
        self.assertEqual(self.e2.angle_between_points(), 270.0)

    def test_give_position(self):
        """Check if portion_traveled returns the correct coordinate."""
        # Halfway point of e1 (0,0 to 100,0) should be (50,0)
        pos = self.e1.give_position(0.5)
        self.assertEqual(pos, (50.0, 0.0))
        
        # Bounds checking
        self.assertEqual(self.e1.give_position(-1), (0.0, 0.0))
        self.assertEqual(self.e1.give_position(2), (100.0, 0.0))

    ## --- Pathfinding Tests ---

    def test_shortest_path_simple(self):
        """Test a clear path between three nodes."""
        cost, path = self.graph.find_shortest_path(self.n_start, self.n_end)
        self.assertEqual(cost, 200.0)
        self.assertEqual(path, [self.n_start, self.n_mid, self.n_end])

    def test_shortest_path_complex(self):
        """Test Dijkstra's ability to pick the cheaper of two routes."""
        # Add a direct shortcut from start to end (diagonal)
        # Distance is sqrt(100^2 + 100^2) ≈ 141.4
        shortcut = Edge(self.n_start, self.n_end)
        
        cost, path = self.graph.find_shortest_path(self.n_start, self.n_end)
        self.assertLess(cost, 200.0)
        self.assertEqual(path, [self.n_start, self.n_end])

    def test_no_path_exists(self):
        """Verify that a ValueError is raised if the graph is disconnected."""
        with self.assertRaises(ValueError):
            self.graph.find_shortest_path(self.n_start, self.n_isolated)

    def test_start_is_end(self):
        """Verify behavior when start and end nodes are the same."""
        cost, path = self.graph.find_shortest_path(self.n_start, self.n_start)
        self.assertEqual(cost, 0.0)
        self.assertEqual(path, [self.n_start])

if __name__ == "__main__":
    unittest.main()