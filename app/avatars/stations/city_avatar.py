from app.avatars.station_avatar import StationAvatar
import pygame
import math


class CityAvatar(StationAvatar):
    def __init__(self, rotation=0):
        super().__init__()
        base_scale = 50
        self.rotation = rotation
        base_surface = pygame.Surface((base_scale, base_scale), pygame.SRCALPHA)
        base_surface.fill((128, 128, 128))
        self.surface = pygame.transform.rotate(base_surface, rotation)
        self.scale = self.surface.get_width()

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
