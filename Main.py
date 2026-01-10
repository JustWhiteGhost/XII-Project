"""
Main entry point for Fog-Shrouded Chronicles RPG
"""
import tkinter as tk
from ui.console import RetroRPGConsole
from game.game_manager import GameManager

def main():
    root = tk.Tk()
    console = RetroRPGConsole(root)
    game = GameManager(console)
    game.start_game()
    root.mainloop()


if __name__ == "__main__":
    main()
