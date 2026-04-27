"""
Test car visual component for debugging train movement and rotation.

Provides a simple coloured rectangle sprite used during development
to verify positioning, pathfinding, and rotation behaviour on the track.
"""

# pylint: disable=no-member
import pygame
from app.avatars.car_avatar import CarAvatar
from pathlib import Path


class PCar1(CarAvatar):
    """
    A simple rectangular sprite used to visualise train movement during testing.

    Renders as a red filled rectangle with a black border, intended as a
    placeholder car for debugging purposes.
    """

    def __init__(self):
        super().__init__()
        image_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "sprites"
            / "cars"
            / "car_1.png"
        )
        scale = 60
        image = pygame.image.load(str(image_path)).convert_alpha()
        scaled_size = (image.get_width() // scale, image.get_height() // scale)
        image = pygame.transform.smoothscale(image, scaled_size)
        self.surface = pygame.Surface(
            (image.get_width(), image.get_height()), pygame.SRCALPHA
        )
        image_rect = image.get_rect(
            center=(image.get_width() // 2, image.get_height() // 2)
        )
        self.surface.blit(image, image_rect)
        self.image = image
        self.mass = 50000  # in kg
        self.passenger_capacity = 50
