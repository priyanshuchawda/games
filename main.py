import pygame
import sys
import os
from pygame import mixer
import math
import hashlib  # For simple password hashing

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
DARK_BG = (18, 18, 18)
DARKER_BG = (12, 12, 12)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
ACCENT_BLUE = (66, 133, 244)
ACCENT_GREEN = (52, 168, 83)
ACCENT_RED = (234, 67, 53)
ACCENT_YELLOW = (251, 188, 4)
ACCENT_PURPLE = (149, 97, 226)
TRANSPARENT = (0, 0, 0, 0)

class InputBox:
    def __init__(self, x, y, width, height, text='', is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.text = text
        self.is_password = is_password
        self.font = pygame.font.Font(None, 32)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = ACCENT_BLUE if self.active else WHITE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                display_text = '*' * len(self.text) if self.is_password else self.text
                self.txt_surface = self.font.render(display_text, True, self.color)
        return False

    def draw(self, screen):
        display_text = '*' * len(self.text) if self.is_password else self.text
        self.txt_surface = self.font.render(display_text, True, self.color)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Button:
    def __init__(self, x, y, width, height, text, color, icon_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        # Ensure color is a tuple of 3 integers (RGB)
        self.color = tuple(max(0, min(255, int(c))) for c in color[:3])
        self.original_color = self.color
        # Calculate hover color with bounds checking
        self.hover_color = tuple(min(255, c + 30) for c in self.color)
        self.font = pygame.font.Font(None, 32)
        self.icon = None
        self.is_hovered = False
        self.is_selected = False
        self.animation_progress = 0
        
        # Try to load icon if provided
        if icon_path:
            try:
                self.icon = pygame.image.load(os.path.join('assets', 'images', icon_path))
                self.icon = pygame.transform.scale(self.icon, (32, 32))
            except:
                print(f"Could not load icon: {icon_path}")

    def draw(self, surface):
        # Draw button background with animation
        self.animation_progress = min(1, self.animation_progress + (0.1 if self.is_hovered or self.is_selected else -0.1))
        current_color = self.interpolate_color(self.original_color, self.hover_color, self.animation_progress)
        
        # Draw rounded rectangle with ensured valid color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        
        # Draw selection indicator
        if self.is_selected:
            pygame.draw.rect(surface, WHITE, self.rect, width=3, border_radius=10)
        
        # Draw icon if available
        if self.icon:
            icon_rect = self.icon.get_rect(midleft=(self.rect.left + 20, self.rect.centery))
            surface.blit(self.icon, icon_rect)
            text_surface = self.font.render(self.text, True, WHITE)
            text_rect = text_surface.get_rect(midleft=(self.rect.left + 70, self.rect.centery))
        else:
            text_surface = self.font.render(self.text, True, WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)
        
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def interpolate_color(self, color1, color2, progress):
        # Ensure we're interpolating between valid RGB colors and return integers
        return tuple(max(0, min(255, int(c1 + (c2 - c1) * progress))) 
                    for c1, c2 in zip(color1, color2))

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Create input boxes for username and password
        box_width = 200
        box_height = 40
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        self.username_box = InputBox(center_x - box_width//2, center_y - 50, 
                                   box_width, box_height)
        self.password_box = InputBox(center_x - box_width//2, center_y + 20, 
                                   box_width, box_height, is_password=True)
        
        self.login_button = Button(center_x - 100//2, center_y + 100, 
                                 100, 40, "Login", ACCENT_BLUE)
        
        self.error_message = ""
        self.error_timer = 0
        self.logged_in = False
        self.username = ""

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            # Handle input box events
            username_enter = self.username_box.handle_event(event)
            password_enter = self.password_box.handle_event(event)
            
            # Try to login if enter is pressed in either box
            if username_enter or password_enter:
                self.try_login()
            
            # Handle login button
            if self.login_button.handle_event(event):
                self.try_login()
                
        return True

    def try_login(self):
        username = self.username_box.text
        password = self.password_box.text
        
        if not username or not password:
            self.error_message = "Please enter both username and password"
            self.error_timer = 60
            return
        
        # For this simple implementation, we'll accept any non-empty username/password
        self.logged_in = True
        self.username = username

    def draw(self):
        # Draw background
        self.screen.fill(DARK_BG)
        
        # Draw title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("Game Center Login", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(title, title_rect)
        
        # Draw labels
        label_font = pygame.font.Font(None, 32)
        username_label = label_font.render("Username:", True, WHITE)
        password_label = label_font.render("Password:", True, WHITE)
        
        self.screen.blit(username_label, (self.username_box.rect.x, self.username_box.rect.y - 30))
        self.screen.blit(password_label, (self.password_box.rect.x, self.password_box.rect.y - 30))
        
        # Draw input boxes
        self.username_box.draw(self.screen)
        self.password_box.draw(self.screen)
        
        # Draw login button
        self.login_button.draw(self.screen)
        
        # Draw error message if any
        if self.error_timer > 0:
            error_font = pygame.font.Font(None, 28)
            error_text = error_font.render(self.error_message, True, ACCENT_RED)
            error_rect = error_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 160))
            self.screen.blit(error_text, error_rect)
            self.error_timer -= 1
        
        pygame.display.flip()

    def run(self):
        while self.running and not self.logged_in:
            if not self.handle_events():
                return False
            self.draw()
            self.clock.tick(FPS)
        return True

class GameLauncher:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game Center")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_game = None
        self.scroll_offset = 0
        self.target_scroll = 0
        self.animation_time = 0
        self.selected_game_index = 0  # Track selected game
        self.controls_font = pygame.font.Font(None, 24)
        self.username = ""
        
        # Show login screen first
        login_screen = LoginScreen(self.screen)
        if login_screen.run():
            self.username = login_screen.username
            # Create categories and buttons
            self.setup_game_buttons()

            # Load background music
            try:
                mixer.music.load(os.path.join('assets', 'sounds', 'background.wav'))
                mixer.music.play(-1)  # Loop indefinitely
                mixer.music.set_volume(0.3)  # Set lower volume
            except Exception as e:
                print(f"Could not load background music: {e}")
        else:
            self.running = False

    def setup_game_buttons(self):
        button_width = 200
        button_height = 200
        spacing = 20
        grid_start_x = (SCREEN_WIDTH - (button_width * 3 + spacing * 2)) // 2
        grid_start_y = 150
        
        self.categories = {
            'Games': [
                ('Snake', ACCENT_GREEN),
                ('Pacman', ACCENT_YELLOW),
                ('Pong', ACCENT_BLUE),
                ('Tic Tac Toe', ACCENT_PURPLE),
                ('Brick Baker', ACCENT_RED),
                ('Flappy Bird', ACCENT_BLUE),
                ('Memory Match', ACCENT_PURPLE)
            ]
        }
        
        self.buttons = {}
        self.game_buttons = []  # Keep track of game buttons separately
        current_x = grid_start_x
        current_y = grid_start_y
        games_per_row = 3
        
        for category, games in self.categories.items():
            current_y += spacing
            for i, (game_name, color) in enumerate(games):
                row = i // games_per_row
                col = i % games_per_row
                x = grid_start_x + col * (button_width + spacing)
                y = grid_start_y + row * (button_height + spacing)
                
                button_key = game_name.lower().replace(' ', '')
                self.buttons[button_key] = Button(
                    x, y, button_width, button_height,
                    game_name, color, f"{button_key}.png"
                )
                self.game_buttons.append(button_key)
            current_y += spacing

        # Add exit button at the bottom
        self.buttons['exit'] = Button(
            SCREEN_WIDTH - 200 - 50,
            SCREEN_HEIGHT - 50 - 30,
            200, 50,
            "Exit Game Center", (40, 40, 40)
        )
        
        # Set initial selection
        self.update_selected_game(0)

    def update_selected_game(self, index):
        # Clear previous selection
        for button in self.buttons.values():
            button.is_selected = False
            
        # Set new selection
        if 0 <= index < len(self.game_buttons):
            self.selected_game_index = index
            self.buttons[self.game_buttons[index]].is_selected = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle mouse wheel for scrolling
            if event.type == pygame.MOUSEWHEEL:
                self.target_scroll = min(0, max(-400, self.target_scroll + event.y * 30))
            
            # Handle keyboard navigation
            if event.type == pygame.KEYDOWN:
                games_per_row = 3
                current_row = self.selected_game_index // games_per_row
                current_col = self.selected_game_index % games_per_row
                
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    new_index = self.selected_game_index - 1
                    if new_index >= 0:      
                        self.update_selected_game(new_index)
                
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    new_index = self.selected_game_index + 1
                    if new_index < len(self.game_buttons):
                        self.update_selected_game(new_index)
                
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    new_index = self.selected_game_index - games_per_row
                    if new_index >= 0:
                        self.update_selected_game(new_index)
                
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    new_index = self.selected_game_index + games_per_row
                    if new_index < len(self.game_buttons):
                        self.update_selected_game(new_index)
                
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    # Launch selected game
                    selected_game = self.game_buttons[self.selected_game_index]
                    self.launch_game(selected_game)
                
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            
            # Handle mouse events
            for button_name, button in self.buttons.items():
                if button.handle_event(event):
                    if button_name == 'exit':
                        self.running = False
                    else:
                        # Update selection when clicking a game
                        if button_name in self.game_buttons:
                            self.update_selected_game(self.game_buttons.index(button_name))
                        self.launch_game(button_name)

    def draw_background(self):
        # Draw gradient background
        for i in range(SCREEN_HEIGHT):
            progress = i / SCREEN_HEIGHT
            color = self.interpolate_color(DARK_BG, DARKER_BG, progress)
            pygame.draw.line(self.screen, color, (0, i), (SCREEN_WIDTH, i))

        # Draw subtle grid pattern
        grid_spacing = 30
        grid_color = (30, 30, 30)  # Darker color for grid lines
        for x in range(0, SCREEN_WIDTH, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y))

    def interpolate_color(self, color1, color2, progress):
        return tuple(int(c1 + (c2 - c1) * progress) for c1, c2 in zip(color1, color2))

    def draw_category_headers(self):
        header_font = pygame.font.Font(None, 48)
        y_pos = 80
        for category in self.categories.keys():
            # Draw category background
            header_bg = pygame.Rect(40, y_pos, SCREEN_WIDTH - 80, 40)
            pygame.draw.rect(self.screen, DARKER_BG, header_bg, border_radius=5)
            
            # Draw category text with pulsing effect
            color = self.interpolate_color(WHITE, ACCENT_BLUE, 
                                        (math.sin(self.animation_time * 0.02) + 1) / 2)
            text = header_font.render(category, True, color)
            self.screen.blit(text, (50, y_pos + 5))

    def draw_controls_help(self):
        help_text = "Arrow Keys/WASD to navigate  |  Enter/Space to select  |  ESC to exit"
        text_surface = self.controls_font.render(help_text, True, GRAY)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(text_surface, text_rect)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def update(self):
        # Smooth scrolling animation
        self.scroll_offset += (self.target_scroll - self.scroll_offset) * 0.1
        
        # Update button positions based on scroll
        for button in self.buttons.values():
            button.rect.y = button.rect.y + (self.target_scroll - self.scroll_offset)

        self.animation_time = (self.animation_time + 1) % 360

    def draw(self):
        self.draw_background()
        
        # Draw animated title with username
        title_font = pygame.font.Font(None, 72)
        title_color = self.interpolate_color(ACCENT_BLUE, ACCENT_GREEN, 
                                          (math.sin(self.animation_time * 0.02) + 1) / 2)
        title = title_font.render(f"Welcome, {self.username}!", True, title_color)
        title_shadow = title_font.render(f"Welcome, {self.username}!", True, DARKER_BG)
        
        # Draw title with shadow effect
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 2, 22))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        # Draw category headers
        self.draw_category_headers()
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Draw controls help
        self.draw_controls_help()
        
        pygame.display.flip()

    def launch_game(self, game_name):
        if game_name == 'snake':
            from games.snake_game import SnakeGame
            game = SnakeGame()
            game.run()
        elif game_name == 'pong':
            from games.pong_game import PongGame
            game = PongGame()
            game.run()
        elif game_name == 'pacman':
            from games.pacman_game import PacmanGame
            game = PacmanGame()
            game.run()
        elif game_name == 'tictactoe':
            from games.tictactoe_game import TicTacToeGame
            game = TicTacToeGame()
            game.run()
        elif game_name == 'brickbaker':
            from games.brickbaker_game import BrickbakerGame
            game = BrickbakerGame()
            game.run()
        elif game_name == 'flappybird':
            from games.flappy_game import FlappyGame
            game = FlappyGame()
            game.run()
        elif game_name == 'memorymatch':
            from games.memory_match_game import MemoryMatchGame
            game = MemoryMatchGame()
            game.run()

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()
    pygame.quit()
    sys.exit()