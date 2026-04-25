from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from websockets.asyncio.client import ClientConnection, connect

from app.networking.serialize import apply_tick, apply_map

MessageHandler = Callable[[str], Awaitable[Any] | Any]

# Send an ack every N ticks received
ACK_INTERVAL = 10


class WebSocketClient:
    """WebSocket client that receives server tick state and sends player actions.

    Applies incoming tick and map packets directly onto the attached game
    object. Detects desync gaps and automatically requests a resync.
    """

    def __init__(self, uri: str, message_handler: MessageHandler | None = None) -> None:
        self.uri = uri
        self._connection: ClientConnection | None = None
        self._message_handler = message_handler
        self._listener_task: asyncio.Task[None] | None = None
        self._game = None
        self._own_id: str | None = None
        self._ticks_received: int = 0

    def attach_game(self, game) -> None:
        """Attach the local game instance that incoming state will be applied to."""
        self._game = game

    @property
    def own_id(self) -> str | None:
        return self._own_id

    async def connect(self) -> None:
        if self._connection is not None:
            raise RuntimeError("Client is already connected.")
        self._connection = await connect(self.uri)

    async def disconnect(self) -> None:
        if self._connection is None:
            raise RuntimeError("Client is not connected.")
        if self._listener_task is not None:
            self._listener_task.cancel()
            self._listener_task = None
        await self._connection.close()
        self._connection = None

    async def listen(self) -> None:
        """Start a background task that handles every incoming message."""
        if self._connection is None:
            raise RuntimeError("Client is not connected.")
        if self._listener_task is not None:
            raise RuntimeError("Listener is already running.")
        self._listener_task = asyncio.create_task(self._receive_loop())

    async def _receive_loop(self) -> None:
        async for message in self._connection:
            await self._route_message(str(message))

    async def _route_message(self, message: str) -> None:
        data = json.loads(message)
        msg_type = data.get("type")

        if msg_type == "id":
            self._own_id = data["id"]

        elif msg_type in ("map", "resync"):
            if self._game is not None:
                apply_map(data, self._game)

        elif msg_type == "tick":
            if self._game is not None:
                clean = apply_tick(data, self._game)
                if not clean:
                    print(f"[client] desync detected at tick {data.get('tick')} — requesting resync")
                    await self._request_resync(data.get("tick", 0) - 1)

            self._ticks_received += 1
            if self._ticks_received % ACK_INTERVAL == 0:
                await self._send_ack(data.get("tick", 0))

        elif msg_type == "reject":
            print(f"[client] action rejected: {data.get('action')} — {data.get('reason')}")

        elif msg_type == "leave":
            if self._game is not None:
                cursors = getattr(self._game, "_remote_cursors", {})
                cursors.pop(data.get("id"), None)

        if self._message_handler is not None:
            result = self._message_handler(message)
            if asyncio.iscoroutine(result):
                await result

    async def send(self, message: str) -> None:
        if self._connection is None:
            raise RuntimeError("Client is not connected.")
        await self._connection.send(message)

    async def send_action(self, action: dict) -> None:
        """Send a client action packet. Caller is responsible for setting 'tick'."""
        await self.send(json.dumps(action))

    async def send_cursor(self, x: float, y: float, tick: int) -> None:
        """Send the player's current cursor position in world coordinates."""
        await self.send(json.dumps({"type": "cursor", "tick": tick, "x": round(x, 2), "y": round(y, 2)}))

    async def recv(self) -> str:
        if self._connection is None:
            raise RuntimeError("Client is not connected.")
        message = await self._connection.recv()
        return str(message)

    async def _send_ack(self, tick: int) -> None:
        await self.send(json.dumps({"type": "ack", "tick": tick}))

    async def _request_resync(self, last_tick: int) -> None:
        await self.send(json.dumps({"type": "resync", "last_tick": last_tick}))


if __name__ == "__main__":
    import sys
    import threading
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from app.networking.window import GameWindow

    server_ip = input("Enter server IP address: ").strip()
    uri = f"ws://{server_ip}:8765"

    window = GameWindow(title="Multiplayer")

    async def _networking() -> None:
        def on_message(msg: str) -> None:
            data = json.loads(msg)
            if data["type"] == "leave":
                window.remove_player(data["id"])

        client = WebSocketClient(uri, message_handler=on_message)
        await client.connect()
        await client.listen()

        while True:
            x, y = window.get_mouse_pos()
            tick = getattr(client._game, "_last_tick", 0) if client._game else 0
            await client.send_cursor(x, y, tick)
            await asyncio.sleep(1 / 20)

    def _run_networking() -> None:
        asyncio.run(_networking())

    thread = threading.Thread(target=_run_networking, daemon=True)
    thread.start()

    window.run()
