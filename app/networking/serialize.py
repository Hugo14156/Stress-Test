"""
Serialization and deserialization for network packets.

Converts live game objects into JSON-ready dicts (for sending) and applies
incoming dicts back onto game state (for receiving). All coordinates are
world-space. Entity IDs are always assigned by the server, never the client.
"""

import math


# ---------------------------------------------------------------------------
# Lightweight client-side stubs — used for rendering only, no simulation
# ---------------------------------------------------------------------------


class _NetworkTrain:
    """Minimal train stand-in on the client — holds position and avatar only."""

    def __init__(self, train_id: str, line_id: str | None = None, owner_id=None, owner_color=None):
        """Create a client-side train stub from server-provided identifiers."""
        from app.avatars.trains.test_train import TestTrain

        self.id = train_id
        self.line_id = line_id
        self.owner_id = owner_id
        self.owner_color = owner_color
        self.owner = None
        self._position = None
        self._network_angle = 0.0
        self.avatar = TestTrain(tuple(owner_color) if owner_color is not None else None)
        self.cars: list = []

    def get_position(self):
        """Return the last network-synced position."""
        return self._position

    def get_angle(self) -> float:
        """Return the last network-synced heading in radians."""
        return self._network_angle


class _NetworkCar:
    """Minimal car stand-in on the client — holds position and avatar only."""

    def __init__(self, car_id: str, owner_color=None):
        """Create a client-side car stub from server-provided identifiers."""
        from app.avatars.train_cars.test_car import TestCar

        self.id = car_id
        self.owner_color = owner_color
        self.owner = None
        self._position = None
        self._network_angle = 0.0
        self.avatar = TestCar(tuple(owner_color) if owner_color is not None else None)

    def get_position(self):
        """Return the last network-synced position."""
        return self._position

    def get_angle(self) -> float:
        """Return the last network-synced heading in radians."""
        return self._network_angle


class _NetworkCity:
    """Minimal city stand-in on the client — holds position and avatar for rendering."""

    def __init__(self, city_id: str, name: str, node, rotation=0):
        """Create a client-side city stub for rendering."""
        from app.avatars.stations.city_avatar import CityAvatar

        self.id = city_id
        self._name = name
        self.center_node = node
        self.rotation = rotation
        self.avatar = CityAvatar(rotation)


class _NetworkDepot:
    """Minimal depot stand-in on the client — holds position and avatar for rendering."""

    def __init__(self, depot_id: str, node, owner_id: str | None = None, owner_color=None):
        """Create a client-side depot stub for rendering."""
        from app.avatars.stations.depot_avatar import DepotAvatar

        self.id = depot_id
        self.owner_id = owner_id
        self.owner_color = owner_color
        self.center_node = node
        self.avatar = DepotAvatar(None, tuple(owner_color) if owner_color is not None else None)


# ---------------------------------------------------------------------------
# Server -> Client: serialize game state into packet dicts
# ---------------------------------------------------------------------------


def serialize_map(game) -> dict:
    """Full map state — sent once on client connect and on resync."""
    return {
        "type": "map",
        "tracks": [_serialize_track(edge, game) for edge in game.edges],
        "cities": [_serialize_city(city) for city in getattr(game, "cities", [])],
        "depots": [_serialize_depot(depot) for depot in getattr(game, "depots", [])],
        "lines": [_serialize_line(line, game) for line in game.lines],
        "trains": [_serialize_train_static(train) for train in game.trains],
    }


def serialize_tick(game, tick: int, cursors: list[dict]) -> dict:
    """Per-tick state — sent ~20/s. Only moving objects and cursors."""
    return {
        "type": "tick",
        "tick": tick,
        "trains": [
            entry
            for train in game.trains
            for entry in [_serialize_train_position(train)]
            if entry is not None
        ],
        "cars": [
            entry
            for train in game.trains
            for car in train.cars
            for entry in [_serialize_car_position(car)]
            if entry is not None
        ],
        "cursors": cursors,
    }


def serialize_resync(game, tick: int) -> dict:
    """Full state resync — map state plus current train/car positions."""
    data = serialize_map(game)
    data["type"] = "resync"
    data["tick"] = tick
    data["train_positions"] = [
        entry
        for train in game.trains
        for entry in [_serialize_train_position(train)]
        if entry is not None
    ]
    data["car_positions"] = [
        entry
        for train in game.trains
        for car in train.cars
        for entry in [_serialize_car_position(car)]
        if entry is not None
    ]
    return data


def serialize_train_add(train, tick: int) -> dict:
    """Single-train update used for train purchases."""
    return {
        "type": "train_add",
        "tick": tick,
        "train": _serialize_train_static(train),
        "train_position": _serialize_train_position(train),
        "car_positions": [
            entry
            for car in train.cars
            for entry in [_serialize_car_position(car)]
            if entry is not None
        ],
    }


def serialize_track_add(edge, game, tick: int) -> dict:
    """Single-track update used for hot path track placement."""
    return {"type": "track_add", "tick": tick, "track": _serialize_track(edge, game)}


def serialize_line_update(line, game, tick: int) -> dict:
    """Single-line update used for hot path line creation/editing."""
    return {"type": "line_update", "tick": tick, "line": _serialize_line(line, game)}


def serialize_reject(tick: int, action: str, reason: str) -> dict:
    """Build a rejection packet for an action the server could not process."""
    return {"type": "reject", "tick": tick, "action": action, "reason": reason}


def serialize_economy_state(economy, tick: int, owner_id: str | None = None) -> dict:
    """Build an economy state packet addressed to a specific recipient."""
    return {
        "type": "economy_state",
        "tick": tick,
        "owner_id": owner_id,
        "players": economy.players_public(),
        "stocks": economy.stocks_public(),
    }


# ---------------------------------------------------------------------------
# Private helpers — individual object serialization
# ---------------------------------------------------------------------------


def _serialize_track(edge, game) -> dict:
    """Serialize a single track edge to a wire-format dict."""
    edge_id = getattr(edge, "id", None) or f"trk_{game.edges.index(edge)}"
    city_a = _find_station_id(edge.start, game)
    city_b = _find_station_id(edge.end, game)
    return {
        "id": edge_id,
        "station_a": city_a,
        "ax": edge.start.position[0],
        "ay": edge.start.position[1],
        "station_b": city_b,
        "bx": edge.end.position[0],
        "by": edge.end.position[1],
    }


def _serialize_city(city) -> dict:
    """Serialize a city to a wire-format dict."""
    return {
        "id": city.id,
        "x": city.center_node.position[0],
        "y": city.center_node.position[1],
        "name": city._name,
        "rotation": getattr(city, "rotation", 0),
    }


def _serialize_depot(depot) -> dict:
    """Serialize a depot to a wire-format dict."""
    return {
        "id": depot.id,
        "owner_id": getattr(depot, "owner_id", None),
        "owner_color": getattr(depot, "owner_color", None),
        "x": depot.center_node.position[0],
        "y": depot.center_node.position[1],
    }


def _serialize_line(line, game) -> dict:
    """Serialize a line and its station list to a wire-format dict."""
    line_id = getattr(line, "id", f"ln_{game.lines.index(line)}")
    station_ids = [_find_station_id(node, game) for node in line._main_nodes]
    return {
        "id": line_id,
        "owner_id": getattr(line, "owner_id", None),
        "color": list(getattr(line, "color", (255, 0, 0))),
        "stations": station_ids,
    }


def _serialize_train_static(train) -> dict:
    """Serialize a train's identity and car roster (not its position)."""
    line_id = getattr(train.line, "id", None) if train.line else None
    return {
        "id": train.id,
        "owner_id": getattr(train, "owner_id", None),
        "owner_color": getattr(train, "owner_color", None),
        "line_id": line_id,
        "cars": [car.id for car in train.cars],
    }


def _serialize_train_position(train) -> dict | None:
    """Serialize a train's current world position and angle, or None if parked."""
    position = train.get_position()
    if position is None:
        return None
    x, y = position
    return {
        "id": train.id,
        "x": round(x, 2),
        "y": round(y, 2),
        "angle": round(train.get_angle(), 4),
    }


def _serialize_car_position(car) -> dict | None:
    """Serialize a car's current world position and angle, or None if parked."""
    position = car.get_position()
    if position is None:
        return None
    x, y = position
    return {
        "id": car.id,
        "x": round(x, 2),
        "y": round(y, 2),
        "angle": round(car.get_angle(), 4),
    }


def _find_station_id(node, game) -> str:
    """Return the ID of whichever city or depot sits on this node."""
    for city in getattr(game, "cities", []):
        if city.center_node is node:
            return city.id
    for depot in getattr(game, "depots", []):
        if depot.center_node is node:
            return depot.id
    return f"nd_{game.nodes.index(node)}" if node in game.nodes else "unknown"


# ---------------------------------------------------------------------------
# Client -> Server: deserialize incoming tick data and apply to local state
# ---------------------------------------------------------------------------


def apply_tick(data: dict, game) -> bool:
    """
    Apply a tick packet to the client's local game state.

    Returns True if applied cleanly, False if a desync gap was detected
    (caller should send a resync_request).
    """
    incoming_tick = data.get("tick", 0)
    game._last_tick = incoming_tick

    train_map = {t.id: t for t in game.trains}
    for entry in data.get("trains", []):
        train = train_map.get(entry["id"])
        if train:
            train._position = (entry["x"], entry["y"])
            train._network_angle = entry.get("angle", 0.0)

    car_map = {car.id: car for train in game.trains for car in train.cars}
    for entry in data.get("cars", []):
        car = car_map.get(entry["id"])
        if car:
            car._position = (entry["x"], entry["y"])
            car._network_angle = entry.get("angle", 0.0)

    game._remote_cursors = {c["id"]: c for c in data.get("cursors", [])}

    return True


def apply_map(data: dict, game):
    """
    Rebuild client-side game state from a map or resync packet.

    Creates lightweight Node, Edge, and stub Train/Car objects so the
    existing render stack methods work without modification.
    """
    from app.core.node_graph import Node, Edge
    from app.entities.line import Line

    # Clear existing client-side state
    game.nodes.clear()
    game.edges.clear()
    game.trains.clear()
    game.lines.clear()
    if hasattr(game, "cities"):
        game.cities.clear()
    if hasattr(game, "depots"):
        game.depots.clear()

    # Build id->Node map so tracks and lines can look up their endpoints
    node_by_id: dict[str, Node] = {}

    for city_data in data.get("cities", []):
        node = Node((city_data["x"], city_data["y"]))
        node.id = city_data["id"]
        game.nodes.append(node)
        node_by_id[city_data["id"]] = node
        city = _NetworkCity(
            city_data["id"],
            city_data.get("name", ""),
            node,
            city_data.get("rotation", 0),
        )
        node.reference = city
        game.cities.append(city)

    for depot_data in data.get("depots", []):
        node = Node((depot_data["x"], depot_data["y"]))
        node.id = depot_data["id"]
        game.nodes.append(node)
        node_by_id[depot_data["id"]] = node
        depot = _NetworkDepot(
            depot_data["id"],
            node,
            depot_data.get("owner_id"),
            depot_data.get("owner_color"),
        )
        node.reference = depot
        game.depots.append(depot)

    for track_data in data.get("tracks", []):
        # Create any endpoint nodes not already known (e.g. entry nodes)
        for side, xk, yk in (("station_a", "ax", "ay"), ("station_b", "bx", "by")):
            sid = track_data[side]
            if sid not in node_by_id and xk in track_data:
                node = Node((track_data[xk], track_data[yk]))
                node.id = sid
                game.nodes.append(node)
                node_by_id[sid] = node

        node_a = node_by_id.get(track_data["station_a"])
        node_b = node_by_id.get(track_data["station_b"])
        if node_a and node_b:
            edge = Edge(node_a, node_b)
            edge.id = track_data["id"]
            game.edges.append(edge)

    for line_data in data.get("lines", []):
        station_nodes = [
            node_by_id[sid]
            for sid in line_data.get("stations", [])
            if sid in node_by_id
        ]
        try:
            line = Line(
                None,
                station_nodes,
                owner_id=line_data.get("owner_id"),
                color=line_data.get("color"),
            )
        except Exception:
            line = Line(
                None,
                [],
                owner_id=line_data.get("owner_id"),
                color=line_data.get("color"),
            )
        line.id = line_data["id"]
        game.lines.append(line)

    for train_data in data.get("trains", []):
        stub = _NetworkTrain(
            train_data["id"],
            train_data.get("line_id"),
            train_data.get("owner_id"),
            train_data.get("owner_color"),
        )
        for car_id in train_data.get("cars", []):
            stub.cars.append(_NetworkCar(car_id, train_data.get("owner_color")))
        game.trains.append(stub)

    if "tick" in data:
        game._last_tick = data["tick"]

    train_map = {t.id: t for t in game.trains}
    for entry in data.get("train_positions", []):
        train = train_map.get(entry["id"])
        if train:
            train._position = (entry["x"], entry["y"])
            train._network_angle = entry.get("angle", 0.0)

    car_map = {car.id: car for t in game.trains for car in t.cars}
    for entry in data.get("car_positions", []):
        car = car_map.get(entry["id"])
        if car:
            car._position = (entry["x"], entry["y"])
            car._network_angle = entry.get("angle", 0.0)


def apply_delta(data: dict, game):
    """Apply a small world update without rebuilding the whole client map."""
    if "tick" in data:
        game._last_tick = data["tick"]

    msg_type = data.get("type")
    if msg_type == "track_add":
        _apply_track_add(data.get("track", {}), game)
    elif msg_type == "line_update":
        _apply_line_update(data.get("line", {}), game)
    elif msg_type == "train_add":
        _apply_train_add(data, game)
    elif msg_type == "economy_state":
        _apply_economy_state(data, game)


def _find_node_by_id(game, node_id: str):
    """Return the first node whose ID matches, or None."""
    return next((node for node in game.nodes if node.id == node_id), None)


def _apply_track_add(track_data: dict, game):
    """Add a new track edge to the client game state."""
    from app.core.node_graph import Node, Edge

    if not track_data or any(edge.id == track_data.get("id") for edge in game.edges):
        return

    endpoints = []
    for side, xk, yk in (("station_a", "ax", "ay"), ("station_b", "bx", "by")):
        node_id = track_data.get(side)
        node = _find_node_by_id(game, node_id)
        if node is None and xk in track_data and yk in track_data:
            node = Node((track_data[xk], track_data[yk]))
            node.id = node_id
            game.nodes.append(node)
        endpoints.append(node)

    node_a, node_b = endpoints
    if node_a is None or node_b is None:
        return

    edge = Edge(node_a, node_b)
    edge.id = track_data["id"]
    game.edges.append(edge)


def _apply_line_update(line_data: dict, game):
    """Create or update a line in the client game state."""
    from app.entities.line import Line

    if not line_data:
        return

    station_nodes = [
        node
        for station_id in line_data.get("stations", [])
        for node in [_find_node_by_id(game, station_id)]
        if node is not None
    ]
    line = next((line for line in game.lines if line.id == line_data.get("id")), None)
    if line is None:
        line = Line(
            None,
            station_nodes,
            owner_id=line_data.get("owner_id"),
            color=line_data.get("color"),
        )
        line.id = line_data["id"]
        game.lines.append(line)
        return

    line.owner_id = line_data.get("owner_id")
    line.color = tuple(line_data.get("color", getattr(line, "color", (255, 0, 0))))
    line._main_nodes = station_nodes
    line.calculate_navigation_path()


def _apply_train_add(data: dict, game):
    """Create or update a train stub in the client game state."""
    train_data = data.get("train", {})
    if not train_data:
        return

    train = next((train for train in game.trains if train.id == train_data.get("id")), None)
    if train is None:
        train = _NetworkTrain(
            train_data["id"],
            train_data.get("line_id"),
            train_data.get("owner_id"),
            train_data.get("owner_color"),
        )
        game.trains.append(train)
    else:
        train.line_id = train_data.get("line_id")
        train.owner_id = train_data.get("owner_id")
        train.owner_color = train_data.get("owner_color")

    existing_cars = {car.id: car for car in train.cars}
    train.cars = [
        existing_cars.get(car_id) or _NetworkCar(car_id, train_data.get("owner_color"))
        for car_id in train_data.get("cars", [])
    ]
    for car in train.cars:
        car.owner_color = train_data.get("owner_color")

    train_position = data.get("train_position")
    if train_position:
        train._position = (train_position["x"], train_position["y"])
        train._network_angle = train_position.get("angle", 0.0)

    car_map = {car.id: car for car in train.cars}
    for entry in data.get("car_positions", []):
        car = car_map.get(entry["id"])
        if car:
            car._position = (entry["x"], entry["y"])
            car._network_angle = entry.get("angle", 0.0)


def _apply_economy_state(data: dict, game):
    """Store the economy snapshot and update the local player's balance."""
    game.economy_state = data
    owner_id = data.get("owner_id") or getattr(getattr(game, "_local_player", None), "id", None)
    players = data.get("players", {})
    if owner_id in players and getattr(game, "_local_player", None) is not None:
        game._local_player._balance = players[owner_id].get(
            "balance", game._local_player._balance
        )
