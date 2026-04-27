import pygame

from camera import Camera
from screens import Screens

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Stress Test")

clock = pygame.time.Clock()

camera = Camera(1280, 720)
screens = Screens(1280, 720)

state = "depot"

blue = pygame.Surface((50, 50))
blue.fill("blue")

red = pygame.Surface((50, 50))
red.fill("red")

green = pygame.Surface((50, 50))
green.fill("green")

hola = pygame.Surface((50, 50))
hola.fill("purple")

objects = [
    {"pos": (400, 300), "surface": blue},
    {"pos": (900, 500), "surface": red},
    {"pos": (1600, 900), "surface": green},
    {"pos": (100, 900), "surface": hola},
]

running = True

while running:
    events = pygame.event.get()
    keys = pygame.key.get_pressed()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")

    if state == "home":
        if screens.homescreen(screen, events) == "start":
            state = "game"

    elif state == "game":
        camera.move(keys)
        camera.draw(screen, objects)

        if screens.top_toolbar(screen, events) == "pause":
            state = "pause"
        elif screens.top_toolbar(screen, events) == "quit":
            state = "quit"

    elif state == "pause":
        screens.pause_screen(screen, events)
        if screens.pause_screen(screen, events) == "resume":
            state = "game"

    elif state == "quit":
        screens.quit_screen(screen, events)
        if screens.quit_screen(screen, events) == "yes":
            running = False
        elif screens.quit_screen(screen, events) == "no":
            state = "game"

    elif state == "depot":
        screens.depot_screen(screen, events)

    pygame.display.flip()
    clock.tick(60)
