import pygame
import random
import math  # Add math module import
from utils.game_base import GameBase

class PongGame(GameBase):
    def __init__(self):
        super().__init__(title="Pong")
        
        # Game objects
        self.paddle_width = 15
        self.paddle_height = 90
        self.ball_size = 15
        self.ball_speed = 7
        self.paddle_speed = 7
        self.ai_speed = 6  # Slightly slower than player for fairness
        
        # Colors
        self.PADDLE_COLOR = (200, 200, 200)
        self.BALL_COLOR = (255, 255, 255)
        self.SCORE_COLOR = (255, 255, 255)
        
        self.reset_game()
        
        # Initialize game font
        self.game_font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
    def reset_game(self):
        # Paddles initial position
        self.player_paddle = pygame.Rect(50, self.height//2 - self.paddle_height//2,
                                       self.paddle_width, self.paddle_height)
        self.ai_paddle = pygame.Rect(self.width - 50 - self.paddle_width,
                                   self.height//2 - self.paddle_height//2,
                                   self.paddle_width, self.paddle_height)
        
        # Ball initial position and direction
        self.ball_pos = [self.width//2, self.height//2]
        self.serve_ball()
        
        # Scores
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.paused = False
        
    def serve_ball(self):
        self.ball_pos = [self.width//2, self.height//2]
        # Random angle between -45 and 45 degrees
        angle = random.uniform(-0.785, 0.785)  # in radians
        direction = 1 if random.random() > 0.5 else -1
        self.ball_vel = [
            direction * self.ball_speed * math.cos(angle),  # Use math.cos instead of pygame.math.cos
            self.ball_speed * math.sin(angle)  # Use math.sin instead of pygame.math.sin
        ]
    
    def update_ai(self):
        # Simple AI that follows the ball
        if not self.game_over and not self.paused:
            target_y = self.ball_pos[1] - self.paddle_height//2
            if self.ai_paddle.centery < target_y:
                self.ai_paddle.y += self.ai_speed
            elif self.ai_paddle.centery > target_y:
                self.ai_paddle.y -= self.ai_speed
            
            # Keep paddle on screen
            self.ai_paddle.clamp_ip(self.screen.get_rect())
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        
        if not self.game_over and not self.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.player_paddle.y -= self.paddle_speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.player_paddle.y += self.paddle_speed
            
            # Keep paddle on screen
            self.player_paddle.clamp_ip(self.screen.get_rect())
        
        return False
    
    def update(self):
        if self.game_over or self.paused:
            return
            
        # Update AI
        self.update_ai()
        
        # Update ball position
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        
        # Ball collision with top and bottom
        if self.ball_pos[1] <= 0 or self.ball_pos[1] >= self.height - self.ball_size:
            self.ball_vel[1] = -self.ball_vel[1]
        
        # Ball collision with paddles
        ball_rect = pygame.Rect(self.ball_pos[0], self.ball_pos[1],
                              self.ball_size, self.ball_size)
        
        if ball_rect.colliderect(self.player_paddle):
            self.ball_pos[0] = self.player_paddle.right
            self.ball_vel[0] = abs(self.ball_vel[0]) * 1.1  # Increase speed slightly
            # Add some randomness to y velocity
            self.ball_vel[1] += random.uniform(-1, 1)
            
        elif ball_rect.colliderect(self.ai_paddle):
            self.ball_pos[0] = self.ai_paddle.left - self.ball_size
            self.ball_vel[0] = -abs(self.ball_vel[0]) * 1.1  # Increase speed slightly
            # Add some randomness to y velocity
            self.ball_vel[1] += random.uniform(-1, 1)
        
        # Scoring
        if self.ball_pos[0] < 0:
            self.ai_score += 1
            if self.ai_score >= 11:
                self.game_over = True
            else:
                self.serve_ball()
                
        elif self.ball_pos[0] > self.width:
            self.player_score += 1
            if self.player_score >= 11:
                self.game_over = True
            else:
                self.serve_ball()
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Draw paddles
        pygame.draw.rect(self.screen, self.PADDLE_COLOR, self.player_paddle)
        pygame.draw.rect(self.screen, self.PADDLE_COLOR, self.ai_paddle)
        
        # Draw ball
        pygame.draw.rect(self.screen, self.BALL_COLOR,
                        (self.ball_pos[0], self.ball_pos[1],
                         self.ball_size, self.ball_size))
        
        # Draw center line
        pygame.draw.line(self.screen, self.PADDLE_COLOR,
                        (self.width//2, 0), (self.width//2, self.height),
                        2)
        
        # Draw scores
        player_text = self.game_font.render(str(self.player_score), True, self.SCORE_COLOR)
        ai_text = self.game_font.render(str(self.ai_score), True, self.SCORE_COLOR)
        self.screen.blit(player_text, (self.width//4, 20))
        self.screen.blit(ai_text, (3*self.width//4, 20))
        
        if self.game_over:
            winner = "Player Wins!" if self.player_score > self.ai_score else "Computer Wins!"
            game_over_text = self.game_font.render(f'{winner} Press R to Restart', True, self.SCORE_COLOR)
            game_over_rect = game_over_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(game_over_text, game_over_rect)
        elif self.paused:
            pause_text = self.game_font.render('PAUSED', True, self.SCORE_COLOR)
            pause_rect = pause_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(pause_text, pause_rect)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            if self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(self.FPS)