from typing import Any


class Surface:
    def __init__(self, size: tuple[int, int]) -> None: ...
    def fill(self, color: Any) -> None: ...
    def get_size(self) -> tuple[int, int]: ...
    def blit(self, source: Surface, dest: tuple[float, float]) -> None: ...


class _Display:
    def set_mode(self, size: tuple[int, int]) -> Surface: ...
    def flip(self) -> None: ...


class _Clock:
    def tick(self, framerate: int) -> None: ...


class _Time:
    def Clock(self) -> _Clock: ...


class _Event:
    def get(self) -> list[Any]: ...


class _Key:
    def get_pressed(self) -> Any: ...


class _Transform:
    def scale(self, surface: Surface, size: tuple[int, int]) -> Surface: ...


display: _Display
time: _Time
event: _Event
key: _Key
transform: _Transform

QUIT: int
K_w: int
K_s: int
K_a: int
K_d: int
K_1: int
K_2: int


def init() -> None: ...
def quit() -> None: ...