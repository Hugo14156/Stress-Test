from __future__ import annotations

import queue

import pygame

WIDTH, HEIGHT = 640, 480
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (220, 220, 220)
FONT_SIZE = 20
MAX_LINES = 18


class GameWindow:
    """Simple pygame window that displays messages received over the network."""

    def __init__(self, title: str = "Network Window") -> None:
        self._title = title
        self._queue: queue.Queue[str] = queue.Queue()
        self._lines: list[str] = []

    def post_message(self, message: str) -> None:
        """Thread-safe: enqueue a message to be displayed on the next frame."""
        self._queue.put(message)

    def run(self) -> None:
        """Run the pygame event loop on the calling thread. Blocks until closed."""
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(self._title)
        font = pygame.font.SysFont("monospace", FONT_SIZE)
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Drain the message queue
            while not self._queue.empty():
                msg = self._queue.get_nowait()
                self._lines.append(msg)
                if len(self._lines) > MAX_LINES:
                    self._lines.pop(0)

            screen.fill(BG_COLOR)
            for i, line in enumerate(self._lines):
                surface = font.render(line, True, TEXT_COLOR)
                screen.blit(surface, (10, 10 + i * (FONT_SIZE + 4)))

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
