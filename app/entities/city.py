from app.entities.station import Station
import random
from app.entities.passenger import Passenger


class City(Station):
    """
    Brief summary of the class.

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

    def __init__(self, node, name):
        super().__init__(node)
        self._name = name
        self._trains = []
        self._lines = []
        self._passengers = []
        self._spawn_rate = 0.25

    def find_unique_connections(self):
        unique_connections = set()
        for line in self._lines:
            for station in line.stations:
                if isinstance(station, City):
                    unique_connections.add(station)
        return unique_connections

    def create_passengers(self, dt):
        unique_connections = self.find_unique_connections()
        new_passengers = []
        for connection in unique_connections:
            if random.random() <= self._spawn_rate * dt:
                new_passengers.append(Passenger(self, target_location=connection))
        self._passengers += new_passengers

    def add_train(self, new_train):
        if new_train not in self._trains:
            self._trains.append(new_train)
            self.board_passengers(new_train)

    def remove_train(self, leaving_train):
        if leaving_train in self._trains:
            self._trains.remove(leaving_train)

    def board_passengers(self, target_train=None):
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
