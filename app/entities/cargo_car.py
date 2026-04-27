"""
Cargo car entity for trains in Stress Test.

Defines the CargoCar class, a specialisation of Car for transporting
cargo. Handles cargo loading and unloading at stations that accept the
relevant cargo type.
"""

from app.entities.car import Car


class CargoCar(Car):
    """A cargo-carrying car that follows a train along the track network.

    Extends Car to replace passenger logic with cargo handling. Loads
    cargo objects up to capacity and unloads them at stations that
    want the carried cargo type.
    """

    def __init__(self, train, avatar, depot):
        """Initialise the cargo car and register it with the depot.

        Args:
            train: The train this car belongs to and follows.
            avatar: The graphical representation of this car.
            depot: The depot used to assign a unique car ID.
        """
        super().__init__(train, avatar, depot, "Cargo Car")
        self.cargo = []

    def load(self, cargo):
        """Load cargo onto the car up to its capacity.

        Attempts to load all provided cargo in order. Stops early if
        the car reaches capacity, returning any cargo that could not
        be loaded.

        Args:
            cargo (list): A list of Cargo objects to attempt to load.

        Returns:
            list: Any cargo that could not be loaded due to capacity.
                Returns an empty list if all cargo was loaded successfully.

        Raises:
            ValueError: If cargo is not a list or tuple.
            ValueError: If any element in cargo is not a Cargo instance.

        Examples:
            >>> load([cargo_1, cargo_2, cargo_3])
            [cargo_3]
        """
        from app.entities.cargo import Cargo

        if not isinstance(cargo, list):
            raise ValueError("cargo must be a list or a tuple.")
        for index, cargo in enumerate(cargo):
            if isinstance(cargo, Cargo):
                raise ValueError(f"index {index} of cargo is not a cargo.")
            if len(self.cargo) < self.avatar.cargo_capacity:
                self.cargo.append(cargo)
                cargo.board_train(self)
            else:
                return cargo[index:]
        return []

    def unload(self, station):
        """Unload all cargo wanted by the current station.

        Iterates over onboard cargo and removes any whose type is accepted
        by the current station, delegating the unload logic to each cargo object.

        Examples:
            >>> unload()
        """
        for cargo in self.cargo:
            if isinstance(self, station.wanted_type):
                cargo.unload(station)
                self.cargo.remove(cargo)
