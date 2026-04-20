"""
City entity for Stress Test.

Defines the City class, a station subtype that generates passengers and
manages train boarding. Cities act as origin and destination points for
passengers travelling across the network.
"""

import random
from app.entities.station import Station


class City(Station):
    """A passenger-generating station on the track network.

    Spawns passengers over time for each unique city connection available
    via its lines, and manages boarding when trains arrive and depart.
    """

    def __init__(self, node, avatar, name):
        """Initialise the city with a node, avatar, and name.

        Args:
            node (Node): The graph node representing this city's position
                in the track network.
            avatar (Avatar): The graphical representation of this city.
            name (str): The display name of this city.
        """
        super().__init__(node, avatar)
        self._name = name
        self._trains = []
        self._lines = []
        self._passengers = []
        self._spawn_rate = 0.25
        self.unique_connections = self.find_unique_connections()

    def find_unique_connections(self):
        """Build the set of unique cities reachable from this city via its lines.

        Iterates over all lines and their stations, collecting every other City
        that shares a line with this one.

        Returns:
            set[City]: All distinct City instances reachable from this city.
        """
        unique_connections = set()
        for line in self._lines:
            for station in line.stations:
                if isinstance(station, City):
                    unique_connections.add(station)
        return unique_connections

    def create_passengers(self, dt):
        """Probabilistically spawn new passengers for each reachable connection.

        For each unique connected city, rolls against the spawn rate scaled by
        delta time. Newly created passengers are appended to the waiting list.

        Args:
            dt (float): Delta time in seconds since the last frame.
        """
        from app.entities.passenger import Passenger

        new_passengers = []
        for connection in self.unique_connections:
            if random.random() <= self._spawn_rate * dt:
                new_passengers.append(Passenger(self, target_location=connection))
        self._passengers += new_passengers

    def add_train(self, new_train):
        """Register an arriving train and immediately attempt to board waiting passengers.

        Args:
            new_train: The train arriving at this city.
        """
        if new_train not in self._trains:
            self._trains.append(new_train)
            self.board_passengers(new_train)

    def remove_train(self, leaving_train):
        """Deregister a departing train from this city.

        Args:
            leaving_train: The train departing from this city.
        """
        if leaving_train in self._trains:
            self._trains.remove(leaving_train)

    def board_passengers(self, target_train=None):
        """Board waiting passengers onto trains currently at this city.

        If a specific train is provided, only attempts to board passengers
        whose destination is valid for that train. Otherwise iterates over
        all present trains. Passengers that cannot be boarded remain waiting.

        Args:
            target_train: The train to board passengers onto. If None,
                all trains currently at this city are considered.
        """
        if target_train is not None:
            candidate_passengers = [
                passenger
                for passenger in self._passengers
                if passenger.check_valid_train(target_train)
            ]
            remaining_passengers = target_train.board(candidate_passengers)
            self._passengers = [
                passenger
                for passenger in self._passengers
                if passenger not in candidate_passengers
                or passenger in remaining_passengers
            ]
        else:
            for train in self._trains:
                candidate_passengers = [
                    passenger
                    for passenger in self._passengers
                    if passenger.check_valid_train(train)
                ]
                remaining_passengers = train.board(candidate_passengers)
                self._passengers = [
                    passenger
                    for passenger in self._passengers
                    if passenger not in candidate_passengers
                    or passenger in remaining_passengers
                ]
