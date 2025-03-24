import pygame
import random
import time
from pygame.locals import *
from utils.game_base import GameBase

class FlappyGame(GameBase):
    def __init__(self):
        super().__init__(title="Flappy Bird")
        
        # Constants
        self.SPEED = 8      # Slowed down bird's vertical speed effect
        self.GRAVITY = 0.8  # Reduced gravity
        self.GAME_SPEED = 4 # Slowed down overall game speed
        self.GROUND_HEIGHT = self.height // 8
        self.PIPE_WIDTH = self.width // 15
        self.PIPE_HEIGHT = self.height
        self.PIPE_GAP = self.height // 3.5  # Reduced gap size for more challenge
        self.pipe_interval = 1800  # Slightly reduced time between pipes
        
        # Load audio
        pygame.mixer.init()
        self.wing_sound = pygame.mixer.Sound('assets/audio/wing.wav')
        self.hit_sound = pygame.mixer.Sound('assets/audio/hit.wav')
        
        # Initialize sprite groups
        self.bird_group = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        
        # Load background and scale to window size
        self.BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
        self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (self.width, self.height))
        
        self.BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()
        self.BEGIN_IMAGE = pygame.transform.scale(self.BEGIN_IMAGE, (self.width//2, self.height//2))
        
        self.GAME_OVER_IMAGE = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
        self.GAME_OVER_IMAGE = pygame.transform.scale(self.GAME_OVER_IMAGE, (self.width//2, self.height//4))
        
        # Game state
        self.begin = True
        self.game_over = False
        self.score = 0
        self.font = pygame.font.Font(None, 64)
        
        # Initialize game objects
        self.init_game()
    
    def init_game(self):
        # Create bird
        self.bird = Bird(self.width, self.height)
        self.bird_group.add(self.bird)
        
        # Create ground
        for i in range(2):
            ground = Ground(self.width * i, self.width, self.height, self.GROUND_HEIGHT)
            self.ground_group.add(ground)
        
        # Create initial pipes
        self.next_pipe_time = 0
        self.create_pipe_pair()
    
    def create_pipe_pair(self):
        """Create a top and bottom pipe with a challenging but fair gap."""
        gap = self.PIPE_GAP
        
        # Adjusted height ranges for more variation
        min_top_height = self.height // 6  # Higher minimum
        max_top_height = self.height - self.GROUND_HEIGHT - gap - self.height // 6  # Lower maximum
        
        if max_top_height < min_top_height:
            max_top_height = min_top_height
        
        # More varied position for the gap
        variance = self.height // 8  # Add some extra randomness to positions
        adjusted_min = max(min_top_height, min_top_height + random.randint(-variance, variance))
        adjusted_max = min(max_top_height, max_top_height + random.randint(-variance, variance))
        
        # Pick a random bottom for the top pipe
        top_pipe_bottom = random.randint(adjusted_min, adjusted_max)
        # The bottom pipe starts at (top pipe bottom + gap)
        bottom_pipe_top = top_pipe_bottom + gap
        
        # Position the pipes offscreen to the right
        xpos = self.width + 100  # Reduced offset for slightly faster appearance
        
        # Create the top (inverted) pipe
        top_pipe = Pipe(
            inverted=True,
            xpos=xpos,
            y_pos=top_pipe_bottom,
            width=self.PIPE_WIDTH,
            full_height=self.PIPE_HEIGHT
        )
        
        # Create the bottom (normal) pipe
        bottom_pipe = Pipe(
            inverted=False,
            xpos=xpos,
            y_pos=bottom_pipe_top,
            width=self.PIPE_WIDTH,
            full_height=self.PIPE_HEIGHT
        )
        
        # Add both to the pipe group
        self.pipe_group.add(top_pipe)
        self.pipe_group.add(bottom_pipe)
        
        # Record the time for spacing out future pipes
        self.next_pipe_time = pygame.time.get_ticks()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                return True
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == K_F11:
                    self.toggle_fullscreen()
                elif event.key in [K_SPACE, K_UP]:
                    if self.begin:
                        self.begin = False
                    elif self.game_over:
                        self.__init__()  # Reset the game by re-initializing
                    else:
                        self.bird.bump()
                        pygame.mixer.Sound.play(self.wing_sound)
        return False
    
    def update(self):
        if self.paused:
            return

        current_time = pygame.time.get_ticks()
        
        if self.begin:
            # Bird flaps in place, ground moves
            self.bird.begin()
            self.ground_group.update()
        elif not self.game_over:
            # Create new pipes periodically
            if current_time - self.next_pipe_time >= self.pipe_interval:
                self.create_pipe_pair()
                self.next_pipe_time = current_time

            # Remove off-screen pipes
            for pipe in self.pipe_group.sprites():
                if pipe.rect.right < 0:
                    self.pipe_group.remove(pipe)
                # Check if bird passed the pipe for scoring
                elif (not pipe.scored 
                      and not pipe.inverted 
                      and pipe.rect.right < self.bird.rect.left):
                    self.score += 0.5  # Each gap counts as 1 point across two pipes
                    pipe.scored = True

            # Update sprites
            self.bird_group.update()
            self.ground_group.update()
            self.pipe_group.update()

            # Check collisions
            if (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask) or
                    pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask)):
                pygame.mixer.Sound.play(self.hit_sound)
                self.game_over = True
    
    def draw(self):
        # Draw background
        self.screen.blit(self.BACKGROUND, (0, 0))
        
        # Draw game elements
        self.pipe_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        self.ground_group.draw(self.screen)
        
        if self.begin:
            begin_rect = self.BEGIN_IMAGE.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(self.BEGIN_IMAGE, begin_rect)
        elif self.game_over:
            gameover_rect = self.GAME_OVER_IMAGE.get_rect(center=(self.width//2, self.height//3))
            self.screen.blit(self.GAME_OVER_IMAGE, gameover_rect)
            restart_text = self.font.render("Press SPACE to restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(restart_text, restart_rect)
        
        # Draw score
        if not self.begin:
            score_text = self.font.render(str(int(self.score)), True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.width//2, 50))
            self.screen.blit(score_text, score_rect)
        
        if self.paused:
            self.draw_pause_menu()
        
        pygame.display.flip()

class Bird(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        pygame.sprite.Sprite.__init__(self)
        
        # Load and scale bird images
        self.images = [pygame.image.load(f'assets/sprites/bluebird-{flap}flap.png').convert_alpha()
                      for flap in ('up', 'mid', 'down')]
        scale_factor = screen_height // 24 / self.images[0].get_height()  # Make bird smaller
        self.images = [pygame.transform.scale(img, 
                      (int(img.get_width() * scale_factor), 
                       int(img.get_height() * scale_factor))) 
                      for img in self.images]
        
        self.speed = 0
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_rect()
        self.rect.x = screen_width // 6
        self.rect.y = screen_height // 2
        
        self.gravity = 0.8     # Reduced gravity
        self.jump_speed = -8   # Reduced jump strength
        self.max_speed = 10    # Reduced max downward speed
    
    def update(self):
        # Update bird animation
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        
        # Apply gravity
        self.speed = min(self.speed + self.gravity, self.max_speed)
        self.rect.y += self.speed
        
        # Rotate based on speed
        self.image = pygame.transform.rotate(self.images[self.current_image], -self.speed * 2)
        self.mask = pygame.mask.from_surface(self.image)
    
    def bump(self):
        # Bird jumps upward
        self.speed = self.jump_speed
    
    def begin(self):
        # Simple flapping animation while waiting
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, y_pos, width, full_height):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        # Scale the pipe to the full height
        self.image = pygame.transform.scale(self.image, (width, full_height))
        
        self.inverted = inverted
        self.scored = False
        
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        
        # Flip image if it's the top (inverted) pipe
        if self.inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            # Align bottom of the top pipe to y_pos
            self.rect.bottom = y_pos
        else:
            # Align top of the bottom pipe to y_pos
            self.rect.top = y_pos
        
        self.mask = pygame.mask.from_surface(self.image)
        
        # Movement speed of the pipe
        self.movement_speed = 4
    
    def update(self):
        self.rect.x -= self.movement_speed

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos, screen_width, screen_height, ground_height):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (screen_width, ground_height))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = screen_height - ground_height
        
        self.screen_width = screen_width
    
    def update(self):
        # Move ground left, and wrap around
        self.rect.x -= 5
        if self.rect.right <= 0:
            self.rect.x = self.screen_width