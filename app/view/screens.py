import pygame


class Screens:
    """
    Handles menu / UI screens such as home screen, end screen, etc.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height

        pygame.font.init()

        self.title_font = pygame.font.SysFont("Trebuchet MS", 72, bold=True)
        self.subtitle_font = pygame.font.SysFont("Trebuchet MS", 30, italic=True)
        self.button_font = pygame.font.SysFont("Trebuchet MS", 36)
        

    def homescreen(self, screen, events):

        screen.fill((55, 101, 179))
        pygame.draw.rect(screen,(20, 40, 180),screen.get_rect(),15)

        title_text = self.title_font.render("Stress Test", True,(237, 198, 30))
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 3 + 60))
        screen.blit(title_text, title_rect)

        start_button = pygame.Rect(self.width//2-150, self.height//2+20, 300, 70)

        hovered = start_button.collidepoint(pygame.mouse.get_pos())

        pygame.draw.rect(
            screen,
            (70,160,70) if hovered else (50,130,50),
            start_button,
            border_radius=12
        )

        text = self.button_font.render("Start Game", True, (255,255,255))
        screen.blit(text, text.get_rect(center=start_button.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and hovered:
                    return "start"

        return None
    
    def top_toolbar(self, screen, events):

        mouse_pos = pygame.mouse.get_pos()

        pause_button = pygame.Rect(self.width//2 - 80, 20, 70, 70)
        pause_hovered = pause_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (150,150,150) if pause_hovered else (100,100,100),
            pause_button,
            border_radius=12
        )

        text = self.button_font.render("||", True, (255,255,255))
        screen.blit(text, text.get_rect(center=pause_button.center))

        quit_button = pygame.Rect(self.width//2 + 10, 20, 70, 70)
        quit_hovered = quit_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (150,150,150) if quit_hovered else (100,100,100),
            quit_button,
            border_radius=12
        )

        text = self.button_font.render("X", True, (255,255,255))
        screen.blit(text, text.get_rect(center=quit_button.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_hovered:
                    return "pause"
                if event.button == 1 and quit_hovered:
                    return "quit"

        return None
    
    def pause_screen(self, screen, events):
        screen.fill((55, 101, 179))
        pygame.draw.rect(screen,(20, 40, 180),screen.get_rect(),15)
        
        pause_text = self.title_font.render("Paused", True,(237, 198, 30))
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 3 + 60))
        screen.blit(pause_text, pause_rect)

        mouse_pos = pygame.mouse.get_pos()

        resume_game_button = pygame.Rect(self.width//2 - 150, self.height // 3 + 130, 300, 70)
        resume_hovered = resume_game_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (70,160,70) if resume_hovered else (50,130,50),          
            resume_game_button,
            border_radius=12
        )

        text = self.button_font.render("Resume Game", True, (255,255,255))
        screen.blit(text, text.get_rect(center=resume_game_button.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and resume_hovered:
                    return "resume"

        return None

    def quit_screen(self, screen, events):
        screen.fill((55, 101, 179))
        pygame.draw.rect(screen,(20, 40, 180),screen.get_rect(),15)

        quit_text = self.title_font.render("Are you sure you want to exit?", True,(237, 198, 30))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 3 + 40))
        screen.blit(quit_text, quit_rect)

        warning_text = self.subtitle_font.render("All in-game progress will be lost.", True,(230, 230, 255))
        warning_rect = warning_text.get_rect(center=(self.width // 2, self.height // 3 + 110))
        screen.blit(warning_text, warning_rect)

        mouse_pos = pygame.mouse.get_pos()

        yes_button = pygame.Rect(self.width//2 - 220, self.height // 3 + 170, 100, 70)
        yes_hovered = yes_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (200,40,60) if yes_hovered else (180,20,40),          
            yes_button,
            border_radius=12
        )

        text = self.button_font.render("Yes", True, (255,255,255))
        screen.blit(text, text.get_rect(center=yes_button.center))

        no_button = pygame.Rect(self.width//2 - 90, self.height // 3 + 170, 300, 70)
        no_hovered = no_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (70,160,70) if no_hovered else (50,130,50),    
            no_button,
            border_radius=12
        )

        text = self.button_font.render("No, resume game", True, (255,255,255))
        screen.blit(text, text.get_rect(center=no_button.center))
    
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and yes_hovered:
                    return "yes"
                if event.button == 1 and no_hovered:
                    return "no"
        return None
