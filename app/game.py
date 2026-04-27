"""Stress Test application using pygame for rendering and event handling."""

import os
import tkinter as tk
from app.avatars.trains.EMD_E8 import EMD_E8
from app.view import camera
import pygame
import math
from app.player import Player
from app.core.node_graph import Node, Edge, Graph
from app.entities.line import Line
from app.entities.train import Train
from app.entities.car import Car
from app.entities.cargo_car import CargoCar
from app.entities.passenger_car import PassengerCar
from app.avatars.train_cars.test_car import TestCar
from app.entities.train_depot import TrainDepot
from app.avatars.trains.test_train import TestTrain
from app.avatars.trains.EMD_E8 import EMD_E8
from app.avatars.trains.EMD_E9 import EMD_E9
from app.entities.city import City
from app.avatars.train_cars.passenger_car_1 import PCar1


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
        self.cities = []
        self.cost_per_unit_rail = 2
        self.last_node = None
        self.action = "Normal"
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
        # self._resolution = (
        #     1280,
        #     720,
        # )
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
        self.place_new_city((500, 50))
        self.place_new_city((1800, 1150))
        self.place_new_city((2400, 120))
        self.place_new_city((-3200, -1320))
        self.place_new_city((4000, 2450))
        self.place_new_city((300, -3200))
        self.place_new_city((-5000, 1543))
        self.place_new_city((100, 4500))
        self.place_new_city((1200, 120))
        clicked_last_tick = False
        made_new_line = False
        while running:
            # Gather user inputs at the start of every tick
            events = pygame.event.get()
            keys = pygame.key.get_pressed()
            mouse = pygame.mouse.get_pressed(num_buttons=3)
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = self._local_player.camera.screen_to_world(
                mouse_pos[0], mouse_pos[1]
            )

            # Clear Screen
            screen.fill((240, 220, 180))

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break

            if state == "home":
                if self._local_player.screen.homescreen(screen, events) == "start":
                    state = "game"
                    clicked_last_tick = True

            elif state == "game":

                # Move camera
                self._local_player.camera.move(keys)

                # Tick all trains
                for train in self.trains:
                    train.tick(5 / self._fps)

                # Tick all Cities
                for city in self.cities:
                    city.tick(5 / self._fps)

                # Compile render stack of this frame
                render_stack = self.compile_render_stack(
                    self.action == "PlacingTrack", self.action == "MakingLine"
                )

                # Draw renderstack onto screen
                self._local_player.camera.draw(screen, render_stack)

                # Draw toolbar over game and check for user interaction
                toolbar_action = self._local_player.screen.top_toolbar(screen, events)
                depot_button_action = self._local_player.screen.depot_press_button(
                    screen, events, self._local_player.camera, self.depots
                )

                # Act based on user interaction

                if depot_button_action == "depot":
                    state = "depot"
                    clicked_last_tick = True

                if toolbar_action == "pause":
                    state = "pause"
                    clicked_last_tick = True
                    continue
                elif toolbar_action == "quit":
                    clicked_last_tick = True
                    state = "quit"
                    continue
                elif toolbar_action == "place_track" and self.action != "PlacingTrack":
                    self.action = "PlacingTrack"
                    clicked_last_tick = True
                    continue
                elif toolbar_action == "place_track" and self.action == "PlacingTrack":
                    self.action = "Normal"
                    clicked_last_tick = True
                    self.last_node = None
                    continue
                elif toolbar_action == "make_line" and self.action != "MakingLine":
                    self.action = "MakingLine"
                    clicked_last_tick = True
                    continue
                elif toolbar_action == "make_line" and self.action == "MakingLine":
                    self.action = "Normal"
                    made_new_line = False
                    clicked_last_tick = True
                    self.last_node = None
                    continue

                if self.action == "PlacingTrack":
                    if self.last_node is not None:
                        line_start = self._local_player.camera.world_to_screen(
                            self.last_node.position[0], self.last_node.position[1]
                        )
                        length = math.sqrt(
                            ((self.last_node.position[0] - world_mouse_pos[0]) ** 2)
                            + ((self.last_node.position[1] - world_mouse_pos[1]) ** 2)
                        )
                        can_afford = (
                            self.cost_per_unit_rail * length
                            <= self._local_player._balance
                        )
                        pygame.draw.line(
                            screen,
                            ((0, 255, 0) if can_afford else (255, 0, 0)),
                            line_start,
                            mouse_pos,
                            5,
                        )
                    if mouse[0]:
                        if self.last_node is None and not clicked_last_tick:
                            for node in self.nodes:
                                if (
                                    node.check_collision(world_mouse_pos)
                                    and node.reference is None
                                ):
                                    self.last_node = node
                                    break
                        elif not clicked_last_tick and can_afford:
                            existing_node = False
                            for node in self.nodes:
                                if node.check_collision(world_mouse_pos):
                                    self.place_new_edge(self.last_node, end_node=node)
                                    self.last_node = None
                                    existing_node = True
                                    break
                            if not existing_node:
                                _, self.last_node = self.place_new_edge(
                                    self.last_node, world_mouse_pos
                                )

                            self._local_player._balance -= (
                                self.cost_per_unit_rail * length
                            )
                        clicked_last_tick = True
                    else:
                        clicked_last_tick = False

                elif self.action == "MakingLine":
                    if made_new_line:
                        if mouse[0]:
                            if not clicked_last_tick:
                                for node in self.nodes:
                                    if node.check_collision(world_mouse_pos):
                                        self.lines[-1].toggle_station(node)
                                        break
                            clicked_last_tick = True
                        else:
                            clicked_last_tick = False

                    else:
                        self.make_new_line([])
                        made_new_line = True
                elif keys[pygame.K_t]:
                    self.add_test_train()
                    self.trains[-1].assign_to_line(self.lines[-1])

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

            elif state == "depot":
                self._local_player.screen.depot_screen(screen, events)
                if self._local_player.screen.depot_screen(screen, events) == "return":
                    state = "game"

                if keys[pygame.K_ESCAPE]:
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
        self._local_player.lines.append(new_line)

    def add_test_train(self):
        """
        Spawn a test train on the given edge.

        Parameters
        ----------
        edge : Edge
            The edge where the train will be placed.
        """
        new_train = Train(self.depots[0], [], EMD_E9(), self._local_player)
        new_train.add_cars(
            [PassengerCar(new_train, PCar1(), self.depots[0]) for i in range(5)]
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

    def place_new_edge(self, start_node, end_node_position=None, end_node=None):
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
        if end_node is not None:
            new_edge = Edge(start_node, end_node)
            self.edges.append(new_edge)
            return new_edge, None
        else:
            end_node = self.place_new_node(end_node_position)
            new_edge = Edge(start_node, end_node)
            self.edges.append(new_edge)
            return new_edge, end_node

    def place_new_depot(self, player, position):
        new_depot_center_node = self.place_new_node(position)
        _, new_depot_entry_node = self.place_new_edge(
            new_depot_center_node, [position[0], position[1] - 250]
        )
        new_depot = TrainDepot(player, [new_depot_center_node, new_depot_entry_node])
        self.depots.append(new_depot)

    def place_new_city(self, position):
        new_city_center_node = self.place_new_node(position)
        _, new_city_entry_node = self.place_new_edge(
            new_city_center_node, [position[0], position[1] - 250]
        )
        new_city = City([new_city_center_node, new_city_entry_node])
        self.cities.append(new_city)

    def compile_node_render_stack(self):
        return [
            {"pos": node.render_position, "surface": node.surface}
            for node in self.nodes
        ]

    def compile_edge_render_stack(self, making_lines):
        return [
            {
                "pos": edge.render_position,
                "surface": edge.line_surface if making_lines else edge.full_surface,
            }
            for edge in self.edges
        ]

    def compile_train_render_stack(self):
        train_render_stack = []
        for train in self.trains:
            render_info = (
                train.avatar.rotate(train.get_position(), train.location.angle)
                if train.nav_bound == 1
                else train.avatar.rotate(
                    train.get_position(), train.location.angle - 180
                )
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

    def compile_city_render_stack(self):
        return [
            {
                "pos": (
                    city.center_node.position[0] - (city.avatar.scale // 2),
                    city.center_node.position[1] - (city.avatar.scale // 2),
                ),
                "surface": city.avatar.surface,
            }
            for city in self.cities
        ]

    def compile_render_stack(self, placing_track, making_lines):
        """
        Build a list of drawable objects for the current frame.

        Returns
        -------
        list[dict]
            A list of dictionaries containing:
            - ``pos``: world‑space position
            - ``surface``: pygame.Surface to draw
        """
        stack = []
        if placing_track or making_lines:
            stack = self.compile_node_render_stack()
        stack += (
            self.compile_edge_render_stack(making_lines)
            + self.compile_train_render_stack()
            + self.compile_depot_render_stack()
            + self.compile_city_render_stack()
        )

        return stack

    @property
    def resolution(self):
        """tuple[int, int]: The current screen resolution."""
        return self._resolution
