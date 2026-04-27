import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotated Rectangle as Surface")

# Clock for controlling FPS
clock = pygame.time.Clock()

# Create a rectangle surface
rect_width, rect_height = 120, 60
rect_surface = pygame.Surface(
    (rect_width, rect_height), pygame.SRCALPHA
)  # SRCALPHA for transparency
# rect_surface.fill((255, 0, 0))  # Fill with red

# Optional: Draw a border for visibility
image = pygame.image.load("assets/sprites/trains/EMD_8.png")
rect_surface.blit(image, (0, 0))
# pygame.draw.rect(rect_surface, , rect_surface.get_rect(), 3)

# Position variables
center_x, center_y = WIDTH // 2, HEIGHT // 2
angle = 0  # Initial rotation angle


def blit_rotate_center(surf, image, topleft, angle):
    """Rotate a surface while keeping its center."""
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
    surf.blit(rotated_image, new_rect.topleft)


# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update rotation
    angle += 1  # Rotate 1 degree per frame
    if angle >= 360:
        angle = 0

    # Clear screen
    screen.fill((30, 30, 30))

    # Draw rotated rectangle at center
    blit_rotate_center(
        screen,
        rect_surface,
        (rect_width // 2, center_y - rect_height // 2),
        angle,
    )

    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS
