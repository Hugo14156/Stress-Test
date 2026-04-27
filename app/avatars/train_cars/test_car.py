"""
Test car visual component for debugging train movement and rotation.

Provides a simple coloured rectangle sprite used during development
to verify positioning, pathfinding, and rotation behaviour on the track.
"""

# pylint: disable=no-member
import pygame


class TestCar:
    """
    A simple rectangular sprite used to visualise train movement during testing.

    Renders as a red filled rectangle with a black border, intended as a
    placeholder car for debugging purposes.
    """

    def __init__(self, color=None):
        """Initialise the test car surface with a red fill and black border."""
        self.surface = pygame.Surface((20, 15), pygame.SRCALPHA)
        self.surface.fill(color or (255, 0, 0))
        pygame.draw.rect(self.surface, (0, 0, 0), self.surface.get_rect(), 3)
        self.mass = 50000  # in kg
        self.cargo_capacity = 50

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
