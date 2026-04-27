from app.avatars.station_avatar import StationAvatar
import pygame
import math


class CityAvatar(StationAvatar):
    def __init__(self):
        super().__init__()
        self.scale = 50
        self.surface = pygame.Surface((self.scale, self.scale), pygame.SRCALPHA)
        self.surface.fill((128, 128, 128))

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
