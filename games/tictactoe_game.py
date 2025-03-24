import pygame
from utils.game_base import GameBase

class TicTacToeGame(GameBase):
    def __init__(self, board_size=3):
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRID_COLOR = (128, 128, 128)
        self.HIGHLIGHT_COLOR = (100, 100, 255)
        self.WIN_HIGHLIGHT_COLOR = (0, 255, 0)
        self.X_COLOR = (255, 100, 100)
        self.O_COLOR = (100, 255, 100)
        
        self.board_size = board_size
        self.selected_cell = [0, 0]  # For keyboard navigation
        self.paused = False
        self.game_font = None  # Will be set in reset_board
        
        super().__init__(title="Tic Tac Toe")
        self.setup_size_selection()
        self.size_selected = False  # Flag to track if size has been selected
        
    def setup_size_selection(self):
        """Initialize the size selection menu"""
        self.size_options = [3, 4, 5]
        self.selected_size = 0  # Index in size_options
        self.menu_font = pygame.font.Font(None, 48)
        
    def handle_size_selection(self, events):
        """Handle input for size selection menu"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_size = (self.selected_size - 1) % len(self.size_options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_size = (self.selected_size + 1) % len(self.size_options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.board_size = self.size_options[self.selected_size]
                    if self.board_size == 3:
                        self.win_condition = 3
                    else:
                        self.win_condition = 4  # For 4x4 and 5x5, need 4 in a row to win
                    self.size_selected = True
                    self.reset_board()
    
    def draw_size_selection(self):
        """Draw the size selection menu"""
        self.screen.fill(self.BLACK)
        title = self.menu_font.render("Select Board Size", True, self.WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title, title_rect)
        
        for i, size in enumerate(self.size_options):
            color = self.WHITE if i == self.selected_size else self.GRID_COLOR
            text = self.menu_font.render(f"{size}x{size}", True, color)
            rect = text.get_rect(center=(self.width // 2, 250 + i * 60))
            
            # Draw selection indicator
            if i == self.selected_size:
                pygame.draw.rect(self.screen, color, rect.inflate(20, 10), 2)
                
            self.screen.blit(text, rect)
        
        # Draw instructions
        instruction_font = pygame.font.Font(None, 32)
        instructions = instruction_font.render("Use UP/DOWN arrows to select, ENTER to start", True, self.GRID_COLOR)
        inst_rect = instructions.get_rect(center=(self.width // 2, self.height - 100))
        self.screen.blit(instructions, inst_rect)

    def handle_pause_menu(self, events):
        """Handle pause menu events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = False
                elif event.key == pygame.K_r:
                    self.reset_game()
                    self.paused = False

    def draw_pause_menu(self):
        """Draw the pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Menu text
        pause_font = pygame.font.Font(None, 48)
        text_color = self.WHITE
        
        # Draw "PAUSED" text
        paused_text = pause_font.render("PAUSED", True, text_color)
        text_rect = paused_text.get_rect(center=(self.width // 2, self.height // 2 - 40))
        self.screen.blit(paused_text, text_rect)
        
        # Draw instructions
        instruction_font = pygame.font.Font(None, 32)
        instructions = [
            "Press ESC to resume",
            "Press R to restart",
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, text_color)
            rect = text.get_rect(center=(self.width // 2, self.height // 2 + 20 + i * 40))
            self.screen.blit(text, rect)

    def reset_board(self):
        """Initialize or reset board, game state and recalc grid dimensions."""
        # Create an empty board based on board size
        self.board = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.winning_cells = []  # For highlighting winning combination
        
        # Calculate cell and grid sizes based on current board size
        # Using a margin factor to leave some padding on the screen
        self.cell_size = min(self.width, self.height) // (self.board_size + 1)
        self.grid_size = self.cell_size * self.board_size
        self.grid_x = (self.width - self.grid_size) // 2
        self.grid_y = (self.height - self.grid_size) // 2
        
        # Initialize the game font with appropriate size
        self.game_font = pygame.font.Font(None, self.cell_size // 2)
    
    def change_grid_size(self, new_size):
        """Change the board size and reset the game."""
        self.board_size = new_size
        self.win_condition = new_size  # Modify this if you want a different win condition
        self.reset_board()
        # Update font size based on new cell size
        self.game_font = pygame.font.Font(None, self.cell_size // 2)
    
    def reset_game(self):
        """Reset the game (board and state)."""
        self.reset_board()
    
    def get_valid_moves(self):
        """Return a list of tuples indicating empty cells."""
        moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == '':
                    moves.append((row, col))
        return moves
    
    def ai_move(self):
        """A simple stub for an AI move. Replace this logic for a smarter AI."""
        valid_moves = self.get_valid_moves()
        if valid_moves:
            row, col = valid_moves[0]  # For now, simply take the first available move
            self.make_move(row, col)
    
    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return True
            
            if not self.size_selected:
                self.handle_size_selection(events)
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif not self.game_over and not self.paused:
                    # Keyboard navigation
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.selected_cell[1] = (self.selected_cell[1] - 1) % self.board_size
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.selected_cell[1] = (self.selected_cell[1] + 1) % self.board_size
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.selected_cell[0] = (self.selected_cell[0] - 1) % self.board_size
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.selected_cell[0] = (self.selected_cell[0] + 1) % self.board_size
                    # Space or Enter to make a move
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.make_move(self.selected_cell[0], self.selected_cell[1])
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                
                # Example keys to change grid sizes:
                elif event.key == pygame.K_3:
                    self.change_grid_size(3)
                elif event.key == pygame.K_4:
                    self.change_grid_size(4)
                elif event.key == pygame.K_5:
                    self.change_grid_size(5)
                    
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.paused:
                x, y = event.pos
                # Convert mouse position to board coordinates
                board_x = (x - self.grid_x) // self.cell_size
                board_y = (y - self.grid_y) // self.cell_size
                self.make_move(board_y, board_x)
                
        if self.paused:
            self.handle_pause_menu(events)
        
        return False
    
    def make_move(self, row, col):
        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == '':
            self.board[row][col] = self.current_player
            if self.check_winner():
                self.winner = self.current_player
                self.game_over = True
            elif self.is_board_full():
                self.game_over = True
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                # Uncomment the following line to have AI move when playing as 'O'
                # if self.current_player == 'O':
                #     self.ai_move()
    
    def check_winner(self):
        """Check for winning combinations with variable win condition length."""
        bs = self.board_size
        win_len = self.win_condition

        # Check rows
        for row in range(bs):
            for col in range(bs - win_len + 1):
                if self.board[row][col] != '':
                    if all(self.board[row][col+i] == self.board[row][col] for i in range(win_len)):
                        self.winning_cells = [(row, col+i) for i in range(win_len)]
                        return True

        # Check columns
        for col in range(bs):
            for row in range(bs - win_len + 1):
                if self.board[row][col] != '':
                    if all(self.board[row+i][col] == self.board[row][col] for i in range(win_len)):
                        self.winning_cells = [(row+i, col) for i in range(win_len)]
                        return True

        # Check diagonals (top-left to bottom-right)
        for row in range(bs - win_len + 1):
            for col in range(bs - win_len + 1):
                if self.board[row][col] != '':
                    if all(self.board[row+i][col+i] == self.board[row][col] for i in range(win_len)):
                        self.winning_cells = [(row+i, col+i) for i in range(win_len)]
                        return True

        # Check anti-diagonals (top-right to bottom-left)
        for row in range(bs - win_len + 1):
            for col in range(win_len - 1, bs):
                if self.board[row][col] != '':
                    if all(self.board[row+i][col-i] == self.board[row][col] for i in range(win_len)):
                        self.winning_cells = [(row+i, col-i) for i in range(win_len)]
                        return True

        return False
    
    def is_board_full(self):
        return all(cell != '' for row in self.board for cell in row)
    
    def draw(self):
        if not self.size_selected:
            self.draw_size_selection()
            pygame.display.flip()
            return

        self.screen.fill(self.BLACK)
        
        # Draw grid lines
        for i in range(self.board_size + 1):
            # Vertical lines
            pygame.draw.line(self.screen, self.GRID_COLOR,
                             (self.grid_x + i * self.cell_size, self.grid_y),
                             (self.grid_x + i * self.cell_size, self.grid_y + self.grid_size), 2)
            # Horizontal lines
            pygame.draw.line(self.screen, self.GRID_COLOR,
                             (self.grid_x, self.grid_y + i * self.cell_size),
                             (self.grid_x + self.grid_size, self.grid_y + i * self.cell_size), 2)
        
        # Draw markers and highlights
        for y in range(self.board_size):
            for x in range(self.board_size):
                cell_rect = pygame.Rect(
                    self.grid_x + x * self.cell_size,
                    self.grid_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Highlight selected cell (if game is not over)
                if not self.game_over and [y, x] == self.selected_cell:
                    pygame.draw.rect(self.screen, self.HIGHLIGHT_COLOR, cell_rect, 3)
                
                # Highlight winning cells if game is over
                if self.game_over and self.winner and (y, x) in self.winning_cells:
                    pygame.draw.rect(self.screen, self.WIN_HIGHLIGHT_COLOR, cell_rect, 5)
                
                cell = self.board[y][x]
                if cell:
                    color = self.X_COLOR if cell == 'X' else self.O_COLOR
                    text = self.game_font.render(cell, True, color)
                    text_rect = text.get_rect(center=(
                        self.grid_x + x * self.cell_size + self.cell_size // 2,
                        self.grid_y + y * self.cell_size + self.cell_size // 2
                    ))
                    self.screen.blit(text, text_rect)
        
        # Draw messages
        if self.game_over:
            if self.winner:
                msg = f"Player {self.winner} wins!"
            else:
                msg = "It's a tie!"
            game_over_text = self.game_font.render(msg, True, self.WHITE)
            restart_text = self.game_font.render("Press R to Restart", True, self.GRID_COLOR)
            game_over_rect = game_over_text.get_rect(center=(self.width // 2, 50))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height - 50))
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
        else:
            turn_text = self.game_font.render(f"Player {self.current_player}'s Turn", True, self.WHITE)
            controls_text = self.game_font.render("Arrows/WASD: move, Space/Enter: select", True, self.GRID_COLOR)
            turn_rect = turn_text.get_rect(center=(self.width // 2, 50))
            controls_rect = controls_text.get_rect(center=(self.width // 2, self.height - 50))
            self.screen.blit(turn_text, turn_rect)
            self.screen.blit(controls_text, controls_rect)
        
        if self.paused:
            self.draw_pause_menu()
        
        pygame.display.flip()
