import pygame
import sys
import os
import subprocess
from utils.game_base import GameBase

class PacmanGame(GameBase):
    def __init__(self):
        super().__init__(title="Pacman")
    
    def setup_display(self):
        # Set icon for the Pacman game window
        try:
            icon_path = os.path.join('assets', 'images', 'pacman.png')
            if os.path.exists(icon_path):
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Could not load Pacman icon: {e}")
        
        # Set proper caption
        pygame.display.set_caption("Pacman")
    
    def run(self):
        # Close the current pygame window to avoid conflicts
        pygame.display.quit()
        
        # Get path to the run.py in the Pacman_main directory
        run_script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Pacman_main', 'run.py')
        
        try:
            # Run the original Pacman game script as a separate process
            print(f"Launching Pacman from: {run_script_path}")
            process = subprocess.Popen([sys.executable, run_script_path], 
                                      cwd=os.path.dirname(run_script_path))
            # Wait for the process to complete
            process.wait()
        except Exception as e:
            print(f"Error launching Pacman game: {e}")
        finally:
            # Reinitialize pygame display for the launcher
            pygame.display.init()
            self.setup_display()