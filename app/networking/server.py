from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from websockets.asyncio.server import Server, ServerConnection, serve

from app.networking.serialize import serialize_map, serialize_tick, serialize_resync, serialize_reject

MessageHandler = Callable[[str, ServerConnection], Awaitable[Any] | Any]
ConnectionHandler = Callable[[ServerConnection], Awaitable[Any] | Any]

# How many ticks behind a client action is allowed to be before rejection
MAX_TICK_AGE = 60


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
        self.host = host
        self.port = port
        self._message_handler = message_handler
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._clients: set[ServerConnection] = set()
        self._client_ids: dict[ServerConnection, str] = {}
        self._client_acks: dict[str, int] = {}
        self._cursors: dict[str, dict] = {}
        self._server: Server | None = None
        self._tick: int = 0
        self._game = None
        self._tick_task: asyncio.Task | None = None

    def attach_game(self, game) -> None:
        """Attach the authoritative game instance to serialize and broadcast."""
        self._game = game

    async def start(self) -> None:
        if self._server is not None:
            raise RuntimeError("Server is already running.")
        self._server = await serve(self._handle_client, self.host, self.port)

    async def stop(self) -> None:
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
        if self._server is None:
            raise RuntimeError("Server is not running.")
        await self._server.wait_closed()

    async def start_tick_loop(self, ticks_per_second: int = 20) -> None:
        """Begin broadcasting tick state at the given rate."""
        self._tick_task = asyncio.create_task(self._tick_loop(ticks_per_second))

    async def _tick_loop(self, ticks_per_second: int) -> None:
        interval = 1 / ticks_per_second
        while True:
            await asyncio.sleep(interval)
            if self._game is not None and self._clients:
                cursors = list(self._cursors.values())
                packet = serialize_tick(self._game, self._tick, cursors)
                await self.broadcast(json.dumps(packet))
            self._tick += 1

    async def send_to(self, client: ServerConnection, message: str) -> None:
        await client.send(message)

    async def broadcast(self, message: str) -> None:
        if not self._clients:
            return
        await asyncio.gather(
            *(client.send(message) for client in tuple(self._clients)),
            return_exceptions=False,
        )

    async def broadcast_except(self, message: str, exclude: ServerConnection) -> None:
        targets = [c for c in self._clients if c is not exclude]
        if not targets:
            return
        await asyncio.gather(
            *(c.send(message) for c in targets),
            return_exceptions=False,
        )

    def get_lag_report(self) -> dict[str, int]:
        """Return how many ticks behind each client is, keyed by client ID."""
        return {cid: self._tick - ack for cid, ack in self._client_acks.items()}

    async def _handle_client(self, websocket: ServerConnection) -> None:
        cid = str(uuid.uuid4())
        self._clients.add(websocket)
        self._client_ids[websocket] = cid
        self._client_acks[cid] = self._tick

        await websocket.send(json.dumps({"type": "id", "id": cid}))

        if self._game is not None:
            await websocket.send(json.dumps(serialize_map(self._game)))

        if self._on_connect is not None:
            result = self._on_connect(websocket)
            if asyncio.iscoroutine(result):
                await result

        try:
            async for message in websocket:
                await self._route_message(message, websocket, cid)
        finally:
            self._clients.discard(websocket)
            self._client_ids.pop(websocket, None)
            self._client_acks.pop(cid, None)
            self._cursors.pop(cid, None)
            await self.broadcast(json.dumps({"type": "leave", "id": cid}))
            if self._on_disconnect is not None:
                result = self._on_disconnect(websocket)
                if asyncio.iscoroutine(result):
                    await result

    async def _route_message(self, message: str, sender: ServerConnection, cid: str) -> None:
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
                "color": data.get("color", [255, 255, 0]),
            }
            return

        # Reject actions that are too old
        if self._tick - msg_tick > MAX_TICK_AGE:
            reject = serialize_reject(self._tick, msg_type, "tick too old")
            await sender.send(json.dumps(reject))
            return

        if self._message_handler is not None:
            result = self._message_handler(data, sender, cid)
            if asyncio.iscoroutine(result):
                await result


if __name__ == "__main__":
    import socket
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from app.game import Game

    def _get_local_ip() -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]

    def _setup_headless_map(game) -> None:
        """Populate the server's initial world with a depot and cities."""
        game.place_new_depot(None, (100, 100))
        game.place_new_city((500, 50))
        game.place_new_city((800, 150))
        game.place_new_city((1200, 120))

    async def _main() -> None:
        # --- game setup (headless — no pygame init, no window) ---
        import os
        import pygame
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.init()
        pygame.display.set_mode((1, 1))

        game = Game(headless=True)
        _setup_headless_map(game)

        async def on_message(data: dict, sender: ServerConnection, cid: str) -> None:
            msg_type = data.get("type")
            if msg_type == "place_track":
                start_node = next((n for n in game.nodes if n.id == data["station_a"]), None)
                if start_node is None:
                    print(f"[server] place_track: unknown node id {data.get('station_a')!r}")
                elif "station_b" in data:
                    end_node = next((n for n in game.nodes if n.id == data["station_b"]), None)
                    if end_node:
                        game.place_new_edge(start_node, end_node=end_node)
                else:
                    game.place_new_edge(start_node, (data["x"], data["y"]))
            elif msg_type == "place_city":
                game.place_new_city((data["x"], data["y"]))
            elif msg_type == "buy_train":
                depot = next((d for d in game.depots if d.id == data["depot_id"]), None)
                if depot:
                    game.add_test_train()
            elif msg_type == "assign_train":
                tid, lid = data.get("train_id"), data.get("line_id")
                train = game.trains[-1] if tid == "latest" else next((t for t in game.trains if t.id == tid), None)
                line = game.lines[-1] if lid == "latest" else next((l for l in game.lines if l.id == lid), None)
                if train and line:
                    train.assign_to_line(line)
            elif msg_type == "create_line":
                game.make_new_line([])
            elif msg_type == "toggle_station":
                node = next((n for n in game.nodes if n.id == data.get("node_id")), None)
                if node and game.lines:
                    game.lines[-1].toggle_station(node)
            else:
                print(f"[server] {cid[:8]} -> unhandled action: {msg_type}")

        local_ip = _get_local_ip()
        server = WebSocketServer(host="0.0.0.0", message_handler=on_message)
        server.attach_game(game)
        await server.start()
        await server.start_tick_loop(ticks_per_second=20)
        print(f"[server] listening on ws://{local_ip}:8765 — Ctrl+C to stop")

        # --- headless simulation loop at 60 fps ---
        dt = 1 / 60
        lag_report_interval = int(60 * 10)  # every 10 seconds at 60 fps
        frame = 0
        while True:
            for train in game.trains:
                train.tick(dt)
            frame += 1
            if frame % lag_report_interval == 0:
                lag = server.get_lag_report()
                if lag:
                    entries = ", ".join(f"{cid[:8]}={ticks}t" for cid, ticks in lag.items())
                    print(f"[server] lag report — {entries}")
            await asyncio.sleep(dt)

    asyncio.run(_main())
