"""
Defines the SNCF Class BB 66600 locomotive avatar, including its static and live specifications.

Includes calculation methods for max speed, acceleration, and deceleration.

Also provides a simple coloured rectangle sprite used during development to 
verify positioning, pathfinding, and rotation behaviour on the track.
"""

# pylint: disable=no-member
import pygame
from app.avatars.train_avatar import TrainAvatar
from pathlib import Path


class BB_66600(TrainAvatar):
    """
    A class to represent the SNCF Class BB 66600 locomotive.

    Attributes:
        surface: A pygame Surface object representing the visual appearance of the locomotive.
        mass: The mass of the locomotive in kilograms.
        power_output: The power output of the locomotive in watts.
        year: The year the locomotive was built.
        power_type: The type of power used by the locomotive (e.g., diesel-electric).
    """

    # Note to self: we may remove some of the attributes from the docstring since they are private
    def __init__(self):
        """
        Initialize the specifications of the SNCF Class BB 66600 locomotive, including its surface representation and physical properties.

        Args: nothing

        Returns: nothing
        """
        super().__init__()
        image_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "sprites"
            / "trains"
            / "BB_66600.png"
        )
        self.surface = pygame.Surface((30, 15), pygame.SRCALPHA)
        scale = 30
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
        # self.surface.fill((255, 0, 0))
        # pygame.draw.rect(self.surface, (0, 0, 0), self.surface.get_rect(), 3)

        self._mass = 64410  # in kg
        self._power_output = 1100000  # in watts
        self._year = 1960
        self._power_type = "Diesel-electric"
        self._condition_rating = 0.004
