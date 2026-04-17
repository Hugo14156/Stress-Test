import pygame

class Camera:
    """
    Camera render function to display game board.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.x = width // 2
        self.y = height // 2

        self.speed = 5

        self.zoom = 1.0
        self.zoom_speed = 0.025
        self.min_zoom = 0.5
        self.max_zoom = 2.0

    def move(self, keys):
        if keys[pygame.K_w]:
            self.y += self.speed
        if keys[pygame.K_s]:
            self.y -= self.speed
        if keys[pygame.K_a]:
            self.x += self.speed
        if keys[pygame.K_d]:
            self.x -= self.speed

        if keys[pygame.K_1]:
            self.zoom += self.zoom_speed
        if keys[pygame.K_2]:
            self.zoom -= self.zoom_speed

        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

    @property
    def bounds(self):
        half_w = (self.width // 2) / self.zoom
        half_h = (self.height // 2) / self.zoom

        return (
            self.x - half_w,
            self.x + half_w,
            self.y - half_h,
            self.y + half_h
        )

    def is_visible(self, x, y, obj_surface):
        left, right, top, bottom = self.bounds

        w, h = obj_surface.get_size()

        center_x = x + w / 2
        center_y = y + h / 2

        return left <= center_x <= right and top <= center_y <= bottom

    def world_to_screen(self, x, y):
        left, _, top, _ = self.bounds

        screen_x = (x - left) * self.zoom
        screen_y = (y - top) * self.zoom

        return screen_x, screen_y

    def draw(self, screen, objects):
        for obj in objects:
            x, y = obj["pos"]

            if self.is_visible(x, y, obj["surface"]):
                sx, sy = self.world_to_screen(x, y)

                surf = obj["surface"]
                if self.zoom != 1.0:
                    size = surf.get_size()
                    new_size = (int(size[0] * self.zoom), int(size[1] * self.zoom))
                    surf = pygame.transform.scale(surf, new_size)

                screen.blit(surf, (sx, sy))