from app.avatars.avatar import Avatar


class CarAvatar(Avatar):

    def __init__(self):
        super().__init__()
        self._mass = 0  # in kg
        self._year = 0
        self._name = ""
        self._capacity = 0  # in passengers
