"""
Train entity for Stress Test.

Defines the Train class, the core moving entity of the transport system.
Trains travel along assigned lines, loading and unloading cargo and
passengers at each station, and managing their own movement physics
and car offsets.
"""

from app.entities.train_depot import TrainDepot
from app.player import Player
from app.avatars.avatar import Avatar
from app.core.node_graph import Graph


class Train:
    """A locomotive that transports passengers and/or cargo along a line.

    Trains are purchased at a depot and assigned to a line, upon which they
    travel continuously between stations. They manage their own speed and
    acceleration, delegate loading and unloading to their cars, and handle
    edge transitions and station arrivals on the node graph.

    Trains periodically degrade in condition, slowing over time. If condition
    falls below a threshold, the train navigates to the nearest depot for
    maintenance before resuming normal operation.
    """

    def __init__(self, depot, cars, avatar, player):
        """Initialise the train at a depot with a consist of cars and an avatar.

        Args:
            depot (TrainDepot): The depot where this train is created. Used to
                assign an ID and set the initial location.
            cars (list[Car]): The cars attached to this locomotive at purchase.
            avatar: The avatar providing the train's sprite and performance stats.
            player (Player): The player who owns this train.

        Raises:
            ValueError: If depot is not a TrainDepot instance.
            ValueError: If any element in cars is not a Car instance.
            ValueError: If player is not a Player instance.
        """
        from app.entities.car import Car

        # from app.entities.station import Station

        # from app.entities.line import Line

        if isinstance(depot, TrainDepot):
            self._id = depot.assign_id("Train")
            self._location = depot.center_node.edges[0]
        else:
            raise ValueError("depot must be a TrainDepot class.")
        if isinstance(cars, (tuple, list)):
            if all(isinstance(car, Car) for car in cars):
                self._cars = cars
            else:
                raise ValueError("cars must only contain Car objects.")
        else:
            raise ValueError("cars must be a list or tuple")
        if isinstance(avatar, Avatar):
            self._avatar = avatar
        else:
            raise ValueError("avatar must be an Avatar object.")

        if isinstance(player, Player):
            self._player = player
        else:
            raise ValueError("player must be a Player object.")
        self._nav_bound = 1
        self._global_bound = 1
        self._line = None
        self._position = None
        self._speed = 0
        self._max_speed = 0
        self._acceleration = 0
        self._deceleration = 0
        self._t = 0
        self._calculate_movement_statistics()
        self.find_car_offsets()
        self.status = "Idle"
        self.navigation_path = []
        self.condition = 1
        self.time_at_station = 0
        self.station = None

    def tick(self, dt):
        """Advance the train's state by one frame.

        Updates speed and moves the train along its current segment.

        Args:
            dt (float): Delta time in seconds since the last frame.
        """
        if self.status == "Running" or self.status == "Navigating":
            self._calculate_speed(
                True,
                dt,
            )
            self._move_along_segment(dt)
        elif self.status == "Maintaining":
            if self.condition >= 1:
                self.condition = 1
                self.assign_to_line(self._line)
            else:
                self.update_condition(dt)
        elif self.status == "AtStation" and self.time_at_station == 0:
            self.time_at_station += 0.1 * dt
        elif self.status == "AtStation":
            if self.time_at_station >= 1:
                self.status = "Running"
                self.station.remove_train(self)
            else:
                self.time_at_station += 0.1 * dt

    def unload(self, station):
        """Instruct all cars to unload relevant passengers or cargo at the current station."""
        print("Unloading")
        for car in self._cars:
            car.unload(station)

    def load(self, new_cargo):
        """Distribute cargo or passengers across all cars in order until full.

        Passes the full list of cargo to each car in sequence. Each car loads
        what it can and returns the remainder, which is passed to the next car.

        Args:
            new_cargo (list): The cargo or passengers to distribute across cars.

        Returns:
            list | None: Any cargo that could not be loaded, or None if a car
                returned None indicating it could take no more.
        """
        print("Loading")
        for car in self._cars:
            new_cargo = car.load(new_cargo)
            if new_cargo is None:
                return new_cargo
        return new_cargo

    def add_cars(self, new_cars):
        """Append additional cars to the train and recalculate all car offsets.

        Args:
            new_cars (list[Car]): The cars to add to the consist.
        """
        from app.entities.car import Car

        if isinstance(new_cars, Car) and Car not in self._cars:
            self._cars.append(new_cars)
        elif isinstance(new_cars, (tuple, list)) and all(
            isinstance(car, Car) for car in new_cars
        ):
            self._cars += [car for car in new_cars if car not in self._cars]
        else:
            raise ValueError(
                "new_cars must be a Car object or a list/turple of Car objects"
            )
        self.find_car_offsets()

    def _calculate_speed(self, accelerate: bool, dt):
        """Update the train's speed for one frame based on acceleration state.

        Accelerates toward max speed if accelerate is True, otherwise
        decelerates toward zero.

        Args:
            accelerate (bool): Whether the train should accelerate this frame.
            dt (float): Delta time in seconds since the last frame.
        """
        if accelerate and self._speed < self._max_speed:
            self._speed += self._acceleration * dt
        elif self._speed > 0:
            self._speed -= self._deceleration * dt

    def stop_distance(self):
        """Calculate the distance required to come to a complete stop.

        Returns:
            float: The braking distance in world units at the current speed.
        """
        return ((self._speed**2) / self._deceleration) / 2
        # need to fix since deceleration is piecewise

    def update_condition(self, dt):
        if self.status == "Running" or self.status == "Navigating":
            self.condition -= self._avatar.update_condition(dt)
        elif self.status == "Maintaining":
            cost = 10 * dt
            if self.player._balance >= cost:
                self.player.add_money(-cost)
                self.condition += 0.05 * dt

    def _move_along_segment(self, dt):
        """Advance the train and all its cars along the current track segment.

        Updates the train's t-value based on speed and direction, then
        delegates movement to each car. Triggers arrival logic if the
        train crosses a segment boundary.

        Args:
            dt (float): Delta time in seconds since the last frame.
        """
        self._calculate_movement_statistics()
        self._t += self._nav_bound * self._speed * dt / self._location.length
        for index, car in enumerate(self._cars):
            if index == 0:
                car.move_along_segment(self, dt)
            else:
                car.move_along_segment(self._cars[index - 1], dt)

        self.update_condition(dt)
        if self.condition <= 0 and self.status == "Running":
            self.maintain_condition()
        else:
            if self._t > 1.0:
                self._arrive_at(self._location.end)
            elif self._t < 0.0:
                self._arrive_at(self._location.start)

    def find_car_offsets(self):
        """Recalculate the parametric t-delay offsets for all attached cars.

        Each car computes its spacing offset relative to the vehicle ahead of
        it — the first car trails the locomotive, and each subsequent car
        trails the one before it.
        """
        for index, car in enumerate(self._cars):
            if index == 0:
                car.find_t_delay(self)
            else:
                car.find_t_delay(self._cars[index - 1])

    def assign_to_line(self, line):
        """Assign this train to a line for operation."""

        self._line = line
        self.navigation_path = self.navigate_to(line.stations[0])
        self.status = "Navigating"

    def get_position(self):
        """Return the current world position of the locomotive on its segment.

        Returns:
            tuple[float, float]: The (x, y) world coordinates at the current t-value.
        """
        return self._location.give_position(self._t)

    def _arrive_at(self, node):
        """Handle the train reaching a node boundary on its current segment.

        If the node is a main station on the line, triggers station arrival
        logic. Otherwise transitions to the next edge without stopping.

        Args:
            node (Node): The node the train has just reached.
        """
        if self.status == "Running":
            self._location.remove_train(self)
            if node in self.line.stations:
                self._arrive_at_station(node)
            else:
                new_edge, new_global_bound, new_nav_bound = self.line.next_edge(
                    node, self._global_bound, self.station.center_node
                )
                self._location = new_edge
                self._global_bound = new_global_bound
                self._nav_bound = new_nav_bound
                self._location.add_train(self)
                self._t = 0 if new_nav_bound == 1 else 1
        elif self.status == "Navigating":
            if node == self.navigation_path[-1]:
                self._arrive_at_station(node)
            else:
                self._location.remove_train(self)
                next_target_node = self.navigation_path[
                    self.navigation_path.index(node) + 1
                ]
                for edge in node.edges:
                    if edge.start == next_target_node:
                        self._nav_bound = -1
                        self._t = 1
                        self._location = edge
                        self._location.add_train(self)
                    elif edge.end == next_target_node:
                        self._nav_bound = 1
                        self._t = 0
                        self._location = edge
                        self._location.add_train(self)

            # self._distance_to_next_station = self._line.distance_to_next_station(
            #     node, self._bound
            # )

    def _calculate_movement_statistics(self):
        """Derive max speed, acceleration, and deceleration from the avatar and consist."""
        self._max_speed = self._avatar.get_max_speed(self._cars)
        self._acceleration = self._avatar.get_acceleration(self._speed, self._cars)
        self._deceleration = self._avatar.get_deceleration(self._speed, self._cars)

    def _arrive_at_station(self, node):
        """Handle the train arriving at a main station node.

        Transitions the train onto the next edge, updates direction, and
        registers the train with the new edge.

        Args:
            node (Node): The station node the train has arrived at.
        """
        from app.entities.city import City

        if self.status == "Navigating":
            if self.condition <= 0 and isinstance(node.reference, TrainDepot):
                self.status = "Maintaining"
            else:
                self.status = "Running"
                self._arrive_at(node)
        elif self.status == "Running":
            if isinstance(node.reference, City):
                self._speed = 0
                self.status = "AtStation"
                self.unload(node.reference)
                node.reference.add_train(self)
                self.station = node.reference
                self.time_at_station = 0
            new_edge, new_global_bound, new_nav_bound = self.line.next_edge(
                node, self._global_bound, self.station.center_node
            )
            self._location = new_edge
            self._global_bound = new_global_bound
            self._nav_bound = new_nav_bound
            self._location.add_train(self)
            self._t = 0 if new_nav_bound == 1 else 1
        # self._distance_to_next_station = self._line.distance_to_next_station(
        #     node, self._bound
        # )

    @property
    def id(self):
        """str: The unique identifier for this train."""
        return self._id

    @property
    def player(self):
        return self._player

    @property
    def location(self):
        """Edge: The track segment the train is currently travelling along."""
        return self._location

    @property
    def cars(self):
        """list[Car]: The cars attached to this train."""
        return self._cars

    @property
    def avatar(self):
        """Avatar: The graphical and statistical representation of this train."""
        return self._avatar

    @property
    def global_bound(self):
        """int: The current direction of travel; 1 for forward, -1 for reverse."""
        return self._global_bound

    @property
    def nav_bound(self):
        """int: The current direction of travel; 1 for forward, -1 for reverse."""
        return self._nav_bound

    @property
    def line(self):
        """Line: The line this train is currently assigned to."""
        return self._line

    @property
    def position(self):
        """tuple[float, float] | None: The cached world position of the train."""
        return self._position

    @property
    def speed(self):
        """float: The current speed of the train in pixels per second."""
        return self._speed

    @property
    def acceleration(self):
        """float: The acceleration rate in pixels per second squared."""
        return self._acceleration

    @property
    def deceleration(self):
        """float: The deceleration rate in pixels per second squared."""
        return self._deceleration

    def set_id(self, new_id):
        """Set the train's unique identifier.

        Args:
            new_id (str): The new ID string to assign.

        Raises:
            ValueError: If new_id is not a string.
        """
        if isinstance(new_id, str):
            self._id = new_id
        else:
            raise ValueError("new_id must be a string.")

    def set_location(self, new_location):
        """Set the train's current location.

        Args:
            new_location (Station | TrainDepot | None): The new location to assign.

        Raises:
            ValueError: If new_location is not a Station, TrainDepot, or None.
        """
        from app.entities.station import Station

        if isinstance(new_location, (Station, TrainDepot, None)):
            self._location = new_location
        else:
            raise ValueError("new_location must be a Station, TrainDepot, or None type")

    def set_cars(self, new_cars):
        """Replace the train's consist with a new list of cars.

        Args:
            new_cars (list[Car]): The new list of Car objects.

        Raises:
            ValueError: If any element in new_cars is not a Car instance.
        """
        from app.entities.car import Car

        if all(isinstance(car, Car) for car in new_cars):
            self._cars = new_cars
        else:
            raise ValueError(
                "new_cars must be a list containing either nothing or only Car/children-of-Car objects."
            )

    def maintain_condition(self):
        self.find_nearest_depot()
        self.status = "Navigating"

    def set_avatar(self, new_avatar):
        """Replace the train's avatar.

        Args:
            new_avatar (Avatar): The new Avatar object to assign.

        Raises:
            ValueError: If new_avatar is not an Avatar instance.
        """
        if isinstance(new_avatar, Avatar):
            self._avatar = new_avatar
        else:
            raise ValueError(
                "new_avatar must be an Avatar object or a child object of the Avatar class."
            )

    def set_bound(self, new_bound):
        """Set the train's direction of travel.

        Args:
            new_bound (bool | None): The new bound value.

        Raises:
            ValueError: If new_bound is not a boolean or None.
        """
        if isinstance(new_bound, (bool, None)):
            self._global_bound = new_bound
        else:
            raise ValueError("new_bound must be a boolean or None type.")

    def set_line(self, new_line):
        """Assign the train to a new line.

        Args:
            new_line (Line): The line to assign.

        Raises:
            ValueError: If new_line is not a Line instance.
        """
        from app.entities.line import Line

        if isinstance(new_line, Line):
            self._line = new_line
        else:
            raise ValueError("new_line must be a Line type.")

    def set_position(self, new_position):
        """Set the train's cached world position.

        Args:
            new_position (tuple | list): A three-element sequence of ints or
                floats representing the new position.

        Raises:
            ValueError: If new_position does not contain exactly three numeric values.
        """
        if len(new_position) == 3 and all(
            isinstance(element, (int, float)) for element in new_position
        ):
            self._position = new_position
        else:
            raise ValueError(
                "new_position must be a three element long list or turple integers or floats"
            )

    def find_nearest_depot(self):
        graph = Graph()
        shortest_length = float("inf")
        shortest_path = []
        start_node = (
            self._location.end if self._nav_bound == 1 else self._location.start
        )
        for depot in self._player.game.depots:
            if depot.player == self._player:
                path_info = graph.find_shortest_path(start_node, depot.center_node)
                if path_info[0] < shortest_length:
                    shortest_path = path_info[1]
                    shortest_length = path_info[0]
        self.navigation_path = shortest_path
        self.status = "Navigating"

    def navigate_to(self, target_node):
        graph = Graph()
        return graph.find_shortest_path(self._location.start, target_node)[1]
