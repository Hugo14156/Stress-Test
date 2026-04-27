from __future__ import annotations

import asyncio
import json
import os
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from websockets.asyncio.server import Server, ServerConnection, serve

from app.networking.serialize import (
    serialize_map,
    serialize_tick,
    serialize_resync,
    serialize_reject,
    serialize_economy_state,
    serialize_train_add,
    serialize_track_add,
    serialize_line_update,
)
from app.core.constants import (
    STARTING_CASH,
    TRACK_COST_PER_UNIT,
    TRAIN_COSTS,
    MAINTENANCE_COST,
)
from app.core.stock_market import Stock

MessageHandler = Callable[[str, ServerConnection], Awaitable[Any] | Any]
ConnectionHandler = Callable[[ServerConnection], Awaitable[Any] | Any]

# How many ticks behind a client action is allowed to be before rejection
MAX_TICK_AGE = 60
DISCOVERY_PORT = 8766
DISCOVERY_MESSAGE = "stress-test-discovery-v1"
DEBUG_NETWORK = os.environ.get("STRESS_TEST_DEBUG", "1") != "0"

CURSOR_COLORS = [
    [255, 80, 80],
    [80, 180, 255],
    [90, 220, 120],
    [255, 210, 80],
    [210, 120, 255],
    [255, 140, 70],
]


def _log(event: str, message: str, *, debug: bool = True) -> None:
    """Conditionally print a labeled debug message to stdout."""
    if debug and not DEBUG_NETWORK:
        return
    print(f"[server][{event}] {message}")


class ServerEconomy:
    def __init__(self) -> None:
        """Initialise an empty economy with no registered players."""
        self.players: dict[str, dict] = {}
        self._order: list[str] = []
        self.stock_market = Stock([])
        self.revision = 0

    def register_player(self, cid: str, name: str = "", color=None) -> None:
        """Add a new player to the economy and stock market."""
        if cid in self.players:
            return
        self._order.append(cid)
        index = len(self._order) - 1
        self.players[cid] = {
            "id": cid,
            "name": name or cid[:8],
            "color": color,
            "stock_index": index,
            "balance": STARTING_CASH,
            "net_worth": STARTING_CASH,
            "track_spend": 0,
            "train_spend": 0,
            "maintenance_spend": 0,
            "income": 0,
        }
        self._rebuild_stock_market()
        self.revision += 1

    def unregister_player(self, cid: str) -> None:
        """Mark a player as disconnected without removing their ledger entry."""
        # Keep departed players in the ledger so stock indices remain stable.
        if cid in self.players:
            self.players[cid]["connected"] = False
            self.revision += 1

    def charge(self, cid: str, amount: float, category: str = "spend") -> bool:
        """Deduct amount from the player's balance; return False if funds are insufficient."""
        player = self.players.get(cid)
        if player is None or player["balance"] < amount:
            return False
        player["balance"] -= amount
        player["net_worth"] -= amount
        if category == "track":
            player["track_spend"] += amount
        elif category == "train":
            player["train_spend"] += amount
        elif category == "maintenance":
            player["maintenance_spend"] += amount
        self._sync_stock_finances()
        self.revision += 1
        return True

    def credit(self, cid: str, amount: float) -> None:
        """Add revenue to a player's balance and net worth."""
        player = self.players.get(cid)
        if player is None:
            return
        player["balance"] += amount
        player["net_worth"] += amount
        player["income"] += amount
        self._sync_stock_finances()
        self.revision += 1

    def buy_stock(self, buyer_id: str, target_id: str, quantity: int) -> None:
        """Execute a stock purchase between two registered players."""
        buyer = self.players[buyer_id]["stock_index"]
        target = self.players[target_id]["stock_index"]
        self.stock_market.buy_stock(buyer, target, quantity)
        self._pull_stock_finances()
        self.revision += 1

    def players_public(self) -> dict:
        """Return a public-safe dict of all player records keyed by player ID."""
        return {
            cid: {
                "id": cid,
                "name": player["name"],
                "color": player["color"],
                "stock_index": player["stock_index"],
                "balance": round(player["balance"], 2),
                "net_worth": round(player["net_worth"], 2),
                "connected": player.get("connected", True),
            }
            for cid, player in self.players.items()
        }

    def stocks_public(self) -> dict:
        """Return current stock prices and the ownership matrix."""
        prices = self.stock_market.set_prices()
        return {
            "prices": {
                cid: round(prices[player["stock_index"]], 2)
                for cid, player in self.players.items()
            },
            "ownership": self.stock_market.ownership,
        }

    def _rebuild_stock_market(self) -> None:
        """Reconstruct the Stock model after a new player joins."""
        old_order = list(self._order)
        old_ownership = getattr(self.stock_market, "ownership", [])
        finances = [
            [self.players[cid]["net_worth"], self.players[cid]["balance"]]
            for cid in self._order
        ]
        ownership = [
            [50 if row == col else 0 for col in range(len(self._order))]
            for row in range(len(self._order))
        ]
        for old_row, _ in enumerate(old_order[:-1]):
            for old_col, _ in enumerate(old_order[:-1]):
                if old_row < len(old_ownership) and old_col < len(old_ownership[old_row]):
                    ownership[old_row][old_col] = old_ownership[old_row][old_col]
        self.stock_market = Stock(finances, ownership)

    def _sync_stock_finances(self) -> None:
        """Push current balance and net-worth into the stock model."""
        for cid in self._order:
            index = self.players[cid]["stock_index"]
            self.stock_market.net_worth[index] = self.players[cid]["net_worth"]
            self.stock_market.cash[index] = self.players[cid]["balance"]

    def _pull_stock_finances(self) -> None:
        """Pull updated balance and net-worth from the stock model back into player records."""
        for cid in self._order:
            index = self.players[cid]["stock_index"]
            self.players[cid]["net_worth"] = self.stock_market.net_worth[index]
            self.players[cid]["balance"] = self.stock_market.cash[index]


class WebSocketServer:
    """WebSocket server that drives the authoritative game simulation.

    Broadcasts tick state to all clients at a fixed rate, handles incoming
    client actions, and tracks per-client lag via ack messages.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765,
        message_handler: MessageHandler | None = None,
        on_connect: ConnectionHandler | None = None,
        on_disconnect: ConnectionHandler | None = None,
    ) -> None:
        """Initialise the server with host, port, and optional lifecycle callbacks."""
        self.host = host
        self.port = port
        self._message_handler = message_handler
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._clients: set[ServerConnection] = set()
        self._client_ids: dict[ServerConnection, str] = {}
        self._client_acks: dict[str, int] = {}
        self._client_colors: dict[str, list[int]] = {}
        self._cursors: dict[str, dict] = {}
        self._server: Server | None = None
        self._tick: int = 0
        self._game = None
        self._tick_task: asyncio.Task | None = None

    def attach_game(self, game) -> None:
        """Attach the authoritative game instance to serialize and broadcast."""
        self._game = game

    async def start(self) -> None:
        """Begin accepting WebSocket connections."""
        if self._server is not None:
            raise RuntimeError("Server is already running.")
        self._server = await serve(
            self._handle_client,
            self.host,
            self.port,
            compression=None,
        )

    async def stop(self) -> None:
        """Stop the server, cancel the tick loop, and clear all client state."""
        if self._server is None:
            raise RuntimeError("Server is not running.")
        if self._tick_task is not None:
            self._tick_task.cancel()
            self._tick_task = None
        self._server.close()
        await self._server.wait_closed()
        self._server = None
        self._clients.clear()

    async def wait_closed(self) -> None:
        """Block until the server has fully shut down."""
        if self._server is None:
            raise RuntimeError("Server is not running.")
        await self._server.wait_closed()

    async def start_tick_loop(self, ticks_per_second: int = 20) -> None:
        """Begin broadcasting tick state at the given rate."""
        self._tick_task = asyncio.create_task(self._tick_loop(ticks_per_second))

    async def _tick_loop(self, ticks_per_second: int) -> None:
        """Broadcast serialized tick state to all clients at the given rate."""
        interval = 1 / ticks_per_second
        while True:
            await asyncio.sleep(interval)
            if self._game is not None and self._clients:
                cursors = list(self._cursors.values())
                packet = serialize_tick(self._game, self._tick, cursors)
                await self.broadcast(json.dumps(packet))
            self._tick += 1

    async def send_to(self, client: ServerConnection, message: str) -> None:
        """Send a message to a single client, removing it on failure."""
        try:
            await client.send(message)
        except Exception:
            self._clients.discard(client)

    async def broadcast(self, message: str) -> None:
        """Send a message to every connected client concurrently."""
        if not self._clients:
            return
        await asyncio.gather(
            *(client.send(message) for client in tuple(self._clients)),
            return_exceptions=True,
        )

    async def broadcast_except(self, message: str, exclude: ServerConnection) -> None:
        """Send a message to all clients except the specified one."""
        targets = [c for c in self._clients if c is not exclude]
        if not targets:
            return
        await asyncio.gather(
            *(c.send(message) for c in targets),
            return_exceptions=True,
        )

    def get_lag_report(self) -> dict[str, int]:
        """Return how many ticks behind each client is, keyed by client ID."""
        return {cid: self._tick - ack for cid, ack in self._client_acks.items()}

    async def _handle_client(self, websocket: ServerConnection) -> None:
        """Manage the full lifecycle of a single client connection."""
        cid = str(uuid.uuid4())
        self._clients.add(websocket)
        self._client_ids[websocket] = cid
        self._client_acks[cid] = self._tick
        self._client_colors[cid] = CURSOR_COLORS[
            (len(self._client_colors)) % len(CURSOR_COLORS)
        ]
        _log("connect", f"{cid[:8]} color={self._client_colors[cid]}")

        await websocket.send(
            json.dumps({"type": "id", "id": cid, "color": self._client_colors[cid]})
        )

        # on_connect runs first so it can modify game state before the map is sent
        if self._on_connect is not None:
            result = self._on_connect(websocket)
            if asyncio.iscoroutine(result):
                await result

        if self._game is not None:
            await websocket.send(json.dumps(serialize_map(self._game)))

        try:
            async for message in websocket:
                await self._route_message(message, websocket, cid)
        finally:
            if self._on_disconnect is not None:
                result = self._on_disconnect(websocket)
                if asyncio.iscoroutine(result):
                    await result
            self._clients.discard(websocket)
            self._client_ids.pop(websocket, None)
            self._client_acks.pop(cid, None)
            self._client_colors.pop(cid, None)
            self._cursors.pop(cid, None)
            _log("disconnect", cid[:8])
            await self.broadcast(json.dumps({"type": "leave", "id": cid}))

    async def _route_message(self, message: str, sender: ServerConnection, cid: str) -> None:
        """Dispatch an incoming client message to ack, resync, cursor, or action handlers."""
        data = json.loads(message)
        msg_type = data.get("type")
        msg_tick = data.get("tick", self._tick)

        if msg_type == "ack":
            self._client_acks[cid] = msg_tick
            return

        if msg_type == "resync":
            if self._game is not None:
                packet = serialize_resync(self._game, self._tick)
                await sender.send(json.dumps(packet))
            return

        if msg_type == "cursor":
            self._cursors[cid] = {
                "id": cid,
                "x": data["x"],
                "y": data["y"],
                "name": data.get("name", ""),
                "color": self._client_colors.get(cid, [255, 255, 0]),
            }
            return

        # Reject actions that are too old
        if self._tick - msg_tick > MAX_TICK_AGE:
            reject = serialize_reject(self._tick, msg_type, "tick too old")
            await sender.send(json.dumps(reject))
            return

        if self._message_handler is not None:
            try:
                result = self._message_handler(data, sender, cid)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:
                _log("reject", f"{cid[:8]} {msg_type}: {exc}", debug=False)
                reject = serialize_reject(self._tick, msg_type, str(exc))
                await self.send_to(sender, json.dumps(reject))


if __name__ == "__main__":
    import math
    import random
    import socket
    import sys
    import threading
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from app.game import Game

    def _get_local_ip() -> str:
        """Return this machine's LAN IP address."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except OSError:
            return socket.gethostbyname(socket.gethostname())

    def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
        """Euclidean distance between two (x, y) points."""
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _pick_position(
        rng: random.Random,
        existing: list[tuple[float, float]],
        *,
        bounds: tuple[int, int, int, int],
        min_distance: float,
        attempts: int = 250,
        fallback_index: int = 0,
    ) -> tuple[int, int]:
        """Pick a random position at least min_distance from all existing positions."""
        min_x, max_x, min_y, max_y = bounds
        for _ in range(attempts):
            pos = (rng.randint(min_x, max_x), rng.randint(min_y, max_y))
            if all(_distance(pos, other) >= min_distance for other in existing):
                return pos

        fallback_positions = [
            (min_x, min_y),
            (max_x, min_y),
            (min_x, max_y),
            (max_x, max_y),
            ((min_x + max_x) // 2, min_y),
            ((min_x + max_x) // 2, max_y),
            (min_x, (min_y + max_y) // 2),
            (max_x, (min_y + max_y) // 2),
        ]
        return fallback_positions[fallback_index % len(fallback_positions)]

    def _setup_headless_map(game, rng: random.Random) -> list[tuple[int, int]]:
        """Populate the server's initial multiplayer world with random cities."""
        city_positions: list[tuple[int, int]] = []
        city_count = rng.randint(15, 20)
        for index in range(city_count):
            pos = _pick_position(
                rng,
                city_positions,
                bounds=(300, 3200, 120, 1900),
                min_distance=320,
                fallback_index=index,
            )
            city_positions.append(pos)
            rotation = rng.randrange(0, 360)
            game.place_new_city(pos, rotation=rotation)
            _log(
                "world",
                f"city {index + 1}/{city_count} at {pos} rotation={rotation}",
            )
        return city_positions

    def _pick_depot_position(
        rng: random.Random,
        game,
        city_positions: list[tuple[int, int]],
        player_index: int,
    ) -> tuple[int, int]:
        """Pick a starting depot position far from existing depots and cities."""
        depot_positions = [depot.center_node.position for depot in game.depots]
        blockers = list(depot_positions)
        soft_blockers = city_positions
        bounds = (180, 3400, 160, 2100)
        for _ in range(300):
            pos = (
                rng.randint(bounds[0], bounds[1]),
                rng.randint(bounds[2], bounds[3]),
            )
            far_from_depots = all(_distance(pos, other) >= 520 for other in blockers)
            far_from_cities = all(_distance(pos, other) >= 260 for other in soft_blockers)
            if far_from_depots and far_from_cities:
                return pos

        return _pick_position(
            rng,
            blockers,
            bounds=bounds,
            min_distance=420,
            fallback_index=player_index,
        )

    def _start_discovery_responder(server, local_ip: str, world_seed: int) -> None:
        """Start a background UDP thread that answers LAN discovery broadcasts."""
        def _run() -> None:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(("", DISCOVERY_PORT))
                    _log(
                        "discovery",
                        f"listening on udp://0.0.0.0:{DISCOVERY_PORT}",
                        debug=False,
                    )
                    while True:
                        data, address = sock.recvfrom(1024)
                        if data.decode("utf-8", errors="ignore") != DISCOVERY_MESSAGE:
                            continue
                        payload = {
                            "type": "stress_test_server",
                            "host": local_ip,
                            "port": server.port,
                            "players": len(server._clients),
                            "seed": world_seed,
                        }
                        sock.sendto(json.dumps(payload).encode("utf-8"), address)
            except OSError as exc:
                _log("discovery", f"unavailable: {exc}", debug=False)

        threading.Thread(target=_run, daemon=True).start()

    async def _main() -> None:
        """Set up the headless server, game world, and run the simulation loop."""
        # --- game setup (headless — no pygame init, no window) ---
        import os
        import pygame
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.init()
        pygame.display.set_mode((1, 1))

        world_seed = random.randrange(1_000_000_000)
        rng = random.Random(world_seed)
        _log("world", f"seed={world_seed}", debug=False)

        game = Game(headless=True)
        economy = ServerEconomy()
        game.economy = economy
        city_positions = _setup_headless_map(game, rng)

        _player_count = 0

        async def on_connect(websocket: ServerConnection) -> None:
            """Register a player, place their depot, and notify existing clients."""
            nonlocal _player_count
            owner_id = server._client_ids[websocket]
            economy.register_player(
                owner_id,
                name=owner_id[:8],
                color=server._client_colors[owner_id],
            )
            pos = _pick_depot_position(rng, game, city_positions, _player_count)
            depot = game.place_new_depot(
                None,
                pos,
                owner_id=owner_id,
                owner_color=server._client_colors[owner_id],
            )
            _log(
                "connect",
                f"{owner_id[:8]} depot={depot.id} pos={pos} color={server._client_colors[owner_id]}",
                debug=False,
            )
            _player_count += 1
            # Notify already-connected clients of the new depot
            await server.broadcast_except(
                json.dumps(serialize_resync(game, server._tick)), websocket
            )
            await broadcast_economy()

        async def on_disconnect(websocket: ServerConnection) -> None:
            """Unregister the player and broadcast the updated economy."""
            cid = server._client_ids.get(websocket)
            if cid is not None:
                economy.unregister_player(cid)
                await broadcast_economy()

        async def send_economy(websocket: ServerConnection) -> None:
            """Send the current economy state to a single client."""
            cid = server._client_ids.get(websocket)
            await server.send_to(
                websocket,
                json.dumps(serialize_economy_state(economy, server._tick, cid)),
            )

        async def broadcast_economy() -> None:
            """Send the current economy state to all connected clients."""
            for websocket in tuple(server._clients):
                await send_economy(websocket)

        def latest_owned_line(owner_id: str):
            """Return the most recently created line owned by owner_id."""
            return next(
                (
                    line
                    for line in reversed(game.lines)
                    if getattr(line, "owner_id", None) == owner_id
                ),
                None,
            )

        async def on_message(data: dict, sender: ServerConnection, cid: str) -> None:
            """Handle all client action messages and broadcast resulting state changes."""
            msg_type = data.get("type")
            packet = None
            if msg_type == "place_track":
                start_node = next((n for n in game.nodes if n.id == data["station_a"]), None)
                if start_node is None:
                    _log(
                        "reject",
                        f"place_track unknown node id {data.get('station_a')!r}",
                        debug=False,
                    )
                elif "station_b" in data:
                    end_node = next((n for n in game.nodes if n.id == data["station_b"]), None)
                    if end_node:
                        length = _distance(start_node.position, end_node.position)
                        cost = TRACK_COST_PER_UNIT * length
                        if not economy.charge(cid, cost, "track"):
                            await server.send_to(
                                sender,
                                json.dumps(
                                    serialize_reject(
                                        server._tick,
                                        msg_type,
                                        f"not enough money for track (${cost:.0f})",
                                    )
                                ),
                            )
                            return
                        edge, _ = game.place_new_edge(start_node, end_node=end_node)
                        packet = serialize_track_add(edge, game, server._tick)
                        _log("track", f"{cid[:8]} {edge.id} existing endpoints")
                else:
                    end_pos = (data["x"], data["y"])
                    length = _distance(start_node.position, end_pos)
                    cost = TRACK_COST_PER_UNIT * length
                    if not economy.charge(cid, cost, "track"):
                        await server.send_to(
                            sender,
                            json.dumps(
                                serialize_reject(
                                    server._tick,
                                    msg_type,
                                    f"not enough money for track (${cost:.0f})",
                                )
                            ),
                        )
                        return
                    edge, _ = game.place_new_edge(start_node, (data["x"], data["y"]))
                    packet = serialize_track_add(edge, game, server._tick)
                    _log("track", f"{cid[:8]} {edge.id} new endpoint")
            elif msg_type == "place_city":
                rotation = rng.randrange(0, 360)
                game.place_new_city((data["x"], data["y"]), rotation=rotation)
                packet = serialize_resync(game, server._tick)
                _log(
                    "world",
                    f"{cid[:8]} placed city at {(data['x'], data['y'])} rotation={rotation}",
                )
            elif msg_type == "buy_train":
                depot = next((d for d in game.depots if d.id == data["depot_id"]), None)
                if depot is None:
                    _log("reject", f"{cid[:8]} buy_train unknown depot", debug=False)
                    await server.send_to(
                        sender,
                        json.dumps(
                            serialize_reject(server._tick, msg_type, "unknown depot")
                        ),
                    )
                    return
                if getattr(depot, "owner_id", None) != cid:
                    _log(
                        "reject",
                        f"{cid[:8]} buy_train depot belongs to {getattr(depot, 'owner_id', None)}",
                        debug=False,
                    )
                    await server.send_to(
                        sender,
                        json.dumps(
                            serialize_reject(
                                server._tick, msg_type, "depot belongs to another player"
                            )
                        ),
                    )
                    return
                train_type = data.get("train_type", "EMD_E9")
                train_cost = TRAIN_COSTS.get(train_type)
                if train_cost is None:
                    await server.send_to(
                        sender,
                        json.dumps(
                            serialize_reject(server._tick, msg_type, "unknown train type")
                        ),
                    )
                    return
                if not economy.charge(cid, train_cost, "train"):
                    await server.send_to(
                        sender,
                        json.dumps(
                            serialize_reject(
                                server._tick,
                                msg_type,
                                f"not enough money for train (${train_cost:.0f})",
                            )
                        ),
                    )
                    return
                train = game.add_test_train(depot)
                if train:
                    train.owner_id = cid
                    train.owner_color = server._client_colors.get(cid)
                    line = latest_owned_line(cid)
                    if line is None:
                        _log("train", f"{cid[:8]} {train.id} parked: no owned line")
                        await server.send_to(
                            sender,
                            json.dumps(
                                serialize_reject(
                                    server._tick, msg_type, "no owned line to assign train"
                                )
                            ),
                        )
                    elif not line.stations:
                        _log("train", f"{cid[:8]} {train.id} parked: empty line {line.id}")
                        await server.send_to(
                            sender,
                            json.dumps(
                                serialize_reject(
                                    server._tick, msg_type, "owned line has no stations"
                                )
                            ),
                        )
                    else:
                        try:
                            train.assign_to_line(line)
                            _log(
                                "train",
                                f"{cid[:8]} {train.id} assigned to {line.id}",
                                debug=False,
                            )
                        except ValueError as exc:
                            _log(
                                "reject",
                                f"{cid[:8]} train cannot reach line {line.id}: {exc}",
                                debug=False,
                            )
                            await server.send_to(
                                sender,
                                json.dumps(
                                    serialize_reject(
                                        server._tick,
                                        msg_type,
                                        f"train cannot reach line: {exc}",
                                    )
                                ),
                            )
                    packet = serialize_train_add(train, server._tick)
            elif msg_type == "assign_train":
                tid, lid = data.get("train_id"), data.get("line_id")
                train = (
                    game.trains[-1]
                    if tid == "latest" and game.trains
                    else next((t for t in game.trains if t.id == tid), None)
                )
                line = latest_owned_line(cid) if lid == "latest" else next(
                    (
                        l
                        for l in game.lines
                        if l.id == lid and getattr(l, "owner_id", None) == cid
                    ),
                    None,
                )
                if train and line and line.stations:
                    try:
                        train.assign_to_line(line)
                    except ValueError as exc:
                        reason = f"train cannot reach line: {exc}"
                        await server.send_to(
                            sender,
                            json.dumps(serialize_reject(server._tick, msg_type, reason)),
                        )
                        return
                    packet = serialize_resync(game, server._tick)
                    _log("train", f"{cid[:8]} assigned {train.id} to {line.id}")
            elif msg_type == "create_line":
                game.make_new_line([], owner_id=cid)
                packet = serialize_line_update(game.lines[-1], game, server._tick)
                _log("line", f"{cid[:8]} created {game.lines[-1].id}")
            elif msg_type == "toggle_station":
                node = next((n for n in game.nodes if n.id == data.get("node_id")), None)
                line = latest_owned_line(cid)
                if node and line:
                    line.toggle_station(node)
                    packet = serialize_line_update(line, game, server._tick)
                    _log("line", f"{cid[:8]} toggled {node.id} on {line.id}")
            elif msg_type == "buy_stock":
                target_id = data.get("target_id")
                quantity = int(data.get("quantity", 0))
                if target_id not in economy.players:
                    await server.send_to(
                        sender,
                        json.dumps(serialize_reject(server._tick, msg_type, "unknown stock target")),
                    )
                    return
                if quantity <= 0:
                    await server.send_to(
                        sender,
                        json.dumps(serialize_reject(server._tick, msg_type, "quantity must be positive")),
                    )
                    return
                try:
                    economy.buy_stock(cid, target_id, quantity)
                except ValueError as exc:
                    await server.send_to(
                        sender,
                        json.dumps(serialize_reject(server._tick, msg_type, str(exc))),
                    )
                    return
                await broadcast_economy()
            else:
                _log("action", f"{cid[:8]} unhandled action: {msg_type}", debug=False)
                return

            if packet is not None:
                await server.broadcast(json.dumps(packet))
            if msg_type in ("place_track", "buy_train"):
                await broadcast_economy()

        local_ip = _get_local_ip()
        server = WebSocketServer(
            host="0.0.0.0",
            message_handler=on_message,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
        )
        server.attach_game(game)
        await server.start()
        await server.start_tick_loop(ticks_per_second=30)
        _start_discovery_responder(server, local_ip, world_seed)
        print(f"[server] listening on ws://{local_ip}:8765 — Ctrl+C to stop")

        # --- headless simulation loop at 60 fps ---
        dt = 1 / 60
        lag_report_interval = int(60 * 10)  # every 10 seconds at 60 fps
        frame = 0
        last_economy_revision = economy.revision
        while True:
            for train in game.trains:
                train.tick(dt)
            for city in game.cities:
                city.tick(dt)
            if economy.revision != last_economy_revision:
                await broadcast_economy()
                last_economy_revision = economy.revision
            frame += 1
            if frame % lag_report_interval == 0:
                lag = server.get_lag_report()
                if lag:
                    entries = ", ".join(f"{cid[:8]}={ticks}t" for cid, ticks in lag.items())
                    _log("lag", entries, debug=False)
            await asyncio.sleep(dt)

    asyncio.run(_main())
