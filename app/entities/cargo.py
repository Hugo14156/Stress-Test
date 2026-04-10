class Cargo:
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

    def __init__(self, kind, station):
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
        self.id = station.assign_id("Cargo")
        self.location = station
        self.kind = kind
