"""Stress test application using pygame for rendering and event handling."""

import pygame
import os
import tkinter as tk


class Game:
    """
    Game object which runs Stress Test either as a server, client, or server-client.

    A Game object contains the entirey of Stress-Test, serving as the only entry point a user
    will ever directly interact with to start the game. If running as a server, this object will
    constantly offer itself to host a game, when commanded by a client, it will start a headless
    game of Stress-Test and send the game state every tick to all clients. It will then listen for
    any resoponces from an clients. If it gets any, it will implement them into the next tick.
    In essence, a server will serve as absolute truth. If running as a client, game will open to
    the main menu, allow for setting changes, and launching of local and multiplayer play, as well
    allowing for a change of game type. If set to server-client, a Game object will act as both a
    server and client. Once a multiplyer game has started, a server-client will render the game as
    a client would, while also serving a global truth for all other players. Only one server/
    server-client can be a lobby at a time.

    Args:
        None


    Returns:
        Game: A Game object.

    Raises:
        Nothing

    Examples:
        >>> game = Game()
    """

    def __init__(self):
        """
        Instances Game object.

        Creates a Game object to run on this computer. Upon creation, will search for
        configureation file. If none is found, then will be set to default settings.

        Args:
            None

        Returns:
            Game: A Game object.

        Raises:
            Nothing

        Examples:
            >>> game = Game()
        """
        self._fps = None
        self._local_player = None
        self._run_type = None
        self._resolution = None
        if not self._load_config():
            self._set_default_configs()

    def _load_config(self):
        """
        Searches for config file. If present, will override current parameters with ones listed
        in file.

        Args:
            None

        Returns:
            bool: True if config file found, else False

        Raises:
            Nothing

        Examples:
            >>> self._load_config()
            True
        """
        pass

    def _set_default_configs(self):
        """
        Sets all parameters to default values.

        Args:
            None

        Returns:
            Nothing

        Raises:
            Nothing

        Examples:
            >>> self._set_default_configs()
        """
        self._fps = 60
        self._local_player = str(os.getlogin())
        self._run_type = "client"
        root = tk.Tk()
        root.withdraw()
        self._resolution = [root.winfo_screenwidth(), root.winfo_screenheight()]
        root.quit()

    def run_game(self):
        """
        Runs game.

        Args:
            None

        Returns:
            Nothing

        Raises:
            Nothing

        Examples:
            >>> game.run_game()
        """
        pygame.init()
        screen = pygame.display.set_mode(self._resolution)
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill("purple")
            pygame.display.flip()

            clock.tick(self._fps)

        pygame.quit()
