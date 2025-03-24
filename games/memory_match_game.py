import pygame
import random
import time
import os
from utils.game_base import GameBase

class MemoryMatchGame(GameBase):
    def __init__(self):
        super().__init__(title="Memory Match")
        
        # Colors
        self.CARD_BACK = (50, 50, 150)
        self.CARD_FRONT = (200, 200, 200)
        self.MATCHED_COLOR = (100, 255, 100)
        
        # Game settings
        self.GRID_SIZE = 4  # 4x4 grid
        self.CARD_WIDTH = min(self.width, self.height) // (self.GRID_SIZE + 2)
        self.CARD_HEIGHT = self.CARD_WIDTH
        self.CARD_MARGIN = self.CARD_WIDTH // 10
        
        # Calculate grid position to center it
        total_width = (self.CARD_WIDTH + self.CARD_MARGIN) * self.GRID_SIZE - self.CARD_MARGIN
        total_height = total_width
        self.grid_start_x = (self.width - total_width) // 2
        self.grid_start_y = (self.height - total_height) // 2
        
        # Game state
        self.reset_game()
        
        # Load sounds
        pygame.mixer.init()
        try:
            self.flip_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'memory_match', 'flip.mp3'))
            self.match_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'memory_match', 'match.mp3'))
            self.fail_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'memory_match', 'failed.mp3'))
            # Set volume
            for sound in [self.flip_sound, self.match_sound, self.fail_sound]:
                sound.set_volume(0.3)
        except Exception as e:
            print(f"Could not load Memory Match sound files: {e}")
        
        # Add selected card tracking for keyboard navigation
        self.selected_row = 0
        self.selected_col = 0
    
    def reset_game(self):
        # Create card values (pairs of numbers)
        values = list(range(1, (self.GRID_SIZE * self.GRID_SIZE) // 2 + 1)) * 2
        random.shuffle(values)
        
        # Initialize cards
        self.cards = []
        self.flipped = []  # Currently flipped cards
        self.matched = []  # Pairs that have been matched
        
        # Create grid of cards
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                x = self.grid_start_x + col * (self.CARD_WIDTH + self.CARD_MARGIN)
                y = self.grid_start_y + row * (self.CARD_HEIGHT + self.CARD_MARGIN)
                card_index = row * self.GRID_SIZE + col
                self.cards.append({
                    'rect': pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT),
                    'value': values[card_index],
                    'index': card_index
                })
        
        self.moves = 0
        self.game_over = False
        self.last_flip_time = 0
        self.flip_delay = 1000  # 1 second delay when cards don't match
    
    def handle_events(self):
        # Get all events before any processing
        events = pygame.event.get()
        
        # Handle game events first
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.paused:
                # Left click
                mouse_pos = pygame.mouse.get_pos()
                self.handle_click(mouse_pos)
                continue
                
            elif event.type == pygame.KEYDOWN and not self.paused:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                    continue
                    
                # Keyboard navigation
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    self.selected_col = (self.selected_col - 1) % self.GRID_SIZE
                    continue
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.selected_col = (self.selected_col + 1) % self.GRID_SIZE
                    continue
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_row = (self.selected_row - 1) % self.GRID_SIZE
                    continue
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_row = (self.selected_row + 1) % self.GRID_SIZE
                    continue
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.last_flip_time >= self.flip_delay:
                        # Select card with keyboard
                        card_index = self.selected_row * self.GRID_SIZE + self.selected_col
                        self.handle_card_selection(card_index)
                    continue
        
        # Then handle parent class events (pause menu, etc)
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == pygame.K_F11:
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
    
    def handle_card_selection(self, index):
        """Handle card selection by index"""
        if (index not in self.flipped and 
            index not in self.matched and 
            len(self.flipped) < 2):
            # Flip card
            self.flipped.append(index)
            self.flip_sound.play()
            
            # Check for match if we have 2 cards flipped
            if len(self.flipped) == 2:
                self.moves += 1
                card1 = self.cards[self.flipped[0]]
                card2 = self.cards[self.flipped[1]]
                
                if card1['value'] == card2['value']:
                    # Match found
                    self.matched.extend(self.flipped)
                    self.flipped = []
                    self.match_sound.play()
                    
                    # Check for game over
                    if len(self.matched) == len(self.cards):
                        self.game_over = True
                else:
                    # No match
                    self.last_flip_time = pygame.time.get_ticks()
                    self.fail_sound.play()
    
    def handle_click(self, pos):
        """Handle mouse click at position"""
        for card in self.cards:
            if card['rect'].collidepoint(pos):
                self.handle_card_selection(card['index'])
                break
    
    def update(self):
        if self.paused:
            return
            
        # Check if we should flip cards back
        current_time = pygame.time.get_ticks()
        if len(self.flipped) == 2 and current_time - self.last_flip_time >= self.flip_delay:
            self.flipped = []
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Draw cards
        for card in self.cards:
            # Determine card color
            if card['index'] in self.matched:
                color = self.MATCHED_COLOR
            elif card['index'] in self.flipped:
                color = self.CARD_FRONT
            else:
                color = self.CARD_BACK
            
            # Draw card background
            pygame.draw.rect(self.screen, color, card['rect'])
            
            # Highlight selected card for keyboard navigation
            if not self.paused and card['index'] == (self.selected_row * self.GRID_SIZE + self.selected_col):
                pygame.draw.rect(self.screen, self.WHITE, card['rect'], 3)
            
            # Draw card value if it's flipped or matched
            if card['index'] in self.flipped or card['index'] in self.matched:
                font = pygame.font.Font(None, self.CARD_WIDTH // 2)
                text = font.render(str(card['value']), True, self.BLACK)
                text_rect = text.get_rect(center=card['rect'].center)
                self.screen.blit(text, text_rect)
        
        # Draw moves counter
        moves_text = pygame.font.Font(None, 36).render(f"Moves: {self.moves}", True, self.WHITE)
        self.screen.blit(moves_text, (20, 20))
        
        # Draw instructions
        if not self.game_over:
            instructions = "Arrow Keys/WASD to move  |  Enter/Space to select"
            inst_text = pygame.font.Font(None, 28).render(instructions, True, self.GRAY)
            inst_rect = inst_text.get_rect(center=(self.width//2, self.height - 30))
            self.screen.blit(inst_text, inst_rect)
        
        # Draw game over message
        if self.game_over:
            font = pygame.font.Font(None, 64)
            text = font.render(f"You Won in {self.moves} moves!", True, self.WHITE)
            text_rect = text.get_rect(center=(self.width//2, 50))
            self.screen.blit(text, text_rect)
            
            restart_text = pygame.font.Font(None, 36).render("Press R to Play Again", True, self.GRAY)
            restart_rect = restart_text.get_rect(center=(self.width//2, self.height - 50))
            self.screen.blit(restart_text, restart_rect)
        
        if self.paused:
            self.draw_pause_menu()
        
        pygame.display.flip()