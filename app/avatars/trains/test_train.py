"""
Test train visual component for debugging train movement and physics.

Provides a simple coloured rectangle sprite with stub physics values used
during development to verify speed, acceleration, and rotation behaviour.
"""

# pylint: disable=no-member
import pygame
from app.avatars.avatar import Avatar


class TestTrain(Avatar):
    """A simple rectangular sprite used to visualise train behaviour during testing.

    Renders as a red filled rectangle with a black border. Provides fixed stub
    values for speed and acceleration, intended as a placeholder locomotive
    for debugging purposes.
    """

    def __init__(self, color=None):
        """Initialise the test train surface with a red fill and black border."""
        self.surface = pygame.Surface((30, 15), pygame.SRCALPHA)
        self.surface.fill(color or (255, 0, 0))
        pygame.draw.rect(self.surface, (0, 0, 0), self.surface.get_rect(), 3)

    def get_max_speed(self, c):
        """Return the maximum speed of the train in pixels per second.

        Args:
            c: Unused context parameter, reserved for future use.

        Returns:
            int: The fixed maximum speed value.
        """
        return 200

    def get_acceleration(self, c):
        """Return the acceleration rate of the train in pixels per second squared.

        Args:
            c: Unused context parameter, reserved for future use.

        Returns:
            int: The fixed acceleration value.
        """
        return 100

    def get_deceleration(self, c):
        """Return the deceleration rate of the train in pixels per second squared.

        Args:
            c: Unused context parameter, reserved for future use.

        Returns:
            int: The fixed deceleration value.
        """
        return 10

    def update_condition(self, dt):
        return 0.1 * dt

    def rotate(self, world_position, angle):
        """Rotate a surface while keeping its center.

        Args:
            world_position (tuple[int, int]): The (x, y) world coordinates of the train.
            angle (float): The rotation angle in degrees (counter-clockwise).

        Returns:
            tuple[pygame.Surface, tuple[int, int]]: The rotated surface and the
                top-left position to blit it at, preserving the train's visual centre.
        """
        rotated_image = pygame.transform.rotate(self.surface, angle)
        new_rect = rotated_image.get_rect(
            center=self.surface.get_rect(
                topleft=(world_position[0] - 20 // 2, world_position[1] - 10 // 2)
            ).center
        )
        return (rotated_image, new_rect.topleft)
