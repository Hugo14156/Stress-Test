import pygame
import sys
import math


class TestTrain:

    def __init__(self):
        self.surface = pygame.Surface((20, 10), pygame.SRCALPHA)
        self.surface.fill((255, 0, 0))
        pygame.draw.rect(self.surface, (0, 0, 0), self.surface.get_rect(), 3)

    def get_max_speed(self):
        return 10

    def get_acceleration(self):
        return 1

    def get_deceleration(self):
        return 2

    def rotate(self, world_position, angle):
        """Rotate a surface while keeping its center."""
        rotated_image = pygame.transform.rotate(self.surface, angle)
        new_rect = rotated_image.get_rect(
            center=self.surface.get_rect(
                topleft=(world_position[0] - 20 // 2, world_position[1] - 10 // 2)
            ).center
        )
        return (rotated_image, new_rect.topleft)
