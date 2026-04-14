from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from websockets.asyncio.server import Server, ServerConnection, serve

MessageHandler = Callable[[str, ServerConnection], Awaitable[Any] | Any]


class WebSocketServer:
    """Basic websocket server with optional broadcast behavior."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765,
        message_handler: MessageHandler | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self._message_handler = message_handler
        self._clients: set[ServerConnection] = set()
        self._server: Server | None = None

    async def start(self) -> None:
        if self._server is not None:
            raise RuntimeError("Server is already running.")
        self._server = await serve(self._handle_client, self.host, self.port)

    async def stop(self) -> None:
        if self._server is None:
            raise RuntimeError("Server is not running.")
        self._server.close()
        await self._server.wait_closed()
        self._server = None
        self._clients.clear()

    async def wait_closed(self) -> None:
        if self._server is None:
            raise RuntimeError("Server is not running.")
        await self._server.wait_closed()

    async def send_to(self, client: ServerConnection, message: str) -> None:
        await client.send(message)

    async def broadcast(self, message: str) -> None:
        if not self._clients:
            return
        await asyncio.gather(
            *(client.send(message) for client in tuple(self._clients)),
            return_exceptions=False,
        )

    async def _handle_client(self, websocket: ServerConnection) -> None:
        self._clients.add(websocket)
        try:
            async for message in websocket:
                if self._message_handler is not None:
                    result = self._message_handler(message, websocket)
                    if asyncio.iscoroutine(result):
                        await result
                else:
                    await self.broadcast(message)
        finally:
            self._clients.discard(websocket)


if __name__ == "__main__":
    import socket

    def _get_local_ip() -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]

    async def _main() -> None:
        async def on_message(msg: str, sender: ServerConnection) -> None:
            print(f"[server] received: {msg}")
            await sender.send(f"echo: {msg}")

        local_ip = _get_local_ip()
        server = WebSocketServer(host="0.0.0.0", message_handler=on_message)
        await server.start()
        print(f"[server] listening on ws://{local_ip}:8765 — Ctrl+C to stop")
        await server.wait_closed()

    asyncio.run(_main())
