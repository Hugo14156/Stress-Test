from pathlib import Path
import pygame
from app.avatars.avatar import Avatar
import math


class TrackAvatar(Avatar):

    def __init__(self, length):
        super().__init__()
        self.image_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "sprites"
            / "track"
            / "track.png"
        )
        self.scale = 60
        self.length = length
        self.track_sprite = None
        self.full_surface = None
        self.line_surface = None
        self.line_color = (0, 0, 0)
        self.make_full_surface()
        self.make_line_surface()

    def make_full_surface(self):
        track_sprite = pygame.image.load(str(self.image_path)).convert_alpha()
        scaled_size = (
            int(track_sprite.get_width() / self.scale),
            int(track_sprite.get_height() / self.scale),
        )
        track_sprite = pygame.transform.smoothscale(track_sprite, scaled_size)
        tile_count = math.ceil(self.length / track_sprite.get_width()) + 1
        self.full_surface = pygame.Surface(
            (self.length, track_sprite.get_height()), pygame.SRCALPHA
        )

        for i in range(tile_count):
            x = i * track_sprite.get_width()
            self.full_surface.blit(track_sprite, (x, 0))
        self.track_sprite = track_sprite

    def make_line_surface(self):
        self.line_surface = pygame.Surface(
            (self.length, self.track_sprite.get_height()), pygame.SRCALPHA
        )
        self.line_surface.fill(self.line_color)

    def change_color(self, color):
        self.line_color = color
        self.make_line_surface()
