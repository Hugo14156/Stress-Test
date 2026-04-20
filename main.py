"""
Stress Test - A 2D train logistics game.

Entry point for the application. Initialises and runs the main game loop.
"""

from app.game import Game

if __name__ == "__main__":
    game = Game()
    game.run_game()
