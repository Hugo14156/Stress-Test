from app.view.camera import Camera


class Player:

    def __init__(self, game, name):
        self._game = game
        self._name = name
        self.camera = Camera(self._game.resolution[0], self._game.resolution[1])
        self._balance = 0.0
