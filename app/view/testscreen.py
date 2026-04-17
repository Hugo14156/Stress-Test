import pygame

from camera import Camera

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

camera = Camera(1280, 720)

blue = pygame.Surface((50, 50))
blue.fill("blue")

red = pygame.Surface((50, 50))
red.fill("red")

green = pygame.Surface((50, 50))
green.fill("green")

objects = [
    {"pos": (400, 300), "surface": blue},
    {"pos": (900, 500), "surface": red},
    {"pos": (1600, 900), "surface": green},
]

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    camera.move(keys, event)

    screen.fill("white")

    camera.draw(screen, objects)
    if objects[0]["pos"][0] <= 1000:
        objects[0]["pos"] = (objects[0]["pos"][0] + 1, 300)
    else:
        objects[0]["pos"] = (400, 300)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
