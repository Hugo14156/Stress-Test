class Node:
    """
    A RailNetwork is a node-graph based rail system in which nodes represent stations/depots and
    edges represent rail segments.

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

    def __init__(self, position, edges, type=None):
        if isinstance(position, [list, tuple]):
            if all(isinstance(coordinates, [int, float]) for coordinates in position):
                self._position = tuple(position)
            else:
                raise ValueError("All elements of position must be a integer or float.")
        else:
            raise ValueError("position but be a list or tuple.")

        if isinstance(edges, [list, tuple]):
            if all(isinstance(edge, [int, float]) for edge in edges):
                self._position = tuple(position)
            else:
                raise ValueError("All elements of position must be a integer or float.")
        else:
            raise ValueError("position but be a list or tuple.")

        self._position = position

    pos: tuple[float, float]
    edges: list[Edge] = field(default_factory=list)


class Edge:
    a: Node
    b: Node
    trains: list[Train] = field(default_factory=list)

    @property
    def length(self) -> float:
        dx = self.b.pos[0] - self.a.pos[0]
        dy = self.b.pos[1] - self.a.pos[1]
        return math.hypot(dx, dy)

    def other(self, station: Station) -> Station:
        """Given one endpoint, return the other."""
        return self.b if station is self.a else self.a


@dataclass
class Graph:
    stations: list[Station] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)

    def add_edge(self, a: Station, b: Station) -> Edge:
        e = Edge(a, b)
        self.edges.append(e)
        a.edges.append(e)
        b.edges.append(e)
        return e


def find_edge(a: Station, b: Station) -> Edge | None:
    for e in a.edges:
        if e.other(a) is b:
            return e
    return None
