import pygame


class Camera:
    """
    Represents the camera in the game world, allowing for movement and zooming. 
    Tracks the camera's position and zoom level, and provides methods to convert between world 
    and screen coordinates, as well as to determine if objects are visible within the camera's view.
    """

    def __init__(self, width, height):
        """
        Initializes the camera with the given width and height for viewport dimensions.

        Args:
            width (int): The width of the camera's view in pixels.
            height (int): The height of the camera's view in pixels.
        """
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
        """
        Moves the camera based on the pressed keys. 
        WASD keys control movement, while 1 and 2 control zooming.
        
        Args:
            keys (pygame.key.get_pressed()): The current state of all keyboard buttons.
        """
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
        """
        Calculates the world coordinates of the camera's view bounds based on its current position and zoom level.
        
        Returns:
            tuple: A tuple containing the left, right, top, and bottom world coordinates of the camera's viewport.
        """
        half_w = (self.width // 2) / self.zoom
        half_h = (self.height // 2) / self.zoom

        return (self.x - half_w, self.x + half_w, self.y - half_h, self.y + half_h)

    def is_visible(self, x, y, obj_surface):
        """
        Determines if an object at the given world coordinates with the specified surface is visible within the camera's current viewport.
       
         Args:
            x (float): The x-coordinate of the object's position in world space.
            y (float): The y-coordinate of the object's position in world space.
            obj_surface (pygame.Surface): The surface representing the object.
        
        Returns:
            bool: True if the object is visible within the camera's view, False otherwise.
        """
        left, right, top, bottom = self.bounds

        w, h = obj_surface.get_size()

        offset = 10
        obj_left = x
        obj_right = x + w
        obj_top = y
        obj_bottom = y + h

        return not (obj_right < left + offset or obj_left > right - offset or obj_bottom < top + offset or obj_top > bottom - offset)

    def world_to_screen(self, x, y):
        """
        Converts world coordinates to screen coordinates based on the camera's current position and zoom level.
        
        Args:
            x (float): The x-coordinate in world space.
            y (float): The y-coordinate in world space.

        Returns:
            tuple: A tuple containing the x and y coordinates in screen space.
        """
        left, _, top, _ = self.bounds

        screen_x = (x - left) * self.zoom
        screen_y = (y - top) * self.zoom

        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """
        Converts screen coordinates to world coordinates based on the camera's current position and zoom level.
        
        Args:
            screen_x (float): The x-coordinate in screen space.
            screen_y (float): The y-coordinate in screen space.

        Returns:
            tuple: A tuple containing the x and y coordinates in world space.
        """
        left, _, top, _ = self.bounds

        x = screen_x / self.zoom + left
        y = screen_y / self.zoom + top

        return (x, y)

    def draw(self, screen, objects):
        """
        Draws the visible objects onto the screen based on the camera's current position and zoom level.
       
        Args:
            screen (pygame.Surface): The surface to draw on.
            objects (list): A list of dictionaries, each containing 'pos' (tuple of world coordinates) and 'surface' (pygame.Surface)
        """
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
