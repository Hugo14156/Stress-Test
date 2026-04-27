"""Player state and UI helpers for a single save slot."""

from app.view.camera import Camera
from app.view.screens import Screens


class Player:
    """Represents one human player, their view state, and their economy."""

    def __init__(self, game, name, color):
        """Create a player bound to the given game instance.

        Args:
            game: The owning Game instance.
            name (str): Display name for the player.
            color: RGB tuple used for player-owned visuals.
        """
        self._game = game
        self._name = name
        self.camera = Camera(self._game.resolution[0], self._game.resolution[1])
        self.screen = Screens(self._game.resolution[0], self._game.resolution[1])
        self.depots = []
        self.lines = []
        self._balance = 100000
        self.color = color

    def add_money(self, money):
        """Adjust the player's balance by the given amount."""
        self._balance += money

    @property
    def game(self):
        """Game: The owning game instance."""
        return self._game
