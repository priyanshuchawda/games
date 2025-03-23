import pygame
from pygame import mixer

class GameBase:
    def __init__(self, width=None, height=None, title="Game"):
        # Get display info for proper screen sizing
        display_info = pygame.display.Info()
        self.max_width = display_info.current_w
        self.max_height = display_info.current_h
        
        # Use current display mode size if no dimensions provided
        current_mode = pygame.display.get_surface()
        if current_mode:
            self.width = current_mode.get_width() if width is None else width
            self.height = current_mode.get_height() if height is None else height
        else:
            # Default to 80% of screen size if no current display
            self.width = int(self.max_width * 0.8) if width is None else width
            self.height = int(self.max_height * 0.8) if height is None else height
        
        # Check if already in fullscreen
        self.is_fullscreen = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN) if pygame.display.get_surface() else False
        self.setup_display()
        pygame.display.set_caption(title)
        
        # Game settings
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.FPS = 60

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)

        # Pause menu buttons
        self.pause_font = pygame.font.Font(None, 36)
        self.menu_items = ["Resume", "Toggle Fullscreen", "Back to Launcher"]
        self.selected_item = 0

    def setup_display(self):
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.max_width, self.max_height), pygame.FULLSCREEN)
            self.width = self.max_width
            self.height = self.max_height
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.setup_display()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                
                if event.key == pygame.K_F11:  # Add F11 shortcut for fullscreen
                    self.toggle_fullscreen()
                
                if self.paused:
                    if event.key == pygame.K_UP:
                        self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        selected_option = self.menu_items[self.selected_item]
                        if selected_option == "Resume":
                            self.paused = False
                        elif selected_option == "Toggle Fullscreen":
                            self.toggle_fullscreen()
                        elif selected_option == "Back to Launcher":
                            self.running = False
                            return True
        return False

    def draw_pause_menu(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        # Draw pause menu title
        title = self.pause_font.render("PAUSED", True, self.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(title, title_rect)

        # Draw pause menu items
        for i, item in enumerate(self.menu_items):
            color = self.WHITE if i == self.selected_item else self.GRAY
            text = self.pause_font.render(item, True, color)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2 + i * 50))
            self.screen.blit(text, text_rect)

    def run(self):
        while self.running:
            if self.handle_events():
                break

            if not self.paused:
                self.update()
            
            self.draw()
            if self.paused:
                self.draw_pause_menu()
            
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def update(self):
        # To be implemented by child classes
        pass

    def draw(self):
        # To be implemented by child classes
        pass