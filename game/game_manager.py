"""  
Game Manager - Orchestrates game logic and data flow
"""
from Components.DataVisualizer import DataVisualizer
from Components.RelationshipSystem import RelationshipSystem
from data.character_data import CharacterDatabase
from data.location_data import LocationDatabase
from data.HeroData import CharacterParser
from game.game_state import GameState
from Components.AIConnection import AIConnection
from Components.ChatterSystem import ChatterSystem
from ui.Dice_ui import DiceUI
from Components.TradeSystem import TradeSystem
from Components.TravelSystem import TravelSystem
from Components.Analytics import RPGAnalytics, AnalyticsViewer
from Components.SessionTracker import SessionTracker, SessionDashboard
from Config.Paths import HERO_CSV, ITEM_CSV, SKILL_CSV, CHARACTER_CSV, LOCATION_CSV, LOCATION_LOCKS_CSV
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
        self.trade_mode = False 
        self.gift_mode = False
        self.menu_mode = False   
        self.travel_mode = False
        self.available_travel_locations = []
        self.session_tracker = SessionTracker()
        self.dice = DiceUI(dice=config["dice"], die_size=200)
        self.chat = ChatterSystem(self.console.print_to_chat)
        self.phraser = CharacterParser(str(HERO_CSV),
                                       str(ITEM_CSV),
                                       str(SKILL_CSV))
        self.trade = TradeSystem(
            items_csv_path=str(ITEM_CSV),
            trade_log_path="saves/trade_history.csv"
        )
        self.relationships = RelationshipSystem(
            characters_csv_path=str(CHARACTER_CSV),
            relationship_log_path="saves/relationship_history.csv"
        )
        self.travel = TravelSystem(
            locations_csv_path=str(LOCATION_CSV),
            location_locks_csv_path=str(LOCATION_LOCKS_CSV),
            items_csv_path=str(ITEM_CSV)
        )
        self.visualizer = DataVisualizer(parent_window=console.root)
        
        self.state = GameState()
        self.analytics = RPGAnalytics(
            str(CHARACTER_CSV),
            str(LOCATION_CSV)
        )
        self.chat.load_scene(self.locdb.get_location_by_id(self.phraser.get_location()).to_dict(),self.db.get_characters_by_location_id(self.phraser.get_location()).to_dict('records'))

        # Set up console callbacks
        self.console.set_input_callback(self.handle_player_input)
        player_currency = self.phraser.get_all_inventory()['currency']
        self.player_gold_cp = self.trade.parse_currency(player_currency)
    
    def start_game(self):
        """Initialize and start the game"""
        self.console.print_to_chat("Welcome to Fog-Shrouded Chronicles!")
        self.console.print_to_chat("A mysterious fog has descended upon the realm...")
        
        # Setup initial UI
        self._setup_navigation()
        self._setup_actions()
        self._update_displays()
    def normalize_response(self, data):
        """Handle response format normalization and flatten nested dicts."""
        if not isinstance(data, dict):
            return data
    
        # Handle list of [key, value] pairs format
        if len(data) == 1:
            key = list(data.keys())[0]
            value = data[key]

            if isinstance(value, list) and all(isinstance(item, list) and len(item) == 2 for item in value):
                return {item[0]: item[1] for item in value}

        # Flatten nested single-key dictionaries
        # Example: {'Action': {'text': 'Leans in'}} -> {'Action': 'Leans in'}
        flattened = {}
        for key, value in data.items():
            if isinstance(value, dict) and len(value) == 1:
                # Get the inner value from single-key dict
                inner_value = list(value.values())[0]
                flattened[key] = inner_value
            else:
                flattened[key] = value
    
        return flattened
    def handle_player_input(self, text):
        """Process player text input with mode handling."""
        self.console.print_to_chat(text, "Player")

        # Help command
        if text.lower() in ["help", "?"]:
            self.show_help()
            return
    
        # Exit commands for special modes
        if text.lower() in ["exit trade", "cancel", "back", "exit"]:
            if self.trade_mode:
                self._exit_trade_mode()
                return
            if self.gift_mode:
                self._exit_gift_mode()
                return
            if self.menu_mode:
                self.menu_mode = False
                self.console.print_to_chat("Closed conversation menu.", "SYSTEM")
                return
            if self.travel_mode:
                self.travel_mode = False
                self.available_travel_locations = []
                self.console.print_to_chat("Closed travel menu.", "SYSTEM")
                return
    
        # MENU MODE: Select NPC from list
        if self.menu_mode:
            selected_npc = self.chat.handle_input(text)
            if selected_npc:
                self.currenttalk_npc = selected_npc
                self.menu_mode = False
            return
    
        # TRADE MODE: Process trade commands
        if self.trade_mode:
            self.process_trade_command(text)
            return

        # GIFT MODE: Process gift commands
        if self.gift_mode:
            if text.lower().startswith('gift '):
                item_id = text.split()[1].upper()
                self.process_gift(item_id)
                self.gift_mode = False
            else:
                self.console.print_to_chat(
                    "Use format: 'gift [item_id]' or type 'exit' to cancel",
                    "SYSTEM"
                )
            return

        # TRAVEL MODE: Select destination by number
        if self.travel_mode:
            try:
                selection = int(text) - 1
            except ValueError:
                self.console.print_to_chat("Please enter a number to choose a destination.", "SYSTEM")
                return
            if selection < 0 or selection >= len(self.available_travel_locations):
                self.console.print_to_chat("Invalid selection.", "SYSTEM")
                return
            destination = self.available_travel_locations[selection]
            self._attempt_travel(destination)
            return
    
        # CONVERSATION MODE: Talk to NPC
        if self.currenttalk_npc:
            self.console.print_to_chat("[AI-Generated Response]", "SYSTEM")
            action_result = self.ai.Chat(self.currenttalk_npc, text)
            action_result = self.normalize_response(action_result)

            impression = action_result.get("Impression", 0)
            done = action_result.get("Done", False)

            # Remove system keys
            action_result.pop("Impression", None)
            action_result.pop("Done", None)

            # Print dialogue
            for key, value in action_result.items():
                self.console.print_to_chat(f"{value}", f"{key}")

            # Show impression feedback
            if impression >= 5:
                self.console.print_to_chat(
                    f"{self.currenttalk_npc['name']} seems delighted! (Impression +{impression})",
                    "SYSTEM"
                )
            elif impression > 3:
                self.console.print_to_chat(
                    f"{self.currenttalk_npc['name']} seems to like you more. (Impression +{impression})",
                    "SYSTEM"
                )
            elif impression > 0:
                self.console.print_to_chat(
                    f"{self.currenttalk_npc['name']} seems to warm up to you. (Impression +{impression})",
                    "SYSTEM"
                )
            elif impression == 0:
                self.console.print_to_chat(
                    f"{self.currenttalk_npc['name']} seems indifferent. (Impression {impression})",
                    "SYSTEM"
                )
            elif impression > -3:
                self.console.print_to_chat(
                    f"{self.currenttalk_npc['name']} seems annoyed. (Impression {impression})",
                    "SYSTEM"
                )
            else:
                self.console.print_to_chat(
                    f"{self.currenttalk_npc['name']} seems angry! (Impression {impression})",
                    "SYSTEM"
                )

            # Advance turn after successful chat exchange
            self.advance_turn()

            # Log conversation to session tracker
            npc_id = self.currenttalk_npc['unique_id']
            npc_name = self.currenttalk_npc['name']
            total_impression = self.relationships.get_relation(npc_id)
            self.session_tracker.log_conversation(
                npc_name=npc_name,
                npc_id=npc_id,
                impression_change=impression,
                total_impression=total_impression
            )

            # End conversation
            if done:
                self.console.print_to_chat(
                    f"You end the conversation with {self.currenttalk_npc['name']}.",
                    "SYSTEM"
                )
                self.currenttalk_npc = None
        else:
            # Not in conversation - handle menu selection
            response = self.ai.resolve_action(text)
            self.console.print_to_chat(f"{response}", "SYSTEM")

    def _attempt_travel(self, destination: dict):
        """Attempt to travel to a destination, handling locks and keys."""
        loc_id = destination['location_id']
        loc_name = destination['location_name']
        player_inv = self.phraser.get_all_inventory()
        access = self.travel.check_access(loc_id, player_inv)
        
        if not access['can_access']:
            # Check if lockpicking is possible
            lock_info = self.travel.get_lock_info(loc_id)
            if lock_info and str(lock_info.get('can_pick_lock', 'False')).lower() == 'true':
                dc = int(lock_info.get('pick_lock_dc', 15))
                self.console.print_to_chat("You try to pick the lock...", "SYSTEM")
                roll = self.dice.roll_die("1d20")
                self.console.print_to_chat(f"Lockpick attempt roll: {roll} (DC {dc})", "SYSTEM")
                if roll >= dc:
                    self.console.print_to_chat("Success! The lock clicks open.", "SYSTEM")
                else:
                    self.console.print_to_chat(access['message'], "SYSTEM")
                    return
            else:
                self.console.print_to_chat(access['message'], "SYSTEM")
                return
        
        # Perform travel
        self.console.print_to_chat(f"You travel to {loc_name}.", "TRAVEL")
        self.state.current_location = loc_id
        self.travel_mode = False
        self.available_travel_locations = []
        # Load scene for chatter system
        self._load_location_scene(destination)
        # Clear current NPC
        self.currenttalk_npc = None
        # Advance turn
        self.advance_turn()

    def _load_location_scene(self, location_record: dict):
        loc_id = location_record.get('location_id', '')
        print(self.locdb.get_location_by_id(loc_id))
        npcs_df = self.db.get_characters_by_location_id(loc_id)
        npcs = npcs_df.to_dict('records') if npcs_df is not None else []
        self.chat.load_scene(self.locdb.get_location_by_id(loc_id).to_dict(), npcs)

    def show_session_dashboard(self):
        """NEW: Show live session dashboard"""
        self.console.print_to_chat("Opening Session Dashboard...", "SYSTEM")
        SessionDashboard(self.console.root, self.session_tracker)
    
    def determine_action_type(self, text):
        """Helper to categorize actions"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['talk', 'speak', 'ask']):
            return 'talk'
        elif any(word in text_lower for word in ['search', 'look', 'examine']):
            return 'explore'
        elif any(word in text_lower for word in ['attack', 'fight', 'hit']):
            return 'combat'
        else:
            return 'other'
    
    def show_help(self):
        """Show help with new commands."""
        help_text = (
            "=== COMMANDS ===\n"
            "- Use buttons to navigate\n"
            "- Talk to NPCs to start conversations\n"
            "- Trade: 'buy [item_id] [qty]' or 'sell [item_id] [qty]'\n"
            "- Gift: 'gift [item_id]' to give items to NPCs\n"
            "- View Stats: See graphs of your progress\n"
            "- Relationships: See who likes/hates you"
        )
        self.console.print_to_chat(help_text, "HELP")
    
    def _setup_navigation(self):
        """Configure navigation buttons"""
        nav_buttons = [
            ("Character", self.show_character_info),
            ("Location", self.show_location_info),
            ("Session", self.show_session_dashboard),
            ("Analytics", self.show_analytics)
        ]
        self.console.set_navigation_buttons(nav_buttons)
    
    def _setup_actions(self):
        """Configure action buttons"""
        self.default_action_buttons = [
            ("Talk", lambda: self.action_talk()),
            ("Trade", lambda: self.action_trade()),
            ("Gift", lambda: self.action_gift()),
            ("Leave", lambda: self.action_leave()),
            ("Travel", lambda: self.action_travel()),
            ("Inventory", self.show_inventory),
            ("View Stats", self.show_statistics),
            ("Relationships", self.show_relationships),
            ("Analytics", lambda: self.show_analytics())
        ]
        self.console.set_action_buttons(self.default_action_buttons)
    
    def _set_trade_mode_buttons(self):
        """Set action buttons for trade mode"""
        trade_buttons = [
            ("View Stock", self._show_merchant_stock),
            ("Buy Item", self._prompt_buy),
            ("Sell Item", self._prompt_sell),
            ("Exit Trade", self._exit_trade_mode),
            ("Inventory", self.show_inventory)
        ]
        self.console.set_action_buttons(trade_buttons)
    
    def _set_gift_mode_buttons(self):
        """Set action buttons for gift mode"""
        gift_buttons = [
            ("Give Gift", self._prompt_gift),
            ("Exit Gift", self._exit_gift_mode),
            ("Inventory", self.show_inventory)
        ]
        self.console.set_action_buttons(gift_buttons)
    
    def _restore_default_buttons(self):
        """Restore default action buttons"""
        self.console.set_action_buttons(self.default_action_buttons)
    
    def show_analytics(self):
        """NEW METHOD: Open analytics dashboard"""
        self.console.print_to_chat("Opening Analytics Dashboard...", "SYSTEM")
        viewer = AnalyticsViewer(self.console.root, self.analytics)

    
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
    
    # Navigation button actions
    def show_character_info(self):
        """Display character information"""
        self.console.print_to_chat("Opening character panel...", "SYSTEM")
        # Load first character as example
        chars = self.phraser.get_basic_info()
        if chars:
            self.state.current_character = chars
            self._update_displays()
    
    def show_location_info(self):
        """Display location information"""
        self.console.print_to_chat(self.console.get_chat_history(), "ACTION")
    
    def show_inventory(self):
        """Display player inventory"""
        self.console.print_to_chat("\n=== YOUR INVENTORY ===", "INVENTORY")
        
        inventory = self.phraser.get_all_inventory()
        
        # Display currency
        if 'currency' in inventory:
            self.console.print_to_chat(
                f"Gold: {self.trade.format_currency(self.player_gold_cp)}",
                "INVENTORY"
            )
        
        # Display weapons
        if 'weapons' in inventory and inventory['weapons']:
            self.console.print_to_chat("\nWeapons:", "INVENTORY")
            for weapon in inventory['weapons']:
                weapon_name = weapon.get('item_name', weapon.get('item_id', 'Unknown'))
                weapon_dmg = weapon.get('damage', 'N/A')
                self.console.print_to_chat(
                    f"  {weapon_name} - Damage: {weapon_dmg}",
                    "INVENTORY"
                )
        
        # Display armor
        if 'armor' in inventory and inventory['armor']:
            self.console.print_to_chat("\nArmor:", "INVENTORY")
            armor = inventory['armor']
            armor_name = armor.get('item_name', armor.get('item_id', 'Unknown'))
            armor_ac = armor.get('armor_class', 'N/A')
            self.console.print_to_chat(
                f"  {armor_name} - AC: {armor_ac}",
                "INVENTORY"
            )
        
        # Display ammunition
        if 'ammunition' in inventory and inventory['ammunition']:
            self.console.print_to_chat("\nAmmunition:", "INVENTORY")
            for ammo in inventory['ammunition']:
                ammo_name = ammo.get('item_name', ammo.get('item_id', 'Unknown'))
                self.console.print_to_chat(f"  {ammo_name}", "INVENTORY")
        
        # Display equipment
        if 'equipment' in inventory and inventory['equipment']:
            self.console.print_to_chat("\nEquipment:", "INVENTORY")
            for equip in inventory['equipment']:
                equip_name = equip.get('item_name', equip.get('item_id', 'Unknown'))
                self.console.print_to_chat(f"  {equip_name}", "INVENTORY")
        
        # Display consumables
        if 'consumables' in inventory and inventory['consumables']:
            self.console.print_to_chat("\nConsumables:", "INVENTORY")
            for item in inventory['consumables']:
                item_name = item.get('item_name', item.get('item_id', 'Unknown'))
                quantity = item.get('quantity', 1)
                self.console.print_to_chat(
                    f"  {item_name} x{quantity}",
                    "INVENTORY"
                )
        
        # Check if inventory is completely empty
        has_items = any([
            inventory.get('weapons'),
            inventory.get('armor'),
            inventory.get('ammunition'),
            inventory.get('equipment'),
            inventory.get('consumables')
        ])
        
        if not has_items:
            self.console.print_to_chat("\nNo items in inventory.", "INVENTORY")
    
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
        self.menu_mode = True
        self.chat.show_menu()
    
    
    def action_leave(self):
        """Handle leave action"""
        if not self.currenttalk_npc:
            self.console.print_to_chat(
                "You're not in a conversation. Use 'Talk' to select someone to talk to.",
                "SYSTEM"
            )
            return
        
        # End conversation with NPC
        self.console.print_to_chat(
            f"You end the conversation with {self.currenttalk_npc['name']}.",
            "ACTION"
        )
        self.currenttalk_npc = None
        self._restore_default_buttons()
    
    def action_examine(self):
        """Handle examine action"""
        self.console.print_to_chat("[Algorithm-Based Response]", "SYSTEM")
        s= self.dice.roll_die("1d20")
        self.console.print_to_chat(f"You look around carefully... rolled {s}", "ACTION")
    
    def action_rest(self):
        """Handle rest action"""
        self.console.print_to_chat("You take a moment to rest...", "ACTION")
        self.state.player_health = min(100, self.state.player_health + 10)
        self._update_displays()
    
    def action_search(self):
        """Handle search action"""
        self.console.print_to_chat("[AI-Generated Response]", "SYSTEM")
        self.console.print_to_chat("".join(self.ai.characterProfiler(self.phraser.format_for_ai_gm())),"ACTION")
    
    def action_wait(self):
        """Handle wait action"""
        self.console.print_to_chat("Time passes...", "ACTION")
        self.advance_turn()

    def action_travel(self):
        """Show available locations to travel to."""
        # Ensure talk menu doesn't intercept numeric input
        self.menu_mode = False
        player_inv = self.phraser.get_all_inventory()
        accessible_locations = self.travel.get_accessible_locations(
            self.state.current_location,
            player_inv
        )

        if not accessible_locations:
            self.console.print_to_chat(
                "No accessible locations from here.",
                "SYSTEM"
            )
            return

        self.console.print_to_chat(
            "\n=== Available Locations ===",
            "TRAVEL"
        )

        for i, loc in enumerate(accessible_locations, 1):
            loc_name = loc['location_name']
            self.console.print_to_chat(
                f"{i}. {loc_name}",
                "TRAVEL"
            )

        self.console.print_to_chat(
            "\nType the number of the location to travel there.",
            "SYSTEM"
        )
        self.travel_mode = True
        self.available_travel_locations = accessible_locations
    def advance_turn(self):
        self.state.advance_turn()
        self._update_displays()
    def action_trade(self):
        """Open trade menu with current NPC or merchant."""
        if not self.currenttalk_npc:
            self.console.print_to_chat(
                "You need to talk to someone first to trade.",
                "SYSTEM"
            )
            self.menu_mode = True
            self.chat.show_menu()
            return
        
        # Check if NPC is a merchant
        if not self.is_tradeable_npc(self.currenttalk_npc):
            self.console.print_to_chat(
                f"{self.currenttalk_npc['name']} is not a merchant.",
                "SYSTEM"
            )
            return
        
        self.console.print_to_chat(
            f"\n=== Trading with {self.currenttalk_npc['name']} ===",
            "TRADE"
        )
        self.console.print_to_chat(
            f"Your gold: {self.trade.format_currency(self.player_gold_cp)}",
            "TRADE"
        )
        self.console.print_to_chat(
            "Use the action buttons to Buy, Sell, or View Stock.",
            "TRADE"
        )
        
        # Show merchant's available items preview
        self._show_merchant_stock()
        
        # Enable trade mode and set trade buttons
        self.trade_mode = True
        self._set_trade_mode_buttons()
    
    def process_trade_command(self, command: str):
        """
        Process trade commands like 'buy WPN001 1' or 'sell AMO001 20'
        
        Args:
            command: User's trade command
        """
        # Handle stock viewing command
        if command.lower() in ['stock', 'list', 'inventory']:
            self._show_merchant_stock()
            return
        
        parts = command.lower().split()
        
        if len(parts) < 3:
            self.console.print_to_chat(
                "Invalid trade command. Use: buy/sell [item_id] [quantity]",
                "SYSTEM"
            )
            return
        
        action = parts[0]
        item_id = parts[1].upper()
        
        try:
            quantity = int(parts[2])
        except ValueError:
            self.console.print_to_chat("Invalid quantity.", "SYSTEM")
            return
        
        # Get NPC's current relationship
        npc_id = self.currenttalk_npc['unique_id']
        npc_relation = self.relationships.get_relation(npc_id)
        
        # Get player charisma
        charisma_mod = self.phraser.get_ability_scores()['charisma']['modifier']
        
        if action == 'buy':
            # Check if merchant has the item in stock
            npc_id = self.currenttalk_npc['unique_id']
            if not self.trade.check_merchant_has_item(npc_id, item_id, quantity):
                self.console.print_to_chat(
                    f"Merchant doesn't have {quantity}x {item_id} in stock.",
                    "TRADE"
                )
                return
            
            self.console.print_to_chat("[Algorithm-Based Response]", "SYSTEM")
            result = self.trade.buy_item(
                item_id=item_id,
                quantity=quantity,
                player_gold_cp=self.player_gold_cp,
                npc_name=self.currenttalk_npc['name'],
                npc_relation=npc_relation,
                player_charisma_mod=charisma_mod
            )
            
            if result['success']:
                self.player_gold_cp = result['player_gold_after']
                self.console.print_to_chat(result['message'], "TRADE")
                
                # Update player inventory
                self._add_item_to_inventory(item_id, quantity)
                
                # Update merchant inventory (remove sold items)
                self.trade.update_merchant_inventory(npc_id, item_id, -quantity)
                
                # Update currency in character data
                self.phraser.current_character['currency'] = self.trade.format_currency(self.player_gold_cp)
                
                # Save character data to CSV
                if self.phraser.save_current_character():
                    self.console.print_to_chat("Character data saved.", "SYSTEM")
                
                # Small relationship boost for successful trade
                self.relationships.modify_relation(
                    npc_id=npc_id,
                    change=1,
                    interaction_type="trade",
                    location=self.state.current_location,
                    notes=f"Bought {item_id}"
                )
                # Advance turn after successful buy transaction
                self.advance_turn()
            else:
                self.console.print_to_chat(result['message'], "TRADE")
        
        elif action == 'sell':
            # Check if player has the item in inventory
            if not self._player_has_item(item_id, quantity):
                self.console.print_to_chat(
                    f"You don't have {quantity}x {item_id} in your inventory.",
                    "TRADE"
                )
                return
            
            self.console.print_to_chat("[Algorithm-Based Response]", "SYSTEM")
            result = self.trade.sell_item(
                item_id=item_id,
                quantity=quantity,
                player_gold_cp=self.player_gold_cp,
                npc_name=self.currenttalk_npc['name'],
                npc_relation=npc_relation,
                player_charisma_mod=charisma_mod
            )
            
            if result['success']:
                self.player_gold_cp = result['player_gold_after']
                self.console.print_to_chat(result['message'], "TRADE")
                
                # Update player inventory (remove sold items)
                self._remove_item_from_inventory(item_id, quantity)
                
                # Update merchant inventory (add bought items)
                self.trade.update_merchant_inventory(npc_id, item_id, quantity)
                
                # Update currency in character data
                self.phraser.current_character['currency'] = self.trade.format_currency(self.player_gold_cp)
                
                # Save character data to CSV
                if self.phraser.save_current_character():
                    self.console.print_to_chat("Character data saved.", "SYSTEM")
                
                # Small relationship boost
                self.relationships.modify_relation(
                    npc_id=npc_id,
                    change=1,
                    interaction_type="trade",
                    location=self.state.current_location,
                    notes=f"Sold {item_id}"
                )
                self.advance_turn()
            else:
                self.console.print_to_chat(result['message'], "TRADE")
    
    # ==================== GIFT SYSTEM ====================
    
    def action_gift(self):
        """Give a gift to NPC to improve relationship."""
        if not self.currenttalk_npc:
            self.console.print_to_chat(
                "You need to talk to someone first to give a gift.",
                "SYSTEM"
            )
            return
        
        self.console.print_to_chat(
            f"\n=== Gift to {self.currenttalk_npc['name']} ===",
            "GIFT"
        )
        self.console.print_to_chat(
            f"They like: {self.currenttalk_npc['favor_tags']}",
            "GIFT"
        )
        self.console.print_to_chat(
            f"They hate: {self.currenttalk_npc['hate_tags']}",
            "GIFT"
        )
        self.console.print_to_chat(
            "Use the 'Give Gift' button to select an item, or check your Inventory.",
            "GIFT"
        )
        
        # Enable gift mode and set gift buttons
        self.gift_mode = True
        self._set_gift_mode_buttons()
    
    def process_gift(self, item_id: str):
        """
        Give a gift to current NPC.
        
        Args:
            item_id: ID of item to gift
        """
        self.console.print_to_chat("[Algorithm-Based Response]", "SYSTEM")
        if not self.currenttalk_npc:
            return
        
        item = self.trade.get_item_by_id(item_id)
        if not item:
            self.console.print_to_chat("Item not found.", "SYSTEM")
            return
        
        # Check favor/hate tags
        favor_tags = self.currenttalk_npc['favor_tags'].split(', ')
        hate_tags = self.currenttalk_npc['hate_tags'].split(', ')
        
        item_name_lower = item['item_name'].lower()
        
        # Calculate impression based on tags
        impression = 0
        
        # Check if item matches favor tags
        for tag in favor_tags:
            if tag.lower() in item_name_lower:
                impression += 3
                break
        
        # Check if item matches hate tags
        for tag in hate_tags:
            if tag.lower() in item_name_lower:
                impression -= 3
                break
        
        # Default small boost if neutral
        if impression == 0:
            impression = 1
        
        # Update relationship
        npc_id = self.currenttalk_npc['unique_id']
        result = self.relationships.modify_relation(
            npc_id=npc_id,
            change=impression,
            interaction_type="gift",
            location=self.state.current_location,
            notes=f"Gave {item['item_name']}"
        )
        
        # Generate response
        if impression > 0:
            self.console.print_to_chat(
                f"{self.currenttalk_npc['name']} is delighted by your gift!",
                "GIFT"
            )
        elif impression < 0:
            self.console.print_to_chat(
                f"{self.currenttalk_npc['name']} looks offended by your gift...",
                "GIFT"
            )
        else:
            self.console.print_to_chat(
                f"{self.currenttalk_npc['name']} accepts your gift politely.",
                "GIFT"
            )
        
        self.console.print_to_chat(result['message'], "SYSTEM")
        
        # Advance turn after successful gift
        self.advance_turn()
    
    # ==================== STATISTICS & VISUALIZATION ====================
    
    def show_statistics(self):
        """Show comprehensive statistics dashboard."""
        self.console.print_to_chat("Opening statistics dashboard...", "SYSTEM")
        
        # Create comprehensive dashboard
        self.visualizer.create_full_dashboard(
            trade_history_df=self.trade.trade_history_df,
            relationship_history_df=self.relationships.relationship_history_df,
            show=True
        )
        
        # Print summary to console
        trade_summary = self.trade.get_trade_summary()
        rel_summary = self.relationships.get_relationship_summary()
        
        self.console.print_to_chat("\n=== STATISTICS SUMMARY ===", "STATS")
        self.console.print_to_chat(
            f"Total Trades: {trade_summary['total_transactions']} "
            f"(Bought: {trade_summary['total_bought']}, Sold: {trade_summary['total_sold']})",
            "STATS"
        )
        self.console.print_to_chat(
            f"Gold Spent: {self.trade.format_currency(trade_summary['total_spent'])}",
            "STATS"
        )
        self.console.print_to_chat(
            f"Gold Earned: {self.trade.format_currency(trade_summary['total_earned'])}",
            "STATS"
        )
        self.console.print_to_chat(
            f"\nNPCs Met: {rel_summary['total_npcs_met']} "
            f"(Friends: {rel_summary['friends']}, Enemies: {rel_summary['enemies']})",
            "STATS"
        )
        
        if rel_summary['best_friend']['name']:
            self.console.print_to_chat(
                f"Best Friend: {rel_summary['best_friend']['name']} "
                f"(Relation: {rel_summary['best_friend']['relation']})",
                "STATS"
            )
        
        if rel_summary['worst_enemy']['name']:
            self.console.print_to_chat(
                f"Worst Enemy: {rel_summary['worst_enemy']['name']} "
                f"(Relation: {rel_summary['worst_enemy']['relation']})",
                "STATS"
            )
    
    def show_relationships(self):
        """Show detailed relationship information."""
        self.console.print_to_chat("\n=== RELATIONSHIPS ===", "RELATIONSHIP")
        
        # Get all relationships
        friends = self.relationships.get_npc_relationships(relation_threshold=3)
        enemies = self.relationships.get_npc_relationships(relation_threshold=-10)
        enemies = [e for e in enemies if e['relation'] < -2]
        
        if friends:
            self.console.print_to_chat("\nFriends:", "RELATIONSHIP")
            for friend in friends[:5]:
                self.console.print_to_chat(
                    f"  {friend['name']} - {friend['tier']} ({friend['relation']:+d}) - {friend['profession']}",
                    "RELATIONSHIP"
                )
        
        if enemies:
            self.console.print_to_chat("\nEnemies:", "RELATIONSHIP")
            for enemy in enemies[:5]:
                self.console.print_to_chat(
                    f"  {enemy['name']} - {enemy['tier']} ({enemy['relation']:+d}) - {enemy['profession']}",
                    "RELATIONSHIP"
                )
        
        # Show relationship distribution graph
        self.visualizer.plot_relationship_distribution(
            relationships_dict=self.relationships.relationships,
            characters_df=self.db.characters_df,
            show=True
        )
    def _update_displays(self):
        """Update all UI displays with current data."""
        # Cache relationship summary to avoid multiple calls
        rel_summary = self.relationships.get_relationship_summary()
        
        # Update info bulletin with current gold
        info = (
            f"Turn: {self.state.turn_count}\n"
            f"Location: {self.state.current_location or 'Unknown'}\n"
            f"Time: {self.state.time_of_day}\n"
            f"Weather: Foggy\n"
            f"\n"
            f"Gold: {self.trade.format_currency(self.player_gold_cp)}\n"
            f"Health: {self.state.player_health}/100\n"
            f"\n"
            f"Friends: {rel_summary['friends']}\n"
            f"Enemies: {rel_summary['enemies']}"
        )
        self.console.update_info_bulletin(info)
    
    def _show_merchant_stock(self):
        """Display full merchant inventory."""
        if not self.currenttalk_npc:
            return
        
        npc_id = self.currenttalk_npc['unique_id']
        merchant_stock = self.trade.get_merchant_inventory(npc_id)
        
        if not merchant_stock:
            self.console.print_to_chat(
                "This merchant has no items in stock.",
                "TRADE"
            )
            return
        
        self.console.print_to_chat(
            f"\n=== {self.currenttalk_npc['name']}'s Full Stock ===",
            "TRADE"
        )
        
        for item in merchant_stock:
            stock_info = "∞" if item['always_stock'] else str(item['quantity'])
            price_cp = self.trade.parse_currency(item['base_price'])
            modified_price = int(price_cp * item['price_modifier'])
            price_str = self.trade.format_currency(modified_price)
            
            self.console.print_to_chat(
                f"  {item['item_id']}: {item['item_name']} - {price_str} (Stock: {stock_info})",
                "TRADE"
            )
        
        self.console.print_to_chat(
            f"\nTotal items available: {len(merchant_stock)}",
            "TRADE"
        )
    
    def _exit_trade_mode(self):
        """Exit trade mode and restore default buttons."""
        self.trade_mode = False
        self._restore_default_buttons()
        self.console.print_to_chat("Exited trade menu.", "SYSTEM")
    
    def _exit_gift_mode(self):
        """Exit gift mode and restore default buttons."""
        self.gift_mode = False
        self._restore_default_buttons()
        self.console.print_to_chat("Exited gift menu.", "SYSTEM")
    
    def _prompt_buy(self):
        """Prompt user to enter buy command."""
        self.console.print_to_chat(
            "Enter: buy [item_id] [quantity]",
            "TRADE"
        )
        self.console.print_to_chat(
            "Example: buy WPN001 1",
            "TRADE"
        )
    
    def _prompt_sell(self):
        """Prompt user to enter sell command."""
        self.console.print_to_chat(
            "Enter: sell [item_id] [quantity]",
            "TRADE"
        )
        self.console.print_to_chat(
            "Example: sell WPN004 1",
            "TRADE"
        )
    
    def _prompt_gift(self):
        """Prompt user to enter gift command."""
        self.console.print_to_chat(
            "Enter: gift [item_id]",
            "GIFT"
        )
        self.console.print_to_chat(
            "Example: gift CMS004",
            "GIFT"
        )
        self.show_inventory()
    
    def _player_has_item(self, item_id: str, quantity: int) -> bool:
        """
        Check if player has enough of an item in inventory.
        
        Args:
            item_id: ID of item to check
            quantity: Required quantity
            
        Returns:
            True if player has enough of the item
        """
        if not self.phraser.current_character:
            return False
        
        # Get item info to determine type
        item = self.trade.get_item_by_id(item_id)
        if not item:
            return False
        
        item_type = item.get('item_type', '').lower()
        
        # Check inventory based on item type
        if 'weapon' in item_type:
            current = str(self.phraser.current_character.get('weapon_ids', '')).strip()
            if current and current != 'nan':
                items_list = [i.strip() for i in current.split(',') if i.strip()]
                return items_list.count(item_id) >= quantity
        elif 'armor' in item_type:
            current = str(self.phraser.current_character.get('armor_id', '')).strip()
            return current == item_id and quantity == 1
        elif 'ammunition' in item_type or 'ammo' in item_type:
            current = str(self.phraser.current_character.get('ammunition_ids', '')).strip()
            if current and current != 'nan':
                items_list = [i.strip() for i in current.split(',') if i.strip()]
                return items_list.count(item_id) >= quantity
        else:
            # Generic equipment
            current = str(self.phraser.current_character.get('equipment_ids', '')).strip()
            if current and current != 'nan':
                items_list = [i.strip() for i in current.split(',') if i.strip()]
                return items_list.count(item_id) >= quantity
        
        return False
    
    def _add_item_to_inventory(self, item_id: str, quantity: int):
        """
        Add items to player inventory.
        
        Args:
            item_id: ID of item to add
            quantity: Quantity to add
        """
        if not self.phraser.current_character:
            return
        
        # Get item info to determine type
        item = self.trade.get_item_by_id(item_id)
        if not item:
            return
        
        item_type = item.get('item_type', '').lower()
        
        # Update inventory based on item type
        if 'weapon' in item_type:
            current = str(self.phraser.current_character.get('weapon_ids', '')).strip()
            if current and current != 'nan':
                for _ in range(quantity):
                    if item_id not in current:
                        current = f"{current}, {item_id}"
            else:
                current = item_id
            self.phraser.current_character['weapon_ids'] = current
        elif 'armor' in item_type:
            self.phraser.current_character['armor_id'] = item_id
        elif 'ammunition' in item_type or 'ammo' in item_type:
            current = str(self.phraser.current_character.get('ammunition_ids', '')).strip()
            if current and current != 'nan':
                current = f"{current}, {item_id}"
            else:
                current = item_id
            self.phraser.current_character['ammunition_ids'] = current
        else:
            # Generic equipment
            current = str(self.phraser.current_character.get('equipment_ids', '')).strip()
            if current and current != 'nan':
                for _ in range(quantity):
                    if item_id not in current:
                        current = f"{current}, {item_id}"
            else:
                current = item_id
            self.phraser.current_character['equipment_ids'] = current
        
        # Log to console
        item_name = item.get('item_name', item_id)
        self.console.print_to_chat(f"Added {quantity}x {item_name} to inventory.", "SYSTEM")
    
    def _remove_item_from_inventory(self, item_id: str, quantity: int):
        """
        Remove items from player inventory.
        
        Args:
            item_id: ID of item to remove
            quantity: Quantity to remove
        """
        if not self.phraser.current_character:
            return
        
        # Get item info to determine type
        item = self.trade.get_item_by_id(item_id)
        if not item:
            return
        
        item_type = item.get('item_type', '').lower()
        
        # Update inventory based on item type
        if 'weapon' in item_type:
            current = str(self.phraser.current_character.get('weapon_ids', '')).strip()
            items_list = [i.strip() for i in current.split(',') if i.strip()]
            for _ in range(quantity):
                if item_id in items_list:
                    items_list.remove(item_id)
            self.phraser.current_character['weapon_ids'] = ', '.join(items_list) if items_list else ''
        elif 'armor' in item_type:
            self.phraser.current_character['armor_id'] = ''
        elif 'ammunition' in item_type or 'ammo' in item_type:
            current = str(self.phraser.current_character.get('ammunition_ids', '')).strip()
            items_list = [i.strip() for i in current.split(',') if i.strip()]
            for _ in range(quantity):
                if item_id in items_list:
                    items_list.remove(item_id)
            self.phraser.current_character['ammunition_ids'] = ', '.join(items_list) if items_list else ''
        else:
            # Generic equipment
            current = str(self.phraser.current_character.get('equipment_ids', '')).strip()
            items_list = [i.strip() for i in current.split(',') if i.strip()]
            for _ in range(quantity):
                if item_id in items_list:
                    items_list.remove(item_id)
            self.phraser.current_character['equipment_ids'] = ', '.join(items_list) if items_list else ''
        
        # Log to console
        item_name = item.get('item_name', item_id)
        self.console.print_to_chat(f"Removed {quantity}x {item_name} from inventory.", "SYSTEM")
    
    def is_tradeable_npc(self, npc):
        """
        Determine if an NPC can trade.

        Args:
            npc: Character dictionary

        Returns:
            bool: True if they can trade
        """
        profession = npc.get('profession', '').lower()
        
        # Explicit merchant types
        tradeable_keywords = [
            'merchant', 'vendor', 'smith', 'innkeeper', 'apothecary',
            'fishmonger', 'guild_master', 'armorer', 'weaponsmith',
            'blacksmith', 'trader', 'shopkeeper', 'seller', 'barmaid'
        ]
    
        # Check keywords
        if any(keyword in profession for keyword in tradeable_keywords):
            return True
    
        # Specific professions that can trade even without keywords
        full_profession = npc.get('profession', '')
        if full_profession in ['Innkeeper', 'Barmaid', 'Guild_Master', 
                               'Traveling_Merchant', 'Senior_Merchant']:
            return True

        return False