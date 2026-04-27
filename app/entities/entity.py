"""
Base entity class for Stress Test.

All game objects that exist in the world (trains, cities, depots, lines,
cars, cargo, passengers) extend this class. Provides unified ID assignment
and ownership tracking.

IDs are globally unique per entity kind and do not encode ownership.
Ownership is tracked separately via the `owner` field.
"""


class Entity:
    """Base class for all game entities.

    Provides ID assignment and ownership tracking. IDs are globally unique
    per kind (e.g. all cities share one counter, all trains share another).
    The owner field is set independently and can be any object (typically
    a Player).
    """

    _prefixes: dict[str, str] = {
        "Depot":         "dep",
        "City":          "cty",
        "Track":         "trk",
        "Line":          "ln",
        "Train":         "t",
        "Cargo Car":     "cc",
        "Passenger Car": "pc",
        "Cargo":         "c",
        "Passenger":     "p",
    }

    _counters: dict[str, int] = {}

    def __init__(self):
        self.id: str | None = None
        self.owner = None
        self._position: tuple[float, float] | None = None
        self._network_angle: float = 0.0

    def get_position(self) -> tuple[float, float] | None:
        """Return the entity's current world position.

        Returns the network-supplied position if one has been received from
        the server, otherwise returns None. Subclasses that compute position
        locally (Train, Car) should override this to fall back to their
        simulation-derived position when _position is None.

        Returns:
            (x, y) world coordinates, or None if position is not yet known.
        """
        return self._position

    def get_angle(self) -> float:
        """Return the entity's current facing angle in degrees.

        Returns the network-supplied angle if one has been received from
        the server. Subclasses that compute angle locally (Train, Car)
        should override this to fall back to their edge-derived angle
        when no network state has been set.

        Returns:
            Angle in degrees.
        """
        return self._network_angle

    def set_network_state(self, x: float, y: float, angle: float) -> None:
        """Apply a position and angle update received from the server.

        Args:
            x: World x coordinate.
            y: World y coordinate.
            angle: Facing angle in degrees.
        """
        self._position = (x, y)
        self._network_angle = angle

    def assign_id(self, kind: str) -> str:
        """Generate and return a new globally unique ID for the given entity kind.

        The ID format is `prefix_N` where prefix is the short code for the
        kind and N is a monotonically increasing integer shared across all
        instances. Ownership is NOT encoded in the ID — set `self.owner`
        separately.

        Args:
            kind: One of the keys in Entity._prefixes, e.g. "Train", "City".

        Returns:
            A unique ID string such as "t_0", "cty_3", "dep_1".

        Raises:
            KeyError: If kind is not a recognised entity kind.
        """
        prefix = Entity._prefixes[kind]
        count = Entity._counters.get(prefix, 0)
        Entity._counters[prefix] = count + 1
        return f"{prefix}_{count}"

    @staticmethod
    def reset_counters() -> None:
        """Reset all ID counters to zero. Intended for testing only."""
        Entity._counters.clear()
