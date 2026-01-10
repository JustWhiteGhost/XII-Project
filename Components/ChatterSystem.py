class ChatterSystem:
    def __init__(self, output_callback):
        """
        Initialize the system ONCE.
        We only pass the things that stay permanent (like the GUI connection).
        """
        self.push_text = output_callback
        self.current_location = None
        self.current_npcs = []

    def load_scene(self, location_data, npc_list):
        """
        Call this function every time the player enters a new room.
        It updates the internal state without needing a new object.
        """
        self.current_location = location_data
        self.current_npcs = npc_list

        print(f"Loaded scene: {location_data.get('location_name', 'Unknown')} with {len(npc_list)} NPCs.")

    def show_menu(self):
        """Formats and pushes text to Tkinter."""
        if not self.current_location:
            self.push_text("System: No location loaded.")
            return

        # 1. Location Header
        loc_name = self.current_location.get('name', 'Unknown')
        desc = self.current_location.get('description', '...')
        
        text_block = [
            f"\n=== {loc_name} ===",
            f"{desc}",
            "-" * 20
        ]

        # 2. NPC List
        if not self.current_npcs:
            text_block.append("(It is quiet here. No one to talk to.)")
        else:
            text_block.append("[PEOPLE NEARBY]")
            for i, char in enumerate(self.current_npcs, 1):
                print(char)
                role = char.get('role', 'NPC')
                name = char.get('name', 'Unknown')
                text_block.append(f" {i}. {name} [{role}]")
            
            text_block.append("\n(Enter the number to interact)")

        # 3. Push to GUI
        self.push_text("\n".join(text_block))

    def handle_input(self, user_input):
        """
        Checks input against the CURRENTLY loaded NPCs.
        """
        if not self.current_npcs:
            return None

        try:
            selection = int(user_input) - 1
            if 0 <= selection < len(self.current_npcs):
                self.push_text(f"You approach {self.current_npcs[selection]['name']}.")
                return self.current_npcs[selection]
            else:
                self.push_text("System: Invalid number.")
        except ValueError:
            self.push_text("System: Please enter a number.")
        
        return None