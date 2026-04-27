"""Car avatar base class for rolling stock sprites and stats."""

from app.avatars.avatar import Avatar


class CarAvatar(Avatar):
    """Base avatar for car sprites and capacity-related metadata."""

    def __init__(self):
        """Initialise the avatar with default physical metadata."""
        super().__init__()
        self._mass = 0  # in kg
        self._year = 0
        self._name = ""
        self._capacity = 0  # in passengers
