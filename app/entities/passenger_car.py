"""
Passenger car entity for Stress Test.

Defines the PassengerCar class, a specialisation of Car for transporting
passengers. Handles boarding and alighting of passengers at city stations
along the train's route.
"""

from app.entities.car import Car


class PassengerCar(Car):
    """A passenger-carrying car that follows a train along the track network.

    Extends Car to provide passenger-specific loading and unloading logic.
    Boards passengers whose destination is reachable via the train's line,
    and disembarks them when their destination station is reached.
    """

    def __init__(self, train, avatar, depot):
        """Initialise the passenger car and register it with the depot.

        Args:
            train: The train this car belongs to and follows.
            avatar: The graphical representation of this car.
            depot: The depot used to assign a unique car ID.
        """
        super().__init__(train, avatar, depot, "Passenger Car")
        self.passengers = []

    def load(self, passengers):
        """Load passengers onto the car up to its capacity.

        Attempts to load all provided passengers in order. Stops early if
        the car reaches capacity, returning any passengers that could not
        be boarded.

        Args:
            passengers (list): A list of Passenger objects to attempt to load.

        Returns:
            list: Any passengers that could not be loaded due to capacity.
                Returns an empty list if all passengers were loaded successfully.

        Raises:
            ValueError: If passengers is not a list.
            ValueError: If any element in passengers is not a Passenger instance.

        Examples:
            >>> load([passenger_1, passenger_2, passenger_3])
            [passenger_3]
        """
        from app.entities.passenger import Passenger

        if isinstance(passengers, list):
            raise ValueError(
                "passengers is not a list. Please input passengers as a list of passenger types."
            )
        for index, passenger in enumerate(passengers):
            if isinstance(passenger, Passenger):
                raise ValueError(
                    f"index {index} of passengers is not a passenger. Please input passengers as a list of passenger types."
                )
            if len(self.passengers) < self.avatar.passenger_capacity:
                self.passengers.append(passenger)
                passenger.embark(self)
            else:
                return passengers[index:]
        return None

    def unload(self):
        """Disembark all passengers whose destination matches the current station.

        Iterates over onboard passengers and removes those who have reached
        their destination, delegating the disembark logic to each passenger.

        Examples:
            >>> unload()
        """
        location = self.train.location
        for passenger in self.passengers:
            if passenger.destination == location:
                passenger.disembark(location)
                self.passengers.remove(passenger)
