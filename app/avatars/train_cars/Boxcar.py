"""
Defines the Boxcar avatar, including its mass, capacity, and build year.

Includes calculation methods for max speed, acceleration, and deceleration.

Also provides a simple coloured rectangle sprite used during development to 
verify positioning, pathfinding, and rotation behaviour on the track.
"""

# pylint: disable=no-member
import pygame
from pathlib import Path


class Boxcar:
    """
    A simple rectangular sprite used to visualise train movement during testing.

    Renders as a red filled rectangle with a black border, intended as a
    placeholder car for debugging purposes.
    """

    def __init__(self):
        """Initialise the test car surface with a red fill and black border."""
        image_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "sprites"
            / "trains"
            / "Boxcar.png"
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

        self.mass = 13608 # in kg
        self.capacity = 362874 # in kg
        self.year = 1962

    def rotate(self, world_position, angle):
        """Rotate the car surface to face the given angle at the given world position.

        Args:
            world_position (tuple[int, int]): The (x, y) world coordinates of the car.
            angle (float): The rotation angle in degrees (counter-clockwise).

        Returns:
            tuple[pygame.Surface, tuple[int, int]]: The rotated surface and the
                top-left position to blit it at, preserving the car's visual centre.
        """
        rotated_image = pygame.transform.rotate(self.surface, angle)
        new_rect = rotated_image.get_rect(
            center=self.surface.get_rect(
                topleft=(world_position[0] - 20 // 2, world_position[1] - 10 // 2)
            ).center
        )
        return (rotated_image, new_rect.topleft)