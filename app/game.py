"""Stress Test application using pygame for rendering and event handling."""

import os
import tkinter as tk
import pygame
from app.player import Player
from app.core.node_graph import Node, Edge, Graph
from app.entities.line import Line
from app.entities.train import Train
from app.entities.car import Car
from app.entities.cargo_car import CargoCar
from app.avatars.train_cars.test_car import TestCar
from app.entities.train_depot import TrainDepot
from app.avatars.trains.test_train import TestTrain
from app.avatars.trains.EMD_E8 import EMD_E8


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
        self.depots = []
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
        self._resolution = (
            1280,
            720,
        )
        root.quit()
        self._local_player = Player(self, local_player_name, (255, 0, 0))

    def run_game(self):
        """
        Start the main game loop.

        Initializes pygame, sets up rendering, processes input, updates trains,
        and draws the world each frame. The loop continues until the user closes
        the window.
        """
        pygame.init()

        screen = pygame.display.set_mode(self._resolution)
        pygame.display.set_caption("Stress Test")

        clock = pygame.time.Clock()

        state = "home"

        running = True

        self.place_new_depot(self._local_player, (100, 100))
        self.place_new_edge(self.nodes[-1], (400, 0))
        self.place_new_edge(self.nodes[-1], (400, 600))
        self.place_new_edge(self.nodes[-1], (-400, 600))
        self.place_new_edge(self.nodes[-1], (-200, 400))
        self.place_new_edge(self.nodes[-1], (0, 0))
        self.make_new_line([self.nodes[3], self.nodes[-1]])
        self.add_test_train()

        self.trains[0].assign_to_line(self.lines[0])

        clicked_last_tick = False
        while running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pressed(num_buttons=3)

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            screen.fill("grey")

            if state == "home":
                if self._local_player.screen.homescreen(screen, events) == "start":
                    state = "game"
                    clicked_last_tick = True

            elif state == "game":
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

                if self._local_player.screen.top_toolbar(screen, events) == "pause":
                    state = "pause"
                elif self._local_player.screen.top_toolbar(screen, events) == "quit":
                    state = "quit"

            elif state == "pause":
                self._local_player.screen.pause_screen(screen, events)
                if self._local_player.screen.pause_screen(screen, events) == "resume":
                    state = "game"

            elif state == "quit":
                self._local_player.screen.quit_screen(screen, events)
                if self._local_player.screen.quit_screen(screen, events) == "yes":
                    running = False
                elif self._local_player.screen.quit_screen(screen, events) == "no":
                    state = "game"

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

    def add_test_train(self):
        """
        Spawn a test train on the given edge.

        Parameters
        ----------
        edge : Edge
            The edge where the train will be placed.
        """
        new_train = Train(self.depots[0], [], EMD_E8(), self._local_player)
        new_train.add_cars(
            [CargoCar(new_train, TestCar(), self.depots[0]) for i in range(5)]
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
        return new_edge, end_node

    def place_new_depot(self, player, position):
        new_depot_center_node = self.place_new_node(position)
        _, new_depot_entry_node = self.place_new_edge(
            new_depot_center_node, [position[0], position[1] - 100]
        )
        new_depot = TrainDepot(player, [new_depot_center_node, new_depot_entry_node])
        self.depots.append(new_depot)

    def compile_node_render_stack(self):
        return [
            {"pos": node.render_position, "surface": node.surface}
            for node in self.nodes
        ]

    def compile_edge_render_stack(self):
        return [
            {"pos": edge.render_position, "surface": edge.surface}
            for edge in self.edges
        ]

    def compile_train_render_stack(self):
        train_render_stack = []
        for train in self.trains:
            render_info = train.avatar.rotate(
                train.get_position(), train.location.angle
            )
            train_render_stack.append(
                {"pos": render_info[1], "surface": render_info[0]}
            )
            for car in train.cars:
                render_info = car.avatar.rotate(car.get_position(), car.location.angle)
                train_render_stack.append(
                    {"pos": render_info[1], "surface": render_info[0]}
                )
        return train_render_stack

    def compile_depot_render_stack(self):
        return [
            {
                "pos": (
                    depot.center_node.position[0] - depot.avatar.scale,
                    depot.center_node.position[1] - depot.avatar.scale,
                ),
                "surface": depot.avatar.surface,
            }
            for depot in self.depots
        ]

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
            self.compile_node_render_stack()
            + self.compile_edge_render_stack()
            + self.compile_train_render_stack()
            + self.compile_depot_render_stack()
        )
        return stack

    @property
    def resolution(self):
        """tuple[int, int]: The current screen resolution."""
        return self._resolution
