"""
Game Manager - Orchestrates game logic and data flow
"""
from data.character_data import CharacterDatabase
from data.HeroData import CharacterParser
from game.game_state import GameState
from ui.Dice_ui import DiceUI
import json

with open('config.json', 'r') as f:
    config = json.load(f)

class GameManager:
    def __init__(self, console):
        self.console = console
        self.db = CharacterDatabase()
        self.dice = DiceUI(dice=config["dice"], die_size=200)
        self.phraser = CharacterParser("D:\\Projects\\XII Project\\Data CSVs\\Hero.csv",
                                       "D:\\Projects\\XII Project\\Data CSVs\\Item_Lookup.csv",
                                       "D:\\Projects\\XII Project\\Data CSVs\\Skill_Lookup.csv")
        self.state = GameState()
        
        # Set up console callbacks
        self.console.set_input_callback(self.handle_player_input)
    
    def start_game(self):
        """Initialize and start the game"""
        self.console.print_to_chat("Welcome to Fog-Shrouded Chronicles!")
        self.console.print_to_chat("A mysterious fog has descended upon the realm...")
        
        # Setup initial UI
        self._setup_navigation()
        self._setup_actions()
        self._update_displays()
    
    def handle_player_input(self, text):
        """Process player text input"""
        self.console.print_to_chat(text, "Player")
        
        # Process command (to be expanded)
        if text.lower() in ["help", "?"]:
            self.show_help()
        else:
            self.console.print_to_chat(
                "Input received. Game logic to be implemented.",
                "SYSTEM"
            )
    
    def show_help(self):
        """Display help information"""
        help_text = (
            "Commands:\n"
            "- Use buttons to navigate and interact\n"
            "- Type messages to communicate\n"
            "- Click character names to view details"
        )
        self.console.print_to_chat(help_text, "HELP")
    
    def _setup_navigation(self):
        """Configure navigation buttons"""
        nav_buttons = [
            ("Character", self.show_character_info),
            ("Location", self.show_location_info),
            ("Inventory", self.show_inventory),
            ("Stats", self.show_stats)
        ]
        self.console.set_navigation_buttons(nav_buttons)
    
    def _setup_actions(self):
        """Configure action buttons"""
        action_buttons = [
            ("Talk", lambda: self.action_talk()),
            ("Trade", lambda: self.action_trade()),
            ("Gift", lambda: self.action_gift()),
            ("Leave", lambda: self.action_leave()),
            ("Examine", lambda: self.action_examine()),
            ("Rest", lambda: self.action_rest()),
            ("Search", lambda: self.action_search()),
            ("Wait", lambda: self.action_wait())
        ]
        self.console.set_action_buttons(action_buttons)
    
    def _update_displays(self):
        """Update all display panels"""
        self._update_profile()
        self._update_info_bulletin()
    
    def _update_profile(self):
        """Update character profile display"""
        if self.state.current_character:
            char = self.state.current_character
            profile = (
                f"{char['name']}\n"
                f"Age: {char['age']}\n"
                f"Class: {char['class']}\n"
                f"Race: {char['race']}\n"
                f"Level: {char['level']}\n"
                f"Player: {char['player']}"
            )
        else:
            profile = "No character selected"
        
        self.console.update_profile(profile)
    
    def _update_info_bulletin(self):
        """Update info bulletin display"""
        info = (
            f"Turn: {self.state.turn_count}\n"
            f"Location: {self.state.current_location or 'Unknown'}\n"
            f"Time: {self.state.time_of_day}\n"
            f"Weather: Foggy\n"
            f"\n"
            f"Gold: {self.state.player_gold}\n"
            f"Health: {self.state.player_health}/100"
        )
        self.console.update_info_bulletin(info)
    
    # Navigation button actions
    def show_character_info(self):
        """Display character information"""
        self.console.print_to_chat("Opening character panel...", "SYSTEM")
        # Load first character as example
        chars = self.phraser.get_basic_info()
        if chars:
            self.state.current_character = chars
            self._update_profile()
    
    def show_location_info(self):
        """Display location information"""
        self.console.print_to_chat("Location: The Foggy Inn", "SYSTEM")
    
    def show_inventory(self):
        """Display inventory"""
        self.console.print_to_chat("Inventory: Empty", "SYSTEM")
    
    def show_stats(self):
        """Display player stats"""
        self.console.print_to_chat(
            f"Health: {self.state.player_health} | "
            f"Gold: {self.state.player_gold}",
            "STATS"
        )
    # D20 check handler
    def perform_d20_check(self, mod: int, bonus: int = 0, difficulty: int = 10) -> bool:
        """Perform a D20 check against a difficulty"""
        roll = self.dice.roll_die("1d20")
        total = roll + mod + bonus
        success = total >= difficulty
        return {"roll": roll, "total": total, "success": success}
    #Attack Roll handler
    def attack_roll(self, character, weapon, target_ac):
        dex_mod = character['dexterity_mod']["modifier"]
        attack_bonus = weapon["damage_bonus"]

        return self.perform_d20_check(mod=dex_mod, bonus=attack_bonus, difficulty=target_ac)
    # Action button handlers
    def action_talk(self):
        """Handle talk action"""
        result = self.dice.roll_die(dice="4d20")
        self.console.print_to_chat(f"You engage in conversation... Rolled a {result}", "ACTION")
    
    def action_trade(self):
        """Handle trade action"""
        self.console.print_to_chat(self.console.get_chat_history(), "ACTION")
    
    def action_gift(self):
        """Handle gift action"""
        self.console.print_to_chat("Select an item to gift...", "ACTION")
    
    def action_leave(self):
        """Handle leave action"""
        self.console.print_to_chat(f"{self.phraser.get_weapons()}","ACTION")
    
    def action_examine(self):
        """Handle examine action"""
        self.console.print_to_chat("You look around carefully...", "ACTION")
    
    def action_rest(self):
        """Handle rest action"""
        self.console.print_to_chat("You take a moment to rest...", "ACTION")
        self.state.player_health = min(100, self.state.player_health + 10)
        self._update_info_bulletin()
    
    def action_search(self):
        """Handle search action"""
        self.console.print_to_chat("You search the area...", "ACTION")
    
    def action_wait(self):
        """Handle wait action"""
        self.console.print_to_chat("Time passes...", "ACTION")
        self.state.advance_turn()
        self._update_info_bulletin()