class Car:
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

    def __init__(self, train, avatar, data_sheet, depot):
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
        self.id = depot.assign_pcar_id()
        self.train = train
        self.avatar = avatar
        self.passengers = []
        self.data_sheet = data_sheet

    def load(self, passengers):
        """
        Loads passengers onto car.

        Will attempt to load all passeners provided into car. If car is at capacity
        or reaches capacity while loading, the loading prosses will stop. Will return
        a list of all passengers successfully loaded onto the car.

        Args:
            passengers (list): A list of passengers to attempt to load.

        Returns:
            list: A list of all successfully loaded passengers (an empty list if no passengers were loaded).

        Raises:
            ValueError: passengers is not a list
            ValueError: passengers contained a non passenger type value

        Examples:
            >>> load([passenger_1, passenger_2, passenger_3])
            [passenger_1, passenger_2]
        """
        if isinstance(passengers, list):
            raise ValueError(
                "passengers is not a list. Please input passengers as a list of passenger types."
            )
        for index, passenger in enumerate(passengers):
            if isinstance(passenger, Passenger):
                raise ValueError(
                    f"index {index} of passengers is not a passenger. Please input passengers as a list of passenger types."
                )
            if len(self.passengers) < self.data_sheet["Passenger Capacity"]:
                self.passengers.append(passenger)
                passenger.embark(self)
            else:
                return passengers[:index]
        return passengers

    def unload(self):
        """
        Unload all relevant passengers.

        Asks all passengers to check if the current station is their destination. If so, they will
        disembark.

        Examples:
            >>> unload()
        """
        location = self.train.location
        for passenger in self.passengers:
            if passenger.destination == location:
                passenger.disembark(location)
                self.passengers.remove(passenger)

    def render(self):
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
        pass
