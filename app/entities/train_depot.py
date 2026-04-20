from app.entities.train import Train



class TrainDepot:
    """
    A train depot allows for the purchase and maintenece of trains. 

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

    ids = {
        "Cargo Station": ["cs", []],
        "Passenger Station": ["ps", []],
        "Cargo Car": ["cc", []],
        "Passenger Car": ["pc", []],
        "Cargo": ["c", []],
        "Passenger": ["p", []],
        "Train": ["t", []],
    }

    def __init__(self, player, position):
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
        self._position = position
        self._player = player
        self._trains = []

    def assign__id(self, kind):
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
        if self.ids[kind][1] == []:
            new_id = f"{self.ids[kind][0]}_{self._player}-{0}"
        else:
            new_id = f"{self.ids[kind][0]}_{self._player}-{int(self.ids[kind][1][-1].split("-")[-1]) + 1}"
        self.ids[kind][1].append(new_id)
        return new_id
    
    def create_train(self, cars, avatar):
        new_train = Train(self, cars, avatar)
        self.add_train(new_train)
    
    def add_train(self, new_train):
        
