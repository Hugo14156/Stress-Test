from app.avatars.station_avatar import StationAvatar
from pathlib import Path
import pygame
import math


class CityAvatar(StationAvatar):
    def __init__(self):
        super().__init__()
        self.scale = 50
        self.surface = pygame.Surface((self.scale, self.scale), pygame.SRCALPHA)
        self.surface.fill((128, 128, 128))

        # image_path = (
        #     Path(__file__).resolve().parents[3]
        #     / "assets"
        #     / "sprites"
        #     / "cities"
        #     / "city.png"
        # )
        # scale = 60
        # image = pygame.image.load(str(image_path)).convert_alpha()
        # scaled_size = (image.get_width() // scale, image.get_height() // scale)
        # image = pygame.transform.smoothscale(image, scaled_size)
        # self.surface = pygame.Surface(
        #     (image.get_width(), image.get_height()), pygame.SRCALPHA
        # )
        # image_rect = image.get_rect(
        #     center=(image.get_width() // 2, image.get_height() // 2)
        # )
        # self.surface.blit(image, image_rect)
        # self.image = image

    def point_in_city(self, point, rect_center):
        """
        Rough check if a point is inside a hexagon using distance to center.
        Works well for click detection.
        """
        px, py = point
        rx, ry = rect_center
        dx = abs(px - rx) / self.scale
        dy = abs(py - ry) / self.scale
        return dx <= 1 and dy <= 1
