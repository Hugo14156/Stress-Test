from app.entities.train_depot import TrainDepot
from app.entities.car import Car
from app.avatars.avatar import Avatar
from app.entities.station import Station
from app.entities.line import Line


class Train:
    """
    Transports passengers and/or cargo along a line. Pathfinds to closest owned depot when in need
    of maintenance.

    Trains are the core of the transport system. They can be bought at a depot, and will remain
    there until assigned to a line. Once on a line, a train will travel to each station on the
    line, prompting at each for all compatable cargo/passengers to load/unload. Will periodicaly
    worsen in condition, slowing down as it does so. If condiciton falls below the cutoff, train
    train will navigate to closest depot and reviece maintence. Once fixed, it will return to
    normal operation.

    :param depot: The spawn depot of the train.
    :type depot: TrainDepot
    :param cars: All cars attached to locomotive at purchase.
    :type cars: list of Cars
    :param avatar: Avatar to render. Also provides data sheet for performace stats.
    :type avatar: TrainAvatar
    :raises ValueError: If an invalid value is provided.
    :example:
        >>> obj = Train(depot, [car1, car2, car2], model_2)
    """

    def __init__(self, depot, cars, avatar):
        """
        Short description of the method.

        Longer description providing more details (optional).

        Args:
            param1 (int): Description of param1.
            param2 (str): Description of param2.

        Returns:
            bool: Description of the return value.

        Raises:
            ValueError: Description of conditions when this exception is raised.

        Examples:
            >>> example_method(1, "test")
            True
        """
        if isinstance(depot, TrainDepot):
            self._id = depot.assign_train_id()
            self._location = depot.node()
        else:
            raise ValueError("depot must be an instance of the TrainDepot class.")
        if all(isinstance(car, Car) for car in cars):
            self._cars = cars
        else:
            raise ValueError(
                "cars must be a list containing either nothing or only Car/children-of-Car objects."
            )
        if isinstance(avatar, Avatar):
            self._avatar = avatar
        else:
            raise ValueError(
                "avatar must be an Avatar object or a child object of the Avatar class."
            )
        self._bound = 1
        self._line = None
        self._position = None
        self._speed = 0
        self._max_speed = 0
        self._acceleration = 0
        self._deceleration = 0
        self._t = 0
        self._calculate_movement_statistics()

    def unload(self):
        for car in self._cars:
            car.unload()

    def load(self, new_cargo):
        for car in self._cars:
            new_cargo = car.load(new_cargo)
            if new_cargo is None:
                return new_cargo
        return new_cargo

    def _calculate_speed(self, accelerate: bool):
        if accelerate and self._speed < self._max_speed:
            self._speed += self._acceleration * dt  # TODO Intergrate dt
        elif self._speed > 0:
            self._speed -= self._deceleration * dt  # TODO Intergrate dt

    def _move_along_segment(self):
        self._t += (
            self._bound * self._speed * dt / self._location.length
        )  # TODO Intergrate dt

        if self._t >= 1.0:
            self._arrive_at(self._location.node_b)
        elif self._t <= 0.0:
            self._arrive_at(self._location.node_a)

    def _arrive_at(self, hit_node):
        self._location.remove_train(self)
        new_location, new_bound = self.line.next_edge(self._location, hit_node)
        self._location = new_location
        self._bound = new_bound
        self._location.add_train(self)

    def _calculate_movement_statistics(self):
        self._max_speed = self._avatar.get_max_speed(self._cars)
        self._acceleration = self._avatar.get_acceleration(self._cars)
        self._deceleration = self._avatar.get_deceleration(self._cars)

    @property
    def id(self):
        return self._id

    @property
    def location(self):
        return self._location

    @property
    def cars(self):
        return self._cars

    @property
    def avatar(self):
        return self._avatar

    @property
    def bound(self):
        return self._bound

    @property
    def line(self):
        return self._line

    @property
    def position(self):
        return self._position

    @property
    def speed(self):
        return self._speed

    @property
    def acceleration(self):
        return self._acceleration

    @property
    def deceleration(self):
        return self._deceleration

    def set_id(self, new_id):
        if isinstance(new_id, str):
            self._id = new_id
        else:
            raise ValueError("new_id must be a string.")

    def set_location(self, new_location):
        if isinstance(new_location, (Station, TrainDepot, None)):
            self._location = new_location
        else:
            raise ValueError("new_location must be a Station, TrainDepot, or None type")

    def set_cars(self, new_cars):
        if all(isinstance(car, Car) for car in new_cars):
            self._cars = new_cars
        else:
            raise ValueError(
                "new_cars must be a list containing either nothing or only Car/children-of-Car objects."
            )

    def set_avatar(self, new_avatar):
        if isinstance(new_avatar, Avatar):
            self._avatar = new_avatar
        else:
            raise ValueError(
                "new_avatar must be an Avatar object or a child object of the Avatar class."
            )

    def set_bound(self, new_bound):
        if isinstance(new_bound, (bool, None)):
            self._bound = new_bound
        else:
            raise ValueError("new_bound must be a boolean or None type.")

    def set_line(self, new_line):
        if isinstance(new_line, Line):
            self._line = new_line
        else:
            raise ValueError("new_line must be a Line type.")

    def set_position(self, new_position):
        if len(new_position) == 3 and all(
            isinstance(element, (int, float)) for element in new_position
        ):
            self._position = new_position
        else:
            raise ValueError(
                "new_position must be a three element long list or turple integers or floats"
            )
