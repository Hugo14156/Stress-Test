"""
Passenger car entity for trains in Stress Test.

Defines the Car class, which represents a single passenger-carrying car
attached to a train. Handles passenger loading and unloading, position
tracking along track segments, and following the lead vehicle.
"""


from app.entities.entity import Entity


class Car(Entity):
    """
    A train car that follows a train along the track network.

    Manages its own position as a parametric offset behind its leader,
    handles boarding and alighting of passengers, and transitions between
    track segments independently when it crosses a node.
    """

    def __init__(self, train, avatar, depot, kind):
        """Initialise the car and register it with the depot.

        Args:
            train: The train this car belongs to and follows.
            avatar: The graphical representation of this car.
            depot: The depot used to assign a unique car ID.
        """
        super().__init__()
        self.id = depot.assign_id(kind)
        self.owner = depot.owner
        self.train = train
        self._location = self.train._location
        self.avatar = avatar
        self._t = 0
        self._t_delay = 0
        self._speed = 0

    def find_t_delay(self, leader):
        """Calculate the parametric offset behind the leader on the current segment.

        Computes the t-value spacing needed to visually separate this car from
        its leader, based on both sprites' widths and the segment's length.

        Args:
            leader: The preceding vehicle (train or car) to maintain spacing behind.
        """
        distance_offset = (
            self.avatar.surface.get_width() // 2
            + leader.avatar.surface.get_height() // 2
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
        if self.train.location == self._location:
            if self.train.bound == 1:
                self._t = leader._t - self._t_delay
            else:
                self._t = leader._t + self._t_delay
        else:
            self._t += self.train.bound * self.train.speed * dt / self._location.length
            if self._t > 1.0:
                self._arrive_at(leader)
                self.find_t_delay(leader)
            elif self._t < 0.0:
                self._arrive_at(leader)
                self.find_t_delay(leader)

    def _arrive_at(self, leader):
        """Transition the car onto the next track segment upon reaching a node.

        Queries the train's line for the next edge from the given node and
        updates the car's location and t-value accordingly.

        Args:
            node: The node (station or junction) the car has just reached.
        """
        new_edge = leader.location
        self._location = new_edge

    @property
    def location(self):
        return self._location
