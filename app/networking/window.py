from __future__ import annotations

import hashlib
import threading

import pygame

WIDTH, HEIGHT = 640, 480
BG_COLOR = (30, 30, 30)
DOT_RADIUS = 10


def _id_to_color(client_id: str) -> tuple[int, int, int]:
    """Derive a consistent RGB color from a client ID string."""
    digest = hashlib.md5(client_id.encode()).digest()
    # Boost brightness so dots are visible on the dark background
    return (max(digest[0], 80), max(digest[1], 80), max(digest[2], 80))


class GameWindow:
    """Pygame window that renders a colored dot for each remote player."""

    def __init__(self, title: str = "Multiplayer") -> None:
        self._title = title
        self._lock = threading.Lock()
        self._players: dict[str, tuple[int, int]] = {}
        self._mouse_pos: tuple[int, int] = (0, 0)

    def update_player(self, client_id: str, x: int, y: int) -> None:
        """Thread-safe: set or update a remote player's dot position."""
        with self._lock:
            self._players[client_id] = (x, y)

    def remove_player(self, client_id: str) -> None:
        """Thread-safe: remove a remote player's dot."""
        with self._lock:
            self._players.pop(client_id, None)

    def get_mouse_pos(self) -> tuple[int, int]:
        """Return the latest mouse position captured on the main thread."""
        return self._mouse_pos

    def run(self) -> None:
        """Run the pygame event loop. Must be called from the main thread."""
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(self._title)
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self._mouse_pos = pygame.mouse.get_pos()

            screen.fill(BG_COLOR)

            with self._lock:
                snapshot = dict(self._players)

            for client_id, (x, y) in snapshot.items():
                color = _id_to_color(client_id)
                pygame.draw.circle(screen, color, (x, y), DOT_RADIUS)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
