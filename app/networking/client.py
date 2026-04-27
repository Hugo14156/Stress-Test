from __future__ import annotations

import asyncio
import json
from queue import Empty
from collections.abc import Awaitable, Callable
from typing import Any

from websockets.asyncio.client import ClientConnection, connect

from app.networking.serialize import apply_tick, apply_map, apply_delta

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
        self._map_queue = None  # if set, map/resync packets are queued here instead of applied directly

    def attach_map_queue(self, map_queue) -> None:
        """Provide a thread-safe queue to defer map/resync application to the main thread."""
        self._map_queue = map_queue

    def attach_game(self, game) -> None:
        """Attach the local game instance that incoming state will be applied to."""
        self._game = game

    @property
    def own_id(self) -> str | None:
        return self._own_id

    def _queue_latest_map(self, data: dict) -> None:
        """Keep only the newest full-state packet waiting for the pygame thread."""
        if self._map_queue is None:
            return
        while True:
            try:
                self._map_queue.get_nowait()
            except Empty:
                break
        self._map_queue.put(data)

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
            if self._game is not None and self._game._local_player is not None:
                self._game._local_player.id = self._own_id
                self._game._local_player.color = tuple(
                    data.get("color", self._game._local_player.color)
                )

        elif msg_type in ("map", "resync"):
            if self._map_queue is not None:
                self._queue_latest_map(data)
            elif self._game is not None:
                apply_map(data, self._game)

        elif msg_type in ("track_add", "line_update", "train_add"):
            if self._map_queue is not None:
                self._map_queue.put(data)
            elif self._game is not None:
                apply_delta(data, self._game)

        elif msg_type == "tick":
            if self._game is not None:
                apply_tick(data, self._game)

            self._ticks_received += 1
            if self._ticks_received % ACK_INTERVAL == 0:
                await self._send_ack(data.get("tick", 0))

        elif msg_type == "reject":
            print(
                f"[client] action rejected: {data.get('action')} — {data.get('reason')}"
            )

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
            return
        try:
            await self._connection.send(message)
        except Exception as exc:
            print(f"[client] disconnected while sending: {exc}")
            self._connection = None

    async def send_action(self, action: dict) -> None:
        """Send a client action packet. Caller is responsible for setting 'tick'."""
        await self.send(json.dumps(action))

    async def send_cursor(
        self,
        x: float,
        y: float,
        tick: int,
        name: str = "",
        color: tuple = (255, 255, 0),
    ) -> None:
        """Send the player's cursor position, name, and color in world coordinates."""
        await self.send(
            json.dumps(
                {
                    "type": "cursor",
                    "tick": tick,
                    "x": round(x, 2),
                    "y": round(y, 2),
                    "name": name,
                    "color": list(color),
                }
            )
        )

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
    import queue
    import sys
    import threading
    import pygame
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from app.game import Game
    from app.networking.serialize import apply_map, apply_delta

    import os

    server_ip = (
        os.environ.get("STRESS_TEST_SERVER_IP")
        or input("Enter server LAN IP (e.g. 192.168.1.5): ").strip()
    )
    # Strip any accidental ws:// prefix or port the user may have pasted
    server_ip = server_ip.removeprefix("ws://").split(":")[0]
    uri = f"ws://{server_ip}:8765"

    game = Game()
    client = WebSocketClient(uri)
    client.attach_game(game)

    # Main thread puts action dicts here; networking thread drains and sends them
    action_queue: queue.Queue = queue.Queue()
    # Map/resync packets are queued here and applied on the main thread (pygame safety)
    map_queue: queue.Queue = queue.Queue()
    client.attach_map_queue(map_queue)

    async def _networking() -> None:
        await client.connect()
        await client.listen()
        while True:
            # drain all queued actions from the main thread
            while not action_queue.empty():
                action = action_queue.get_nowait()
                await client.send_action(action)

            tick = game._last_tick
            mouse_pos = pygame.mouse.get_pos()
            world_pos = game._local_player.camera.screen_to_world(
                mouse_pos[0], mouse_pos[1]
            )
            await client.send_cursor(
                world_pos[0],
                world_pos[1],
                tick,
                name=game._local_player._name,
                color=game._local_player.color,
            )
            await asyncio.sleep(1 / 20)

    def _run_networking() -> None:
        asyncio.run(_networking())

    thread = threading.Thread(target=_run_networking, daemon=True)
    thread.start()

    # --- pygame render loop (main thread) ---
    pygame.init()
    screen = pygame.display.set_mode(game.resolution)
    pygame.display.set_caption("Stress Test")
    clock = pygame.time.Clock()
    state = "home"
    clicked_last_tick = False
    made_new_line = False

    def _latest_owned_line():
        return next(
            (
                line
                for line in reversed(game.lines)
                if getattr(line, "owner_id", None) in (None, client.own_id)
            ),
            None,
        )

    def _owned_depot():
        return next(
            (
                depot
                for depot in game.depots
                if getattr(depot, "owner_id", None) == client.own_id
            ),
            None,
        )

    running = True
    while running:
        # Apply any pending map/resync packets (deferred from networking thread)
        pending_packets = []
        while not map_queue.empty():
            pending_packets.append(map_queue.get_nowait())
        for packet in pending_packets:
            if packet.get("type") in ("map", "resync"):
                apply_map(packet, game)
            else:
                apply_delta(packet, game)

        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed(num_buttons=3)
        screen.fill("grey")

        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break
            if state == "game" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t and game.depots:
                    depot = _owned_depot()
                    if depot is None:
                        print("[client] cannot buy train: own depot not synced yet")
                        continue
                    action_queue.put(
                        {
                            "type": "buy_train",
                            "tick": game._last_tick,
                            "depot_id": depot.id,
                        }
                    )
        if state == "home":
            if game._local_player.screen.homescreen(screen, events) == "start":
                state = "game"
                clicked_last_tick = True

        elif state == "game":
            making_lines = game.action == "MakingLine"
            game._local_player.camera.move(keys)

            # render only — no train.tick() calls, server drives simulation
            render_stack = game.compile_render_stack(
                game.action == "PlacingTrack", making_lines
            )
            game._local_player.camera.draw(screen, render_stack)

            toolbar_action = game._local_player.screen.top_toolbar(screen, events)
            if toolbar_action == "pause":
                state = "pause"
                clicked_last_tick = True
            elif toolbar_action == "quit":
                state = "quit"
                clicked_last_tick = True
            elif toolbar_action == "place_track":
                game.action = (
                    "PlacingTrack" if game.action != "PlacingTrack" else "Normal"
                )
                game.last_node = None
                clicked_last_tick = True
            elif toolbar_action == "make_line":
                if game.action != "MakingLine":
                    game.action = "MakingLine"
                    made_new_line = False
                else:
                    game.action = "Normal"
                    made_new_line = False
                    game.last_node = None
                clicked_last_tick = True

            if game.action == "PlacingTrack":
                mouse_pos = pygame.mouse.get_pos()
                world_pos = game._local_player.camera.screen_to_world(
                    mouse_pos[0], mouse_pos[1]
                )
                if mouse[0]:
                    if game.last_node is None and not clicked_last_tick:
                        for node in game.nodes:
                            if node.check_collision(world_pos):
                                game.last_node = node
                                clicked_last_tick = True
                                break
                    elif game.last_node is not None and not clicked_last_tick:
                        # Check if the second click lands on an existing node
                        existing = next(
                            (
                                n
                                for n in game.nodes
                                if n.check_collision(world_pos)
                                and n is not game.last_node
                            ),
                            None,
                        )
                        if existing:
                            action_queue.put(
                                {
                                    "type": "place_track",
                                    "tick": game._last_tick,
                                    "station_a": game.last_node.id,
                                    "station_b": existing.id,
                                }
                            )
                        else:
                            action_queue.put(
                                {
                                    "type": "place_track",
                                    "tick": game._last_tick,
                                    "station_a": game.last_node.id,
                                    "x": world_pos[0],
                                    "y": world_pos[1],
                                }
                            )
                        game.last_node = None
                        clicked_last_tick = True
                else:
                    clicked_last_tick = False

            elif game.action == "MakingLine":
                mouse_pos = pygame.mouse.get_pos()
                world_pos = game._local_player.camera.screen_to_world(
                    mouse_pos[0], mouse_pos[1]
                )
                if mouse[0] and not clicked_last_tick:
                    if not made_new_line:
                        action_queue.put(
                            {"type": "create_line", "tick": game._last_tick}
                        )
                        made_new_line = True
                    else:
                        for node in game.nodes:
                            if node.check_collision(world_pos):
                                action_queue.put(
                                    {
                                        "type": "toggle_station",
                                        "tick": game._last_tick,
                                        "node_id": node.id,
                                    }
                                )
                                break
                    clicked_last_tick = True
                elif not mouse[0]:
                    clicked_last_tick = False

        elif state == "pause":
            if game._local_player.screen.pause_screen(screen, events) == "resume":
                state = "game"

        elif state == "quit":
            result = game._local_player.screen.quit_screen(screen, events)
            if result == "yes":
                running = False
            elif result == "no":
                state = "game"

        pygame.display.flip()
        clock.tick(game._fps)

    pygame.quit()
