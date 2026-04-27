"""
City entity for Stress Test.

Defines the City class, a station subtype that generates passengers and
manages train boarding. Cities act as origin and destination points for
passengers travelling across the network.
"""

import random

# from app.entities.station import Station
from app.avatars.stations.city_avatar import CityAvatar


class City:
    """A passenger-generating station on the track network.

    Spawns passengers over time for each unique city connection available
    via its lines, and manages boarding when trains arrive and depart.
    """

    cities = [
        "New York",
        "London",
        "Tokyo",
        "Paris",
        "Sydney",
        "Berlin",
        "Toronto",
        "Dubai",
        "Singapore",
        "Rome",
        "Barcelona",
        "Amsterdam",
        "Hong Kong",
        "Los Angeles",
        "Chicago",
        "Cape Town",
        "Bangkok",
        "Istanbul",
        "San Francisco",
        "Lisbon",
        "Windale",
        "Moneyville",
        "Train City",
        "New London",
        "Olintown",
    ]
    ids = {
        "Passenger": ["p", []],
    }

    def __init__(self, nodes):
        """Initialise the city with a node, avatar, and name.

        Args:
            node (Node): The graph node representing this city's position
                in the track network.
            avatar (Avatar): The graphical representation of this city.
            name (str): The display name of this city.
        """
        self._name = random.choice(self.cities)
        self._trains = []
        self._lines = []
        self._passengers = []
        self.center_node = nodes[0]
        self.center_node.reference = self
        self.entry_node = nodes[1]
        self._spawn_rate = 0.1
        self.unique_connections = set()
        self.find_unique_connections()
        self.avatar = CityAvatar()

    def assign_id(self, kind="Passenger"):
        """Generate and register a new unique ID for an entity of the given type.

        Constructs an ID using the type's prefix and an incrementing integer
        based on the last assigned ID for that type. The new ID is appended
        to the type's ID list before being returned.

        Args:
            kind (str): The entity type key, must be one of the keys in the
                ids class variable (e.g. "Train", "Passenger", "Cargo Car").

        Returns:
            str: The newly assigned unique ID string, e.g. "t_player-3".
        """
        if self.ids[kind][1] == []:
            new_id = f"{self.ids[kind][0]}-{0}"
        else:
            new_id = (
                f"{self.ids[kind][0]}-{int(self.ids[kind][1][-1].split("-")[-1]) + 1}"
            )
        self.ids[kind][1].append(new_id)
        return new_id

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
                if isinstance(station.reference, City):
                    unique_connections.add(station)
        self.unique_connections = unique_connections

    def tick(self, dt):
        self.create_passengers(dt)

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
                new_passengers.append(
                    Passenger(self, target_location=connection.reference)
                )
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
            remaining_passengers = target_train.load(candidate_passengers)
            if remaining_passengers is None:
                self._passengers = [
                    passenger
                    for passenger in self._passengers
                    if passenger not in candidate_passengers
                ]
            else:
                self._passengers = [
                    passenger
                    for passenger in self._passengers
                    if (passenger not in candidate_passengers)
                    or (passenger in remaining_passengers)
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

    def add_line(self, new_line):
        if new_line not in self._lines:
            self._lines.append(new_line)

    def remove_line(self, target_line):
        if target_line in self._lines:
            self._lines.remove(target_line)
