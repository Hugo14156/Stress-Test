class Avatar:
    """
    Transports passengers and/or cargo along a line. Pathfinds to closest owned depot when in need
    of maintenance.

    Trains are the core of the transport system. Can be bought at a TrainDepot, and will remain
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
            self._location = depot
        else:
            raise ValueError("depot must be an instance of the TrainDepot class")
        if all(isinstance(car, Car) for car in cars):
            self._cars = cars
        else:
            raise ValueError(
                "cars must be a list containing either nothing or only Car/children-of-Car objects"
            )
        if isinstance(avatar, Avatar):
            self.avatar = avatar
        else:
            raise ValueError(
                "avatar must be an Avatar object or a child object of the Avatar class"
            )
        self._bound = None
        self._line = None
        self._position = None

    def assign_line(self, new_line):
        self.line = new_line
