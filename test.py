from __future__ import annotations
from dataclasses import dataclass, field
import math


@dataclass
class Station:
    pos: tuple[float, float]
    passengers: list = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


@dataclass
class Edge:
    a: Station
    b: Station
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
class Train:
    edge: Edge
    t: float = 0.0  # 0.0 = at edge.a, 1.0 = at edge.b
    direction: int = 1  # +1 toward b, -1 toward a
    speed: float = 100.0
    line: Line = None

    def update(self, dt: float):
        self.t += self.direction * self.speed * dt / self.edge.length

        if self.t >= 1.0:
            self._arrive_at(self.edge.b)
        elif self.t <= 0.0:
            self._arrive_at(self.edge.a)

    def _arrive_at(self, station: Station):
        """Reached a station — pick the next edge on the line."""
        self.edge.trains.remove(self)
        next_edge, next_dir = self.line.next_edge(self.edge, station)
        self.edge = next_edge
        self.direction = next_dir
        self.t = 0.0 if next_dir == 1 else 1.0
        self.edge.trains.append(self)
        # TODO: load/unload passengers here

    @property
    def pos(self) -> tuple[float, float]:
        ax, ay = self.edge.a.pos
        bx, by = self.edge.b.pos
        return (ax + (bx - ax) * self.t, ay + (by - ay) * self.t)


@dataclass
class Line:
    stations: list[Station]
    color: tuple[int, int, int]
    trains: list[Train] = field(default_factory=list)

    def edges(self) -> list[Edge]:
        """Return all edges along this line in order."""
        # Assumes edges exist between consecutive stations
        result = []
        for i in range(len(self.stations) - 1):
            edge = find_edge(self.stations[i], self.stations[i + 1])
            result.append(edge)
        return result

    def next_edge(self, current_edge: Edge, arrived_at: Station) -> tuple[Edge, int]:
        """Given the train just arrived at a station, return (next_edge, direction)."""
        line_edges = self.edges()
        idx = line_edges.index(current_edge)

        # Try to continue in current direction
        # arrived_at == current_edge.b means we were going forward
        going_forward = arrived_at is current_edge.b

        if going_forward and idx < len(line_edges) - 1:
            next_e = line_edges[idx + 1]
            return next_e, (1 if next_e.a is arrived_at else -1)
        elif not going_forward and idx > 0:
            next_e = line_edges[idx - 1]
            return next_e, (1 if next_e.a is arrived_at else -1)
        else:
            # End of line — reverse on the same edge
            return current_edge, -1 if going_forward else 1


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
