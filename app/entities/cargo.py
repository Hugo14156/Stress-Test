"""Cargo entities carried by cargo cars and stations."""


class Cargo:
    """Represents a single cargo item created at a station."""

    def __init__(self, kind, station):
        """Create a cargo item and register a unique station-scoped ID.

        Args:
            kind (str): Cargo type label.
            station: Station that spawned the cargo.
        """
        self.id = station.assign_id("Cargo")
        self.location = station
        self.kind = kind
