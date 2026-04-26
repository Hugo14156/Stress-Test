from app.avatars.station_avatar import StationAvatar
import pygame
import math


class DepotAvatar(StationAvatar):
    def __init__(self, player):
        super().__init__()
        self.scale = 50
        self.player = player
        self.points = self.hexagon_points((self.scale, self.scale), self.scale)
        self.surface = pygame.Surface((self.scale * 2, self.scale * 2), pygame.SRCALPHA)
        pygame.draw.polygon(self.surface, player.color, self.points)

    def hexagon_points(self, center, size):
        """
        Calculate the 6 vertices of a regular hexagon.
        center: (x, y) tuple for the center of the hexagon
        size: distance from center to any vertex
        """
        cx, cy = center
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30  # start flat-topped
            angle_rad = math.radians(angle_deg)
            x = cx + size * math.cos(angle_rad)
            y = cy + size * math.sin(angle_rad)
            points.append((x, y))
        return points

    def point_in_hexagon(self, point, hex_center, size):
        """
        Rough check if a point is inside a hexagon using distance to center.
        Works well for click detection.
        """
        px, py = point
        cx, cy = hex_center
        dx = abs(px - cx) / size
        dy = abs(py - cy) / size
        return dy <= math.sqrt(3) / 2 and dx <= 1 and dx + dy / math.sqrt(3) <= 1
