"""
Serialization and deserialization for network packets.

Converts live game objects into JSON-ready dicts (for sending) and applies
incoming dicts back onto game state (for receiving). All coordinates are
world-space. Entity IDs are always assigned by the server, never the client.
"""

import math


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
        "id": getattr(depot, "id", "dep_0"),
        "x": depot._position[0],
        "y": depot._position[1],
    }


def _serialize_line(line, game) -> dict:
    line_id = getattr(line, "id", f"ln_{game.lines.index(line)}")
    station_ids = [_find_station_id(node, game) for node in line._main_nodes]
    return {"id": line_id, "stations": station_ids}


def _serialize_train_static(train) -> dict:
    line_id = getattr(train.line, "id", None) if train.line else None
    return {"id": train.id, "line_id": line_id}


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
        if depot._node is node:
            return getattr(depot, "id", "dep_0")
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
    Rebuild static game state from a map or resync packet.

    Does not reconstruct full simulation objects — only stores the raw
    data needed for client-side rendering. Full reconstruction requires
    avatar/asset lookup which is handled by the caller.
    """
    game._network_tracks = data.get("tracks", [])
    game._network_cities = data.get("cities", [])
    game._network_depots = data.get("depots", [])
    game._network_lines = data.get("lines", [])
    game._network_trains = data.get("trains", [])
    if "tick" in data:
        game._last_tick = data["tick"]
