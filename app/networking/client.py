from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from websockets.asyncio.client import ClientConnection, connect

MessageHandler = Callable[[str], Awaitable[Any] | Any]


class WebSocketClient:
    """Basic websocket client wrapper with optional background listener."""

    def __init__(self, uri: str, message_handler: MessageHandler | None = None) -> None:
        self.uri = uri
        self._connection: ClientConnection | None = None
        self._message_handler = message_handler
        self._listener_task: asyncio.Task[None] | None = None

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
        """Start a background task that calls message_handler for every incoming message."""
        if self._connection is None:
            raise RuntimeError("Client is not connected.")
        if self._listener_task is not None:
            raise RuntimeError("Listener is already running.")
        self._listener_task = asyncio.create_task(self._receive_loop())

    async def _receive_loop(self) -> None:
        async for message in self._connection:
            if self._message_handler is not None:
                result = self._message_handler(str(message))
                if asyncio.iscoroutine(result):
                    await result

    async def send(self, message: str) -> None:
        if self._connection is None:
            raise RuntimeError("Client is not connected.")
        await self._connection.send(message)

    async def recv(self) -> str:
        if self._connection is None:
            raise RuntimeError("Client is not connected.")
        message = await self._connection.recv()
        return str(message)


if __name__ == "__main__":
    import sys
    import threading
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from app.networking.window import GameWindow

    server_ip = input("Enter server IP address: ").strip()
    uri = f"ws://{server_ip}:8765"

    window = GameWindow(title="WebSocket Client")

    async def _networking() -> None:
        def on_message(msg: str) -> None:
            window.post_message(msg)

        client = WebSocketClient(uri, message_handler=on_message)
        await client.connect()
        window.post_message("[connected to server]")
        await client.listen()

        while True:
            text = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            if not text:
                break
            await client.send(text)

        await client.disconnect()
        window.post_message("[disconnected]")

    def _run_networking() -> None:
        asyncio.run(_networking())

    thread = threading.Thread(target=_run_networking, daemon=True)
    thread.start()

    # pygame must run on the main thread
    window.run()
