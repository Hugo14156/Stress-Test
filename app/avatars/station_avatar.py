"""Station avatar base class for depots, cities, and other stops."""

from app.avatars.avatar import Avatar


class StationAvatar(Avatar):
    """Base avatar for station sprites and ownership metadata."""

    def __init__(self):
        """Initialise the station avatar with no owner assigned."""
        super().__init__()
        self.player = None
