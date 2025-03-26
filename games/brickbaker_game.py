import pygame
from utils.game_base import GameBase
import math  # Added for angle calculations

class BrickbakerGame(GameBase):
    def __init__(self):
        super().__init__(title="Brickbaker")
        
        # Scale elements based on screen size
        self.brick_width = self.width // 20
        self.brick_height = self.height // 30
        self.gap = self.width // 200
        
        # Ball properties - scaled with screen size
        self.ball_radius = min(self.width, self.height) // 80
        self.initial_ball_speed = min(self.width, self.height) // 160
        self.ball_speed = self.initial_ball_speed
        self.ball_dx = self.ball_speed
        self.ball_dy = -self.ball_speed
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        
        # Speed increase properties
        self.start_time = pygame.time.get_ticks()
        self.speed_multiplier = 1.0
        self.speed_increase_rate = 0.25  # 10% increase every 30 seconds
        self.speed_check_interval = 10000  # 30 seconds in milliseconds
        
        # Colors
        self.yellow = (65, 25, 133)
        self.green = (0, 255, 0)
        
        # Brick layout - adjusted for screen size
        self.rows = 5
        self.columns = min(18, self.width // (self.brick_width + self.gap))
        
        # Paddle properties - scaled with screen size
        self.paddle_width = self.width // 8
        self.paddle_height = self.height // 30
        self.paddle_x = self.width // 2 - self.paddle_width // 2
        self.paddle_y = int(self.height * 0.85)
        self.paddle_vel = self.width // 120  # Smoother movement speed
        
        # Game state
        self.lives = 3
        self.bloc_rect = []
        self.game_over = False
        self.last_time = pygame.time.get_ticks()
        self.dt = 0  # Delta time for smooth movement
        
        # Initialize bricks
        self.build_level()

    def build_level(self):
        self.bloc_rect.clear()
        start_x = (self.width - (self.columns * (self.brick_width + self.gap))) // 2
        
        for i in range(self.rows):
            for j in range(self.columns):
                x = start_x + j * (self.brick_width + self.gap)
                y = self.gap + i * (self.brick_height + self.gap)
                bloc = pygame.Rect(x, y, self.brick_width, self.brick_height)
                self.bloc_rect.append(bloc)

    def handle_events(self):
        if super().handle_events():
            return True
            
        # Calculate delta time for smooth movement
        current_time = pygame.time.get_ticks()
        self.dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.paddle_x >= 0:
            self.paddle_x -= self.paddle_vel * self.dt * 60  # Scale by 60 to maintain consistent speed
        elif keys[pygame.K_RIGHT] and self.paddle_x <= self.width - self.paddle_width:
            self.paddle_x += self.paddle_vel * self.dt * 60
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()
        
        return False

    def update(self):
        if self.paused or self.game_over:
            return

        # Increase ball speed over time
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time >= self.speed_check_interval:
            self.speed_multiplier += self.speed_increase_rate
            self.ball_speed = self.initial_ball_speed * self.speed_multiplier
            # Preserve direction while updating speed
            angle = math.atan2(self.ball_dy, self.ball_dx)
            self.ball_dx = self.ball_speed * math.cos(angle)
            self.ball_dy = self.ball_speed * math.sin(angle)
            self.start_time = pygame.time.get_ticks()

        # Update ball position with delta time
        self.ball_x += self.ball_dx * self.dt * 60
        self.ball_y += self.ball_dy * self.dt * 60

        # Ball collision with walls
        if self.ball_x - self.ball_radius <= 0 or self.ball_x + self.ball_radius >= self.width:
            self.ball_dx = -self.ball_dx

        if self.ball_y - self.ball_radius <= 0:
            self.ball_dy = -self.ball_dy

        # Ball collision with paddle
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height)
        ball_rect = pygame.Rect(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, 
                              self.ball_radius * 2, self.ball_radius * 2)
        
        if ball_rect.colliderect(paddle_rect):
            self.ball_dy = -abs(self.ball_dy)  # Always bounce up
            # Calculate angle based on where ball hits paddle
            hit_pos = (self.ball_x - self.paddle_x) / self.paddle_width
            angle = hit_pos * math.pi/3  # Convert hit position to angle (max 60 degrees)
            self.ball_dx = self.ball_speed * math.sin(angle)
            self.ball_dy = -self.ball_speed * math.cos(angle)

        # Ball falls below paddle
        if self.ball_y + self.ball_radius > self.height:
            self.lives -= 1
            if self.lives > 0:
                self.reset_ball()
            else:
                self.game_over = True

        # Check brick collisions
        ball_rect = pygame.Rect(self.ball_x - self.ball_radius, self.ball_y - self.ball_radius, 
                              self.ball_radius * 2, self.ball_radius * 2)
        for bloc in self.bloc_rect[:]:
            if ball_rect.colliderect(bloc):
                self.bloc_rect.remove(bloc)
                # Determine bounce direction based on collision side
                if abs(ball_rect.bottom - bloc.top) < 10 or abs(ball_rect.top - bloc.bottom) < 10:
                    self.ball_dy = -self.ball_dy
                else:
                    self.ball_dx = -self.ball_dx

    def reset_ball(self):
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        # Use current ball speed when resetting
        angle = math.pi/4  # 45 degree angle
        self.ball_dx = self.ball_speed * math.cos(angle)
        self.ball_dy = -self.ball_speed * math.sin(angle)  # Negative to go up
        self.paddle_x = self.width // 2 - self.paddle_width // 2

    def draw(self):
        self.screen.fill(self.BLACK)

        # Draw bricks
        for bloc in self.bloc_rect:
            pygame.draw.rect(self.screen, self.green, bloc)

        # Draw ball
        pygame.draw.circle(self.screen, self.WHITE, (int(self.ball_x), int(self.ball_y)), self.ball_radius)
        
        # Draw paddle
        pygame.draw.rect(self.screen, self.yellow, (self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height))

        # Draw lives and speed multiplier
        font = pygame.font.Font(None, self.height // 20)
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        speed_text = font.render(f"Speed: x{self.speed_multiplier:.1f}", True, (255, 255, 255))
        self.screen.blit(lives_text, (20, 20))
        self.screen.blit(speed_text, (20, 50))

        if self.game_over:
            font = pygame.font.Font(None, self.height // 10)
            text = font.render("Game Over! Press R to Restart", True, self.WHITE)
            text_rect = text.get_rect(center=(self.width/2, self.height/2))
            self.screen.blit(text, text_rect)