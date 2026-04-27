from app.view.camera import Camera
from app.view.screens import Screens


class Player:

    def __init__(self, game, name, color):
        self._game = game
        self._name = name
        self.camera = Camera(self._game.resolution[0], self._game.resolution[1])
        self.screen = Screens(self._game.resolution[0], self._game.resolution[1])
        self.depots = []
        self.lines = []
        self._balance = 100000
        self.color = color

    def add_money(self, money):
        self._balance += money

    @property
    def game(self):
        return self._game
