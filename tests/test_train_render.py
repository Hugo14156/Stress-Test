"""Render a train PNG with Pygame for visual test validation."""

from pathlib import Path

import pygame  # pylint: disable=c-extension-no-member


def main() -> None:
    """Create a window and render the train sprite until quit."""
    pygame.init()

    width, height = 680, 480
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pygame Blit Example")

    image_path = (
        Path(__file__).resolve().parents[1]
        / "assets"
        / "sprites"
        / "trains"
        / "EMD_8.png"
    )
    image = pygame.image.load(str(image_path)).convert_alpha()

    scaled_size = (image.get_width() // 10, image.get_height() // 10)
    image = pygame.transform.smoothscale(image, scaled_size)

    image_rect = image.get_rect(center=(width // 2, height // 2))
    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        screen.fill((30, 30, 30))
        screen.blit(image, image_rect)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
