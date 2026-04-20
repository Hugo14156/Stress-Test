"""
Passenger car entity for trains in Stress Test.

Defines the Car class, which represents a single passenger-carrying car
attached to a train. Handles passenger loading and unloading, position
tracking along track segments, and following the lead vehicle.
"""


class Car:
    """
    A train car that follows a train along the track network.

    Manages its own position as a parametric offset behind its leader,
    handles boarding and alighting of passengers, and transitions between
    track segments independently when it crosses a node.
    """

    def __init__(self, train, avatar, depot):
        """Initialise the car and register it with the depot.

        Args:
            train: The train this car belongs to and follows.
            avatar: The graphical representation of this car.
            depot: The depot used to assign a unique car ID.
        """
        self.id = depot.assign_pcar_id()
        self.train = train
        self._location = self.train._location
        self.avatar = avatar
        self._t = 0
        self._t_delay = 0
        self._speed = 0

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

        if isinstance(passengers, (list, tuple)):
            raise ValueError("passengers must be a list or a tuple.")
        for index, passenger in enumerate(passengers):
            if isinstance(passenger, Passenger):
                raise ValueError(f"index {index} of passengers is not a passenger.")
            if len(self.passengers) < self.avatar.passenger_capacity:
                self.passengers.append(passenger)
                passenger.board_train(self)
            else:
                return passengers[index:]
        return []

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

    def find_t_delay(self, leader):
        """Calculate the parametric offset behind the leader on the current segment.

        Computes the t-value spacing needed to visually separate this car from
        its leader, based on both sprites' widths and the segment's length.

        Args:
            leader: The preceding vehicle (train or car) to maintain spacing behind.
        """
        distance_offset = (
            self.avatar.surface.get_width() / 2
            + leader.avatar.surface.get_width() / 2
            + 0.1
        )
        self._t_delay = distance_offset / self._location.length

    def get_position(self):
        """Return the current world position of this car on its track segment.

        Returns:
            tuple[float, float]: The (x, y) world coordinates at the current t-value.
        """
        return self._location.give_position(self._t)

    def move_along_segment(self, leader, dt):
        """Advance the car's position along its track segment for one frame.

        If the car shares the same segment as the train, its t-value is derived
        directly from the leader's t-value minus the spacing offset. Otherwise,
        the car moves independently and handles segment transitions on crossing
        a node boundary.

        Args:
            leader: The preceding vehicle whose position this car trails.
            dt (float): Delta time in seconds since the last frame.
        """
        if self.train._location == self._location:
            if self.train.bound == 1:
                self._t = leader._t - self._t_delay
            else:
                self._t = leader._t + self._t_delay
        else:
            self._t += self.train.bound * self.train._speed * dt / self._location.length
            if self._t > 1.0:
                self._arrive_at(self._location.end)
                self.find_t_delay(leader)
            elif self._t < 0.0:
                self._arrive_at(self._location.start)
                self.find_t_delay(leader)

    def _arrive_at(self, node):
        """Transition the car onto the next track segment upon reaching a node.

        Queries the train's line for the next edge from the given node and
        updates the car's location and t-value accordingly.

        Args:
            node: The node (station or junction) the car has just reached.
        """
        new_edge, new_bound = self.train._line.next_edge(node, self.train._bound)
        self._location = new_edge
        self._t = 0 if new_bound == 1 else 1
