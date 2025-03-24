import pygame
import random
from utils.game_base import GameBase

class SnakeGame(GameBase):
    def __init__(self):
        super().__init__(title="Snake")
        # Make cell size smaller and ensure it divides screen dimensions evenly
        self.cell_size = 20
        self.grid_width = self.width // self.cell_size
        self.grid_height = self.height // self.cell_size
        self.snake_speed = 10
        # Start snake at grid-aligned position
        start_x = (self.grid_width // 2) * self.cell_size
        start_y = (self.grid_height // 2) * self.cell_size
        self.snake = [(start_x, start_y)]
        self.direction = [self.cell_size, 0]
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # Colors
        self.SNAKE_COLOR = (50, 205, 50)
        self.FOOD_COLOR = (255, 0, 0)
        self.SCORE_COLOR = (255, 255, 255)
        
        # Initialize game font
        self.game_font = pygame.font.Font(None, 36)
        
        # Initialize clock for controlling game speed
        self.clock = pygame.time.Clock()
        
    def spawn_food(self):
        while True:
            # Ensure food spawns on grid
            grid_x = random.randrange(0, self.grid_width)
            grid_y = random.randrange(0, self.grid_height)
            pos = (grid_x * self.cell_size, grid_y * self.cell_size)
            if pos not in self.snake:
                return pos
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif not self.game_over and not self.paused:
                    if event.key in [pygame.K_LEFT, pygame.K_a] and self.direction[0] <= 0:
                        self.direction = [-self.cell_size, 0]
                    elif event.key in [pygame.K_RIGHT, pygame.K_d] and self.direction[0] >= 0:
                        self.direction = [self.cell_size, 0]
                    elif event.key in [pygame.K_UP, pygame.K_w] and self.direction[1] <= 0:
                        self.direction = [0, -self.cell_size]
                    elif event.key in [pygame.K_DOWN, pygame.K_s] and self.direction[1] >= 0:
                        self.direction = [0, self.cell_size]
        return False
    
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Move snake
        new_head = (self.snake[0][0] + self.direction[0],
                   self.snake[0][1] + self.direction[1])
        
        # Check for collisions with walls
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height or
            new_head in self.snake[:-1]):  # Don't count tail collision when moving
            self.game_over = True
            return
        
        self.snake.insert(0, new_head)
        
        # Check if food is eaten - using grid-aligned positions
        food_rect = pygame.Rect(self.food[0], self.food[1], self.cell_size, self.cell_size)
        head_rect = pygame.Rect(new_head[0], new_head[1], self.cell_size, self.cell_size)
        
        if food_rect.colliderect(head_rect):
            self.score += 1
            self.food = self.spawn_food()
            # Increase speed every 5 points
            if self.score % 5 == 0:
                self.snake_speed = min(20, self.snake_speed + 1)
        else:
            self.snake.pop()
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Draw snake
        for segment in self.snake:
            pygame.draw.rect(self.screen, self.SNAKE_COLOR,
                           (segment[0], segment[1], self.cell_size - 2, self.cell_size - 2))
        
        # Draw food
        pygame.draw.rect(self.screen, self.FOOD_COLOR,
                        (self.food[0], self.food[1], self.cell_size - 2, self.cell_size - 2))
        
        # Draw score
        score_text = self.game_font.render(f'Score: {self.score}', True, self.SCORE_COLOR)
        self.screen.blit(score_text, (10, 10))
        
        if self.game_over:
            game_over_text = self.game_font.render('Game Over! Press R to Restart', True, self.SCORE_COLOR)
            game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(game_over_text, game_over_rect)
        elif self.paused:
            pause_text = self.game_font.render('PAUSED', True, self.SCORE_COLOR)
            pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_text, pause_rect)
        
        pygame.display.flip()
    
    def reset_game(self):
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = [self.cell_size, 0]
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.snake_speed = 10
    
    def run(self):
        while self.running:
            if self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(self.snake_speed)  # Control game speed