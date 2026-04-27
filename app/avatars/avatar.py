"""
Base avatar class for graphical representation of game objects.

Provides a reusable foundation for sprite-based objects in the game,
managing surface rendering and rotation. Intended to be subclassed,
not used directly.
"""

import pygame


class Avatar:
    """
    Serves as a graphical and statistical representation of an object in the game. Framework class
    to be inherited by others. Not to be used by itself.
    """

    def __init__(self):
        """Initialise the avatar with default asset folder paths and a null surface."""
        self.surface = None

    def rotate(self, world_position, angle):
        """Rotate surface to face the given angle at the given world position.

        Args:
            world_position (tuple[int, int]): The (x, y) world coordinates of surface.
            angle (float): The rotation angle in degrees (counter-clockwise).

        Returns:
            tuple[pygame.Surface, tuple[int, int]]: The rotated surface and the
                top-left position to blit it at, preserving the avatar's visual centre.
        """
        rotated_image = pygame.transform.rotate(self.surface, angle)
        new_rect = rotated_image.get_rect(
            center=self.surface.get_rect(
                topleft=(
                    world_position[0] - (self.surface.get_width() // 2),
                    world_position[1] - (self.surface.get_height() // 2),
                )
            ).center
        )
        return (rotated_image, new_rect.topleft)
