"""
Game Manager - Orchestrates game logic and data flow
"""
from time import time
from data.character_data import CharacterDatabase
from data.location_data import LocationDatabase
from data.HeroData import CharacterParser
from game.game_state import GameState
from Components.AIConnection import AIConnection
from Components.ChatterSystem import ChatterSystem
from ui.Dice_ui import DiceUI
import json

with open('config.json', 'r') as f:
    config = json.load(f)

class GameManager:
    def __init__(self, console):
        self.currenttalk_npc = None
        self.console = console
        self.ai = AIConnection()
        self.db = CharacterDatabase()
        self.locdb = LocationDatabase()
        self.dice = DiceUI(dice=config["dice"], die_size=200)
        self.chat = ChatterSystem(self.console.print_to_chat)
        self.phraser = CharacterParser("D:\\Projects\\XII Project\\Data CSVs\\Hero.csv",
                                       "D:\\Projects\\XII Project\\Data CSVs\\Item_Lookup.csv",
                                       "D:\\Projects\\XII Project\\Data CSVs\\Skill_Lookup.csv")
        self.state = GameState()
        
        self.chat.load_scene(self.locdb.get_location_by_id(self.phraser.get_location()).to_dict(),self.db.get_characters_by_location_id(self.phraser.get_location()).to_dict('records'))

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
    def normalize_response(data):
        """Handle both direct dict and any wrapper format (response, action, etc.)"""
    
        if not isinstance(data, dict):
            return data
    
        # Check if there's exactly one key and it contains a list
        if len(data) == 1:
            key = list(data.keys())[0]
            value = data[key]
        
            # If the value is a list of [key, value] pairs, convert it
            if isinstance(value, list) and all(isinstance(item, list) and len(item) == 2 for item in value):
                return {item[0]: item[1] for item in value}
    
            # Otherwise, return as-is (already in correct format)
        return data
    def handle_player_input(self, text):
        """Process player text input"""
        self.console.print_to_chat(text, "Player")
        
        # Process command (to be expanded)
        if text.lower() in ["help", "?"]:
            self.show_help()
        elif not self.currenttalk_npc == None:
            action_result = self.ai.Chat(self.currenttalk_npc, text)
            action_result = GameManager.normalize_response(action_result)
            impression = action_result.get("Impression", 0)
            done = action_result.get("Done", False)

            # Remove system keys
            action_result.pop("Impression", None)
            action_result.pop("Done", None)

            #    Print NPC dialogue/actions
            for key, value in action_result.items():
                self.console.print_to_chat(f"{value}", f"{key}")
            # Impression feedback with better thresholds
            if impression >= 5:
               self.console.print_to_chat(f"{self.currenttalk_npc['name']} seems delighted! (Impression +{impression})", "SYSTEM")
            elif impression > 3:
                self.console.print_to_chat(f"{self.currenttalk_npc['name']} seems to like you more. (Impression +{impression})", "SYSTEM")
            elif impression > 0:
                self.console.print_to_chat(f"{self.currenttalk_npc['name']} seems to warm up to you. (Impression +{impression})", "SYSTEM")
            elif impression == 0:
                self.console.print_to_chat(f"{self.currenttalk_npc['name']} seems indifferent. (Impression {impression})", "SYSTEM")
            elif impression > -3:
                self.console.print_to_chat(f"{self.currenttalk_npc['name']} seems annoyed. (Impression {impression})", "SYSTEM")
            else:  # impression <= -3
                self.console.print_to_chat(f"{self.currenttalk_npc['name']} seems angry! (Impression {impression})", "SYSTEM")

            # End conversation if done
            if done:
                self.console.print_to_chat(f"You end the conversation with {self.currenttalk_npc['name']}.", "SYSTEM")
                self.currenttalk_npc = None
                            
        else:
            self.currenttalk_npc =self.chat.handle_input(text)
            
    
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
        self.console.print_to_chat(self.console.get_chat_history(), "ACTION")
    
    def show_inventory(self):
        """Display inventory"""
        self.console.print_to_chat(f'{self.ai.extract_roleplay_guide("D:\\Projects\\XII Project\\data.txt")}', "INVENTORY")
    
    def show_stats(self):
        """Display player stats"""
        self.console.print_to_chat(
            f"Health: {self.state.player_health} | "
            f"Gold: {self.state.player_gold}",
            "STATS"
        )
    # Action button handlers
    def action_talk(self):
        """Handle talk action"""
        self.chat.show_menu()
    
    def action_trade(self):
        """Handle trade action"""
        self.console.print_to_chat(self.console.get_chat_history(), "ACTION")
    
    def action_gift(self):
        """Handle gift action"""
        self.console.print_to_chat(f"{self.db.get_characters_by_location_id(self.phraser.get_location()).to_dict('records')}", "ACTION")
    
    def action_leave(self):
        """Handle leave action"""
        self.console.print_to_chat(f"{self.phraser.format_for_ai_gm()}","ACTION")
    
    def action_examine(self):
        """Handle examine action"""
        s= self.dice.roll_die("1d20")
        self.console.print_to_chat(f"You look around carefully... rolled {s}", "ACTION")
    
    def action_rest(self):
        """Handle rest action"""
        self.console.print_to_chat("You take a moment to rest...", "ACTION")
        self.state.player_health = min(100, self.state.player_health + 10)
        self._update_info_bulletin()
    
    def action_search(self):
        """Handle search action"""
        self.console.print_to_chat("".join(self.ai.characterProfiler(self.phraser.format_for_ai_gm())),"ACTION")
    
    def action_wait(self):
        """Handle wait action"""
        self.console.print_to_chat("Time passes...", "ACTION")
        self.state.advance_turn()
        self._update_info_bulletin()