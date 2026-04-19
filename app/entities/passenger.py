from app.entities.city import City
import names
import random


class Passenger:
    """
    A Passenger is a type of cargo carried by passegner cars. Passengers will be created at cities,
    and will have a target city in mind that is a memebr of a line which services their home city.

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

    def __init__(self, location, name=None, target_location=None):
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
        if isinstance(location, City):
            self._id = location.assign__id("Passenger")
            self._location = location
        else:
            raise ValueError("location must be a City object")
        if isinstance(name, str):
            self._name = name
        else:
            self._name = names.get_full_name()
        if isinstance(target_location, City):
            self._target_location = target_location
        else:
            self._target_location = self._location.assign_target_location()

    def check_valid_train(self, train):
        return self._target_location in train.line().stations()

    def check_valid_city(self, city):
        return city == self._target_location

    def board_train(self, train):
        self._location = train

    def pay(self):
        self._location.player.add_money(4.28)
