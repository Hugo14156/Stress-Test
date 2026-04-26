"""
Passenger entity for Stress Test.

Defines the Passenger class, which represents a traveller generated at a
city with a target destination. Passengers wait at their origin city,
board valid trains, and pay a fare upon reaching their destination.
"""

import names


from app.entities.entity import Entity


class Passenger(Entity):
    """A traveller generated at a city with a target destination city.

    Passengers are spawned by cities and assigned a destination reachable
    via a line servicing their home city. They board trains whose routes
    include their destination and disembark upon arrival.
    """

    def __init__(self, location, name=None, target_location=None):
        """Initialise the passenger at a city with a name and target destination.

        If no name is provided, one is generated randomly. If no target location
        is provided, one is assigned by the origin city.

        Args:
            location (City): The city where this passenger is created and waits.
            name (str | None): The passenger's name. If None, a random name
                is generated.
            target_location (City | None): The passenger's destination city.
                If None, the origin city assigns one.

        Raises:
            ValueError: If location is not a City instance.
        """
        from app.entities.city import City

        super().__init__()
        if isinstance(location, City):
            self.id = location.assign_id("Passenger")
            self.owner = location.owner
            self._location = location
        else:
            raise ValueError("location must be a City object")
        if isinstance(name, str):
            self._name = name
        else:
            self._name = names.get_full_name()
        if isinstance(target_location, City):
            self._target_location = target_location
        else:
            self._target_location = self._location.assign_target_location()

    def check_valid_train(self, train):
        """Check whether this passenger's destination is served by the given train.

        Args:
            train: The train to check against.

        Returns:
            bool: True if the train's line includes the passenger's destination.
        """
        return self._target_location in train.line().stations()

    def check_valid_city(self, city):
        """Check whether the given city is this passenger's destination.

        Args:
            city (City): The city to check against.

        Returns:
            bool: True if the city matches the passenger's target location.
        """
        return city == self._target_location

    def board_train(self, train):
        """Update the passenger's location to reflect boarding a train.

        Args:
            train: The train or car the passenger is boarding.
        """
        self._location = train

    def pay(self):
        """Issue a fare payment to the player upon reaching the destination."""
        self._location.player.add_money(4.28)
