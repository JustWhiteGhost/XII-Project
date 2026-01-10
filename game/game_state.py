"""
Game State - Manages current game state and progression
"""


class GameState:
    def __init__(self):
        self.turn_count = 1
        self.current_location = "The Foggy Inn"
        self.current_character = None
        self.time_of_day = "Morning"
        
        # Player stats
        self.player_health = 100
        self.player_gold = 500
        self.player_inventory = []
        
        # Game flags
        self.flags = {}
    
    def advance_turn(self):
        """Progress to next turn"""
        self.turn_count += 1
        self._update_time()
    
    def _update_time(self):
        """Update time of day based on turns"""
        times = ["Morning", "Afternoon", "Evening", "Night"]
        time_index = (self.turn_count // 3) % len(times)
        self.time_of_day = times[time_index]
    
    def set_flag(self, flag_name, value=True):
        """Set a game flag"""
        self.flags[flag_name] = value
    
    def get_flag(self, flag_name, default=False):
        """Get a game flag value"""
        return self.flags.get(flag_name, default)
    
    def add_gold(self, amount):
        """Add gold to player"""
        self.player_gold += amount
    
    def remove_gold(self, amount):
        """Remove gold from player"""
        self.player_gold = max(0, self.player_gold - amount)
    
    def add_item(self, item):
        """Add item to inventory"""
        self.player_inventory.append(item)
    
    def remove_item(self, item):
        """Remove item from inventory"""
        if item in self.player_inventory:
            self.player_inventory.remove(item)