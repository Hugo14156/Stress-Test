class Avatar:
    """
    Serves as a graphical and statistical repesentation of an object in the fame. Framework class
    to be inherited by others. Not to be used by itself.


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

    def __init__(self):
        self._parent_folder_path = ["assets, sprites"]
        self._local_folder_path = []

    def _make_render_request(self):
        pass

    def _render(self):
        pass
