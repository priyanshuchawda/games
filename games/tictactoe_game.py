import pygame
from utils.game_base import GameBase

class TicTacToeGame(GameBase):
    def __init__(self):
        super().__init__(title="Tic Tac Toe")
        
        # Game board
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        
        # Calculate cell size based on screen dimensions
        self.cell_size = min(self.width, self.height) // 4
        self.grid_size = self.cell_size * 3
        self.grid_x = (self.width - self.grid_size) // 2
        self.grid_y = (self.height - self.grid_size) // 2
        
        # Colors
        self.GRID_COLOR = (200, 200, 200)
        self.X_COLOR = (66, 133, 244)  # Blue
        self.O_COLOR = (52, 168, 83)   # Green
        self.HIGHLIGHT_COLOR = (128, 128, 128)  # Gray for selection
        
        # Font
        self.game_font = pygame.font.Font(None, self.cell_size // 2)
        
        # Keyboard navigation
        self.selected_cell = [0, 0]  # [row, col]
        
    def handle_events(self):
        # Handle pause and fullscreen from parent
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif not self.game_over and not self.paused:
                    # Keyboard navigation
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.selected_cell[1] = (self.selected_cell[1] - 1) % 3
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.selected_cell[1] = (self.selected_cell[1] + 1) % 3
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.selected_cell[0] = (self.selected_cell[0] - 1) % 3
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.selected_cell[0] = (self.selected_cell[0] + 1) % 3
                    # Space or Enter to make a move
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.make_move(self.selected_cell[0], self.selected_cell[1])
                elif event.key == pygame.K_r and self.game_over:
                    self.__init__()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.paused:
                x, y = event.pos
                # Convert mouse position to grid coordinates
                board_x = (x - self.grid_x) // self.cell_size
                board_y = (y - self.grid_y) // self.cell_size
                self.make_move(board_y, board_x)
                
        if self.paused:
            self.handle_pause_menu(events)
        
        return False
    
    def make_move(self, row, col):
        # Check if move is valid
        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == '':
            self.board[row][col] = self.current_player
            if self.check_winner():
                self.winner = self.current_player
                self.game_over = True
            elif self.is_board_full():
                self.game_over = True
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def check_winner(self):
        # Check rows, columns and diagonals
        for i in range(3):
            if (self.board[i][0] == self.board[i][1] == self.board[i][2] != '' or
                self.board[0][i] == self.board[1][i] == self.board[2][i] != ''):
                return True
        
        if (self.board[0][0] == self.board[1][1] == self.board[2][2] != '' or
            self.board[0][2] == self.board[1][1] == self.board[2][0] != ''):
            return True
        
        return False
    
    def is_board_full(self):
        return all(cell != '' for row in self.board for cell in row)
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Draw grid lines
        for i in range(4):
            # Vertical lines
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (self.grid_x + i * self.cell_size, self.grid_y),
                           (self.grid_x + i * self.cell_size, self.grid_y + self.grid_size), 2)
            # Horizontal lines
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (self.grid_x, self.grid_y + i * self.cell_size),
                           (self.grid_x + self.grid_size, self.grid_y + i * self.cell_size), 2)
        
        # Draw X's and O's and highlight selected cell
        for y in range(3):
            for x in range(3):
                cell_rect = pygame.Rect(
                    self.grid_x + x * self.cell_size,
                    self.grid_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Highlight selected cell
                if not self.game_over and [y, x] == self.selected_cell:
                    pygame.draw.rect(self.screen, self.HIGHLIGHT_COLOR, cell_rect, 3)
                
                cell = self.board[y][x]
                if cell:
                    color = self.X_COLOR if cell == 'X' else self.O_COLOR
                    text = self.game_font.render(cell, True, color)
                    text_rect = text.get_rect(center=(
                        self.grid_x + x * self.cell_size + self.cell_size // 2,
                        self.grid_y + y * self.cell_size + self.cell_size // 2
                    ))
                    self.screen.blit(text, text_rect)
        
        # Draw game over message
        if self.game_over:
            if self.winner:
                text = f"Player {self.winner} wins!"
            else:
                text = "It's a tie!"
            
            game_over_text = self.game_font.render(text, True, self.WHITE)
            restart_text = self.game_font.render("Press R to Restart", True, self.GRAY)
            
            game_over_rect = game_over_text.get_rect(center=(self.width // 2, 50))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height - 50))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
        else:
            # Show current player's turn and controls
            turn_text = self.game_font.render(f"Player {self.current_player}'s Turn", True, self.WHITE)
            controls_text = self.game_font.render("Arrow Keys/WASD to move, Space/Enter to select", True, self.GRAY)
            
            turn_rect = turn_text.get_rect(center=(self.width // 2, 50))
            controls_rect = controls_text.get_rect(center=(self.width // 2, self.height - 50))
            
            self.screen.blit(turn_text, turn_rect)
            self.screen.blit(controls_text, controls_rect)
        
        if self.paused:
            self.draw_pause_menu()
        
        pygame.display.flip()