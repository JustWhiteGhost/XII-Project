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

    def on_closing():
        game.session_tracker.export_session_report()
        game.session_tracker.save_session_json()
        root.quit()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
