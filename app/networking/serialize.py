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

    def __init__(self, train_id: str):
        from app.avatars.trains.test_train import TestTrain
        self.id = train_id
        self.owner = None
        self._position = None
        self._network_angle = 0.0
        self.avatar = TestTrain()
        self.cars: list = []

    def get_position(self):
        return self._position

    def get_angle(self) -> float:
        return self._network_angle


class _NetworkCar:
    """Minimal car stand-in on the client — holds position and avatar only."""

    def __init__(self, car_id: str):
        from app.avatars.train_cars.test_car import TestCar
        self.id = car_id
        self.owner = None
        self._position = None
        self._network_angle = 0.0
        self.avatar = TestCar()

    def get_position(self):
        return self._position

    def get_angle(self) -> float:
        return self._network_angle


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
        "trains": [_serialize_train_position(train) for train in game.trains],
        "cars": [
            _serialize_car_position(car)
            for train in game.trains
            for car in train.cars
        ],
        "cursors": cursors,
    }


def serialize_resync(game, tick: int) -> dict:
    """Full state resync — same shape as map but includes tick counter."""
    data = serialize_map(game)
    data["type"] = "resync"
    data["tick"] = tick
    data["trains"] = [_serialize_train_position(t) for t in game.trains]
    data["cars"] = [
        _serialize_car_position(car)
        for train in game.trains
        for car in train.cars
    ]
    return data


def serialize_reject(tick: int, action: str, reason: str) -> dict:
    return {"type": "reject", "tick": tick, "action": action, "reason": reason}


# ---------------------------------------------------------------------------
# Private helpers — individual object serialization
# ---------------------------------------------------------------------------

def _serialize_track(edge, game) -> dict:
    edge_id = getattr(edge, "id", None) or f"trk_{game.edges.index(edge)}"
    city_a = _find_station_id(edge.start, game)
    city_b = _find_station_id(edge.end, game)
    return {"id": edge_id, "station_a": city_a, "station_b": city_b}


def _serialize_city(city) -> dict:
    return {
        "id": city.id,
        "x": city._node.position[0],
        "y": city._node.position[1],
        "name": city._name,
    }


def _serialize_depot(depot) -> dict:
    return {
        "id": depot.id,
        "x": depot.center_node.position[0],
        "y": depot.center_node.position[1],
    }


def _serialize_line(line, game) -> dict:
    line_id = getattr(line, "id", f"ln_{game.lines.index(line)}")
    station_ids = [_find_station_id(node, game) for node in line._main_nodes]
    return {"id": line_id, "stations": station_ids}


def _serialize_train_static(train) -> dict:
    line_id = getattr(train.line, "id", None) if train.line else None
    return {
        "id": train.id,
        "line_id": line_id,
        "cars": [car.id for car in train.cars],
    }


def _serialize_train_position(train) -> dict:
    x, y = train.get_position()
    angle = train.location.angle if train.location else 0.0
    return {"id": train.id, "x": round(x, 2), "y": round(y, 2), "angle": round(angle, 4)}


def _serialize_car_position(car) -> dict:
    x, y = car.get_position()
    angle = car._location.angle if car._location else 0.0
    return {"id": car.id, "x": round(x, 2), "y": round(y, 2), "angle": round(angle, 4)}


def _find_station_id(node, game) -> str:
    """Return the ID of whichever city or depot sits on this node."""
    for city in getattr(game, "cities", []):
        if city._node is node:
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
    last_tick = getattr(game, "_last_tick", None)

    desync = last_tick is not None and incoming_tick != last_tick + 1
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

    game._remote_cursors = {c["id"]: (c["x"], c["y"]) for c in data.get("cursors", [])}

    return not desync


def apply_map(data: dict, game):
    """
    Rebuild client-side game state from a map or resync packet.

    Creates lightweight Node, Edge, and stub Train/Car objects so the
    existing render stack methods work without modification.
    """
    from app.core.node_graph import Node, Edge

    # Clear existing client-side state
    game.nodes.clear()
    game.edges.clear()
    game.trains.clear()

    # Build id->Node map so tracks can look up their endpoints
    node_by_id: dict[str, Node] = {}

    for city_data in data.get("cities", []):
        node = Node((city_data["x"], city_data["y"]))
        node.id = city_data["id"]
        game.nodes.append(node)
        node_by_id[city_data["id"]] = node

    for depot_data in data.get("depots", []):
        node = Node((depot_data["x"], depot_data["y"]))
        node.id = depot_data["id"]
        game.nodes.append(node)
        node_by_id[depot_data["id"]] = node

    for track_data in data.get("tracks", []):
        node_a = node_by_id.get(track_data["station_a"])
        node_b = node_by_id.get(track_data["station_b"])
        if node_a and node_b:
            edge = Edge(node_a, node_b)
            edge.id = track_data["id"]
            game.edges.append(edge)

    for train_data in data.get("trains", []):
        stub = _NetworkTrain(train_data["id"])
        for car_id in train_data.get("cars", []):
            stub.cars.append(_NetworkCar(car_id))
        game.trains.append(stub)

    if "tick" in data:
        game._last_tick = data["tick"]
