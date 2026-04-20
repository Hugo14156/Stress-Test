"""Stress Test application using pygame for rendering and event handling."""

import os
import tkinter as tk
import pygame
from app.player import Player
from app.core.node_graph import Node, Edge, Graph
from app.entities.line import Line
from app.entities.train import Train
from app.entities.car import Car
from app.avatars.train_cars.test_car import TestCar
from app.entities.train_depot import TrainDepot
from app.avatars.trains.test_train import TestTrain


class Game:
    """
    Main game controller for Stress Test.

    The `Game` object represents the entire Stress Test application. It is the
    single entry point for running the game in server, client, or hybrid
    server‑client mode.

    - **Server mode:** Runs a headless simulation, broadcasting authoritative
      game state to all connected clients and applying their inputs each tick.
    - **Client mode:** Opens the main menu, allows configuration changes, and
      runs local or multiplayer sessions.
    - **Server‑client mode:** Acts as both server and client simultaneously,
      rendering the game locally while also serving as the authoritative host.

    Only one server or server‑client instance may host a lobby at a time.

    Examples
    --------
    >>> game = Game()
    """

    def __init__(self):
        """
        Initialize a new Game instance.

        Loads configuration if available; otherwise falls back to default
        settings. Initializes core game containers such as nodes, edges, trains,
        and lines.
        """
        self._fps = None
        self._local_player = None
        self._run_type = None
        self._resolution = None
        self.nodes = []
        self.edges = []
        self.trains = []
        self.lines = []
        if not self._load_config():
            self._set_default_configs()

    def _load_config(self):
        """
        Attempt to load a configuration file.

        Returns
        -------
        bool
            True if a configuration file was successfully loaded, False
            otherwise.
        """
        return False

    def _set_default_configs(self):
        """
        Apply default configuration settings.

        Sets default FPS, run type, resolution, and initializes the local
        player and a test train depot.
        """
        self._fps = 60
        self._run_type = "client"
        local_player_name = str(os.getlogin())
        root = tk.Tk()
        root.withdraw()
        self._resolution = (
            root.winfo_screenwidth(),
            root.winfo_screenheight(),
        )
        root.quit()
        self._local_player = Player(self, local_player_name)
        self.test_depot = TrainDepot(self._local_player, (0, 0), Node((0, 0)))

    def run_game(self):
        """
        Start the main game loop.

        Initializes pygame, sets up rendering, processes input, updates trains,
        and draws the world each frame. The loop continues until the user closes
        the window.
        """
        pygame.init()
        screen = pygame.display.set_mode(self._resolution)
        clock = pygame.time.Clock()
        running = True
        blue = pygame.Surface((50, 50))
        blue.fill("blue")

        red = pygame.Surface((50, 50))
        red.fill("red")

        green = pygame.Surface((50, 50))
        green.fill("green")
        self.place_new_node((300, 300))
        self.place_new_edge(self.nodes[-1], (600, 400))
        self.place_new_edge(self.nodes[-1], (600, 600))
        self.place_new_edge(self.nodes[-1], (900, 600))
        self.place_new_edge(self.nodes[-1], (700, 1200))
        self.place_new_edge(self.nodes[-1], (200, 1000))
        self.make_new_line([self.nodes[0], self.nodes[-1]])
        self.add_test_train(self.edges[0])

        self.trains[0].assign_to_line(self.lines[0])

        clicked_last_tick = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pressed(num_buttons=3)
            if mouse[0]:
                if not clicked_last_tick:
                    new_node_pos = pygame.mouse.get_pos()
                    new_node_world_pos = self._local_player.camera.screen_to_world(
                        new_node_pos[0], new_node_pos[1]
                    )
                    if len(self.nodes) == 0:
                        self.place_new_node(new_node_world_pos)
                    else:
                        self.place_new_edge(self.nodes[-1], new_node_world_pos)
                    clicked_last_tick = True
            else:
                clicked_last_tick = False
            for train in self.trains:
                train.tick(1 / self._fps)
            self._local_player.camera.move(keys)
            screen.fill("grey")
            render_stack = self.compile_render_stack()
            self._local_player.camera.draw(screen, render_stack)
            pygame.display.flip()
            clock.tick(self._fps)

        pygame.quit()

    def make_new_line(self, main_nodes):
        """
        Create a new line connecting the given nodes.

        Parameters
        ----------
        main_nodes : list[Node]
            The primary nodes that define the line.
        """
        new_line = Line(main_nodes)
        self.lines.append(new_line)

    def add_test_train(self, edge):
        """
        Spawn a test train on the given edge.

        Parameters
        ----------
        edge : Edge
            The edge where the train will be placed.
        """
        new_train = Train(self.test_depot, [], TestTrain(), self._local_player)
        new_train.location = self.edges[0]
        new_train.add_cars(
            [Car(new_train, TestCar(), self.test_depot) for i in range(5)]
        )
        self.trains.append(new_train)

    def place_new_node(self, position):
        """
        Create and register a new node.

        Parameters
        ----------
        position : tuple[int, int]
            World‑space coordinates of the new node.

        Returns
        -------
        Node
            The newly created node.
        """
        new_node = Node(position)
        self.nodes.append(new_node)
        return new_node

    def place_new_edge(self, start_node, end_node_position):
        """
        Create a new edge starting from an existing node.

        Parameters
        ----------
        start_node : Node
            The node from which the edge originates.
        end_node_position : tuple[int, int]
            World‑space coordinates of the new end node.

        Returns
        -------
        Edge
            The newly created edge.
        """
        end_node = self.place_new_node(end_node_position)
        new_edge = Edge(start_node, end_node)
        self.edges.append(new_edge)
        return new_edge

    def compile_render_stack(self):
        """
        Build a list of drawable objects for the current frame.

        Returns
        -------
        list[dict]
            A list of dictionaries containing:
            - ``pos``: world‑space position
            - ``surface``: pygame.Surface to draw
        """
        stack = (
            [
                {"pos": node.render_position, "surface": node.surface}
                for node in self.nodes
            ]
            + [{"pos": edge.position, "surface": edge.surface} for edge in self.edges]
            + [
                {
                    "pos": train.avatar.rotate(
                        train.get_position(), train.location.angle
                    )[1],
                    "surface": train.avatar.rotate(
                        train.get_position(), train.location.angle
                    )[0],
                }
                for train in self.trains
            ]
        )
        for train in self.trains:
            stack += [
                {
                    "pos": car.avatar.rotate(car.get_position(), car._location.angle)[
                        1
                    ],
                    "surface": car.avatar.rotate(
                        car.get_position(), car._location.angle
                    )[0],
                }
                for car in train.cars
            ]
        return stack

    @property
    def resolution(self):
        """tuple[int, int]: The current screen resolution."""
        return self._resolution
