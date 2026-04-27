import pygame
from app.view.camera import Camera  


class Screens:
    """
    A class to manage different game screens such as the home screen, pause screen, and quit confirmation screen.
    """

    def __init__(self, width, height):
        """
        Initializes the Screens class with the given width and height for the game window.

        Args:
            width (int): The width of the game window in pixels.
            height (int): The height of the game window in pixels.
        """
        self.width = width
        self.height = height

        pygame.font.init()

        self.title_font = pygame.font.SysFont("Trebuchet MS", 80, bold=True)
        self.subtitle_font = pygame.font.SysFont("Trebuchet MS", 30, italic=True)
        self.button_font = pygame.font.SysFont("Trebuchet MS", 36)

    def homescreen(self, screen, events):
        """
        Displays the home screen and handles user interactions.

        Args:
            screen (pygame.Surface): The surface to draw the home screen on.
            events (list): A list of pygame events to handle user interactions.

        Returns:
            str: "start" if the user clicks the start button, None otherwise.
        """

        screen.fill((255, 180, 90))
        pygame.draw.rect(screen, (250, 130, 70), screen.get_rect(), 15)

        title_text = self.title_font.render("Stress Test", True, (255, 255, 255))
        title_rect = title_text.get_rect(
            center=(self.width // 2, self.height // 3 + 100)
        )
        screen.blit(title_text, title_rect)

        start_button = pygame.Rect(
            self.width // 2 - 150, self.height // 2 + 20, 300, 70
        )

        hovered = start_button.collidepoint(pygame.mouse.get_pos())

        pygame.draw.rect(
            screen,
            (100, 190, 100) if hovered else (80, 160, 80),
            start_button,
            border_radius=12,
        )

        text = self.button_font.render("Start Game", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=start_button.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and hovered:
                    return "start"
        return None

    def top_toolbar(self, screen, events):
        """
        Displays the top toolbar during the game and handles user interactions for pausing and quitting.

        Args:
            screen (pygame.Surface): The surface to draw the toolbar on.
            events (list): A list of pygame events to handle user interactions.

        Returns:
            str: "pause" if the user clicks the pause button, "quit" if the user clicks the quit button, "place_track" if the user clicks the place track button, "make_line" if the user clicks the make line button, None otherwise.
        """
        mouse_pos = pygame.mouse.get_pos()

        pause_button = pygame.Rect(self.width // 2 - 150, 20, 70, 70)
        pause_hovered = pause_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (200, 180, 120) if pause_hovered else (180, 160, 100),
            pause_button,
            border_radius=12,
        )

        text = self.button_font.render("||", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=pause_button.center))

        quit_button = pygame.Rect(self.width // 2 - 60, 20, 70, 70)
        quit_hovered = quit_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (200, 180, 120) if quit_hovered else (180, 160, 100),
            quit_button,
            border_radius=12,
        )

        text = self.button_font.render("X", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=quit_button.center))

        track_button = pygame.Rect(self.width // 2 + 30, 20, 70, 70)
        track_hovered = track_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (120, 120, 240) if track_hovered else (100, 150, 240),
            track_button,
            border_radius=12,
        )

        text = pygame.font.SysFont("Trebuchet MS", 20).render(
            "Place\nTrack", True, (255, 255, 255)
        )
        screen.blit(text, text.get_rect(center=track_button.center))

        line_button = pygame.Rect(self.width // 2 + 120, 20, 70, 70)
        line_hovered = line_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (120, 120, 240) if line_hovered else (100, 150, 240),
            line_button,
            border_radius=12,
        )

        text = pygame.font.SysFont("Trebuchet MS", 20).render(
            "Make\nLine", True, (255, 255, 255)
        )
        screen.blit(text, text.get_rect(center=line_button.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and pause_hovered:
                    return "pause"
                if event.button == 1 and quit_hovered:
                    return "quit"
                if event.button == 1 and track_hovered:
                    return "place_track"
                if event.button == 1 and line_hovered:
                    return "make_line"

        return None

    def pause_screen(self, screen, events):
        """
        Displays the pause screen and handles user interactions for resuming the game.

        Args:
            screen (pygame.Surface): The surface to draw the pause screen on.
            events (list): A list of pygame events to handle user interactions.

        Returns:
            str: "resume" if the user clicks the resume button, None otherwise.
        """
        screen.fill((255, 180, 90))
        pygame.draw.rect(screen, (250, 130, 70), screen.get_rect(), 15)

        pause_text = self.title_font.render("Paused", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(
            center=(self.width // 2, self.height // 3 + 100)
        )
        screen.blit(pause_text, pause_rect)

        mouse_pos = pygame.mouse.get_pos()

        resume_game_button = pygame.Rect(
            self.width // 2 - 150, self.height // 3 + 170, 300, 70
        )
        resume_hovered = resume_game_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (70, 160, 70) if resume_hovered else (50, 130, 50),
            resume_game_button,
            border_radius=12,
        )

        text = self.button_font.render("Resume Game", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=resume_game_button.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and resume_hovered:
                    return "resume"

        return None

    def quit_screen(self, screen, events):
        """
        Displays the quit confirmation screen and handles user interactions for confirming or canceling quitting the game.

        Args:
            screen (pygame.Surface): The surface to draw the quit confirmation screen on.
            events (list): A list of pygame events to handle user interactions.

        Returns:
            str: "yes" if the user clicks the yes button, "no" if the user clicks the no button, None otherwise.
        """
        screen.fill((255, 180, 90))
        pygame.draw.rect(screen, (250, 130, 70), screen.get_rect(), 15)

        quit_text = self.title_font.render(
            "Are you sure you want to exit?", True, (255, 255, 255)
        )
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 3 + 80))
        screen.blit(quit_text, quit_rect)

        warning_text = self.subtitle_font.render(
            "All in-game progress will be lost.", True, (255, 240, 210)
        )
        warning_rect = warning_text.get_rect(
            center=(self.width // 2, self.height // 3 + 150)
        )
        screen.blit(warning_text, warning_rect)

        mouse_pos = pygame.mouse.get_pos()

        yes_button = pygame.Rect(self.width // 2 - 220, self.height // 3 + 210, 100, 70)
        yes_hovered = yes_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (200, 40, 60) if yes_hovered else (180, 20, 40),
            yes_button,
            border_radius=12,
        )

        text = self.button_font.render("Yes", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=yes_button.center))

        no_button = pygame.Rect(self.width // 2 - 90, self.height // 3 + 210, 300, 70)
        no_hovered = no_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (70, 160, 70) if no_hovered else (50, 130, 50),
            no_button,
            border_radius=12,
        )

        text = self.button_font.render("No, resume game", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=no_button.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and yes_hovered:
                    return "yes"
                if event.button == 1 and no_hovered:
                    return "no"
        return None

    def depot_press_button(self, screen, events, camera, depots):
        """
        Checks if the player clicks on a depot's center node and displays a prompt to enter the depot.
        
        Args:
            screen (pygame.Surface): The surface to draw the prompt on.
            events (list): A list of pygame events to handle user interactions.
            camera (Camera): The camera object to convert between screen and world coordinates.
            depots (list): A list of depot objects to check for interactions.
            
        Returns:
            str: "depot" if the user clicks on a depot's center node and the prompt, None otherwise.
            """
        mouse_pos = pygame.mouse.get_pos()
        world_mouse = camera.screen_to_world(*mouse_pos)

        for depot in depots:
            node = depot.center_node
            if node.check_collision(world_mouse):
                sx, sy = camera.world_to_screen(*node.position)
                press_rect = pygame.Rect(sx - 130, sy - 30, 260, 60)
                pygame.draw.rect(screen, (100, 200, 250), press_rect, border_radius=12)
                text = self.button_font.render("Enter Depot", True, (255, 255, 255))
                screen.blit(text, text.get_rect(center=press_rect.center))

                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            return "depot"
        return None
    
    def depot_screen(self, screen, events):
        """
        Displays the depot screen with options to buy trains and view the depot train list.
        
        Args:
            screen (pygame.Surface): The surface to draw the depot screen on.
            events (list): A list of pygame events to handle user interactions.
            
        Returns:
            str: "buy_EMD8" if the user clicks the buy EMD E8 button, "buy_EMD9" if the user clicks the buy EMD E9 button, "buy_ACS-64" if the user clicks the buy Siemens ACS-64 button, "return" if the user clicks the return to game button, "train_list" if the user clicks the view depot train list button, None otherwise.
        """

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((220, 200, 160, 120))
        screen.blit(overlay, (0, 0))

        popup = pygame.Rect(
            200,
            200,
            self.width - 400,
            self.height - 400
        )

        pygame.draw.rect(screen, (235, 235, 235), popup, border_radius=18)
        pygame.draw.rect(screen, (40, 40, 40), popup, 4, border_radius=18)

        title = self.title_font.render("Depot Menu", True, (20, 20, 20))
        screen.blit(title, title.get_rect(center=(popup.centerx, popup.y + 80)))

        mouse_pos = pygame.mouse.get_pos()

        button_width = 240
        button_height = 120
        gap = 40

        total_width = button_width * 3 + gap * 2
        start_x = popup.centerx - total_width // 2 - 50
        y_pos = popup.y + 170

        EMD8_button = pygame.Rect(
            start_x,
            y_pos,
            button_width,
            button_height
        )

        EMD8_hovered = EMD8_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (50, 200, 60) if EMD8_hovered else (80, 220, 70),
            EMD8_button,
            border_radius=12
        )

        text = self.button_font.render("Buy EMD E8", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=EMD8_button.center))

        EMD9_button = pygame.Rect(
            start_x + button_width + gap,
            y_pos,
            button_width,
            button_height
        )

        EMD9_hovered = EMD9_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (50, 200, 60) if EMD9_hovered else (80, 220, 70),
            EMD9_button,
            border_radius=12
        )

        text = self.button_font.render("Buy EMD E9", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=EMD9_button.center))

        siemens_button = pygame.Rect(
            start_x + (button_width + gap) * 2,
            y_pos,
            button_width + 150,
            button_height
        )

        siemens_hovered = siemens_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (50, 200, 60) if siemens_hovered else (80, 220, 70),
            siemens_button,
            border_radius=12
        )

        text = self.button_font.render("Buy Siemens ACS-64", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=siemens_button.center))

        return_button = pygame.Rect(
            start_x + (button_width + gap) * 2,
            y_pos + 180,
            button_width + 150,
            button_height
        )

        return_hovered = return_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (50, 80, 220) if return_hovered else (80, 110, 250),
            return_button,
            border_radius=12
        )

        text = self.button_font.render("Return to Game", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=return_button.center))

        train_list_button = pygame.Rect(
            start_x,
            y_pos + 180,
            button_width + 280,
            button_height
        )

        train_list_hovered = train_list_button.collidepoint(mouse_pos)

        pygame.draw.rect(
            screen,
            (50, 80, 220) if train_list_hovered else (80, 110, 250),
            train_list_button,
            border_radius=12
        )

        text = self.button_font.render("View Depot Train List", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=train_list_button.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if EMD8_hovered:
                    return "buy_EMD8"

                if EMD9_hovered:
                    return "buy_EMD9"

                if siemens_hovered:
                    return "buy_ACS-64"
                
                if return_hovered:
                    return "return"
                
                if train_list_hovered:
                    return "train_list"
        return None

    def purchase_complete(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((110, 230, 100, 110))
        screen.blit(overlay, (0, 0))

        popup = pygame.Rect(
            200,
            200,
            self.width - 400,
            self.height - 400
        )

        pygame.draw.rect(screen, (235, 235, 235), popup, border_radius=18)
        pygame.draw.rect(screen, (40, 40, 40), popup, 4, border_radius=18)

        title = self.title_font.render("Purchase Complete!", True, (20, 20, 20))
        screen.blit(title, title.get_rect(center=(popup.centerx, popup.y + 220)))

    def player_money(self, screen, money):
        """
        Displays the player's current money on the screen.

        Args:
            screen (pygame.Surface): The surface to draw the player's money on.
            self.local_player (Player): The local player object containing the money attribute.

        Returns:
            None
        """
        cash = int(money)
        pygame.draw.rect(screen, (80, 60, 40), (30, self.height - 86, 310, 55), border_radius=12)
        money_text = self.button_font.render(f"Money: ${cash}", True, (255, 255, 255))
        screen.blit(money_text, (50, self.height - 80))