"""
Themed Dice Roller - Matches the Fog-Shrouded Chronicles aesthetic
"""
import tkinter as tk
import random
import time


class DiceUI:
    # Theme colors matching your console
    THEME = {
        'bg_dark': '#2b2b2b',
        'bg_medium': '#3d3d3d',
        'bg_light': '#1e1e1e',
        'border': '#8b7355',
        'text': '#e8e0d5',
        'accent': '#731010',
        'accent_hover': '#8b1a1a',
        'dot_color': '#e8e0d5'
    }
    
    def __init__(self, dice: str = "1d6", die_size=250, parent=None):
        self.count, self.faces = self.parse_dice(dice=dice)
        if self.count < 1 or self.faces < 2:
            raise ValueError("Invalid dice notation")

        self.dice = dice
        self.die_size = die_size
        self.dot_radius = 12
        
        # Create toplevel window or use parent
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Toplevel()
            
        self.root.title(f"Dice Roller - {dice}")
        self.root.configure(bg=self.THEME['bg_dark'])
        self.root.resizable(False, False)
        
        # Center the window
        self._center_window()
        
        # Create main frame with border
        self.main_frame = tk.Frame(
            self.root,
            bg=self.THEME['border'],
            padx=3,
            pady=3
        )
        self.main_frame.pack(padx=10, pady=10)
        
        # Inner frame
        inner_frame = tk.Frame(
            self.main_frame,
            bg=self.THEME['bg_medium']
        )
        inner_frame.pack()
        
        # Title label
        title_label = tk.Label(
            inner_frame,
            text=f"Rolling {dice}",
            bg=self.THEME['bg_medium'],
            fg=self.THEME['border'],
            font=('Georgia', 14, 'bold')
        )
        title_label.pack(pady=(10, 5))
        
        # Canvas for die
        self.canvas = tk.Canvas(
            inner_frame,
            width=die_size,
            height=die_size,
            bg=self.THEME['bg_light'],
            highlightthickness=2,
            highlightbackground=self.THEME['border']
        )
        self.canvas.pack(padx=15, pady=10)
        
        # Result label
        self.result_label = tk.Label(
            inner_frame,
            text="Click 'Roll' to begin",
            bg=self.THEME['bg_medium'],
            fg=self.THEME['text'],
            font=('Georgia', 12),
            wraplength=die_size - 20
        )
        self.result_label.pack(pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(inner_frame, bg=self.THEME['bg_medium'])
        btn_frame.pack(pady=10)
        
        # Roll button
        self.roll_button = tk.Button(
            btn_frame,
            text="Roll Dice",
            font=('Georgia', 11, 'bold'),
            command=self.roll_die,
            bg=self.THEME['accent'],
            fg=self.THEME['text'],
            activebackground=self.THEME['accent_hover'],
            activeforeground=self.THEME['text'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=5
        )
        self.roll_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = tk.Button(
            btn_frame,
            text="Close",
            font=('Georgia', 11, 'bold'),
            command=self.root.destroy,
            bg=self.THEME['bg_dark'],
            fg=self.THEME['text'],
            activebackground='#3d3d3d',
            activeforeground=self.THEME['text'],
            cursor='hand2',
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=5
        )
        close_button.pack(side=tk.LEFT, padx=5)
        
        # Draw initial die outline
        self.draw_die_outline()
        
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.die_size + 80
        height = self.die_size + 150
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # --------------------
    # Utilities
    # --------------------
    def parse_dice(self, dice: str):
        """Parse dice notation like '2d6' into count and faces"""
        dice = dice.lower().strip()
        if 'd' not in dice:
            raise ValueError("Invalid dice notation - must contain 'd'")
            
        count, faces = dice.split("d")
        count = int(count)
        faces = int(faces)

        if count < 1 or faces < 2:
            raise ValueError("Invalid dice notation")

        return count, faces

    # --------------------
    # Drawing
    # --------------------
    def draw_die_outline(self):
        """Draw the die border"""
        self.canvas.delete("all")
        
        # Ornate border
        margin = 20
        self.canvas.create_rectangle(
            margin, margin,
            self.die_size - margin,
            self.die_size - margin,
            width=3,
            outline=self.THEME['border']
        )
        
        # Inner border
        inner_margin = margin + 10
        self.canvas.create_rectangle(
            inner_margin, inner_margin,
            self.die_size - inner_margin,
            self.die_size - inner_margin,
            width=1,
            outline=self.THEME['border'],
            dash=(3, 3)
        )

    def draw_dot(self, x, y):
        """Draw a single die dot"""
        r = self.dot_radius
        self.canvas.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=self.THEME['dot_color'],
            outline=self.THEME['border'],
            width=2
        )

    def draw_classic_face(self, value):
        """Draw classic die faces (1-6) with dots"""
        center = self.die_size // 2
        offset = 40
        
        positions = {
            1: [(center, center)],
            2: [(center - offset, center - offset), 
                (center + offset, center + offset)],
            3: [(center - offset, center - offset), 
                (center, center), 
                (center + offset, center + offset)],
            4: [(center - offset, center - offset), 
                (center + offset, center - offset),
                (center - offset, center + offset), 
                (center + offset, center + offset)],
            5: [(center - offset, center - offset), 
                (center + offset, center - offset),
                (center, center),
                (center - offset, center + offset), 
                (center + offset, center + offset)],
            6: [(center - offset, center - offset), 
                (center + offset, center - offset),
                (center - offset, center), 
                (center + offset, center),
                (center - offset, center + offset), 
                (center + offset, center + offset)],
        }
        
        for x, y in positions.get(value, []):
            self.draw_dot(x, y)

    def draw_number_face(self, value):
        """Draw numeric face for dice with more than 6 faces"""
        self.canvas.create_text(
            self.die_size // 2,
            self.die_size // 2,
            text=str(value),
            font=('Georgia', 56, 'bold'),
            fill=self.THEME['text']
        )

    # --------------------
    # Animation & Logic
    # --------------------
    def animate_roll(self, faces):
        """Animate the rolling effect"""
        self.roll_button.config(state=tk.DISABLED)
        
        for i in range(15):
            temp = random.randint(1, faces)
            self.draw_die_outline()
            
            # Draw temporary face
            if temp <= 6:
                self.draw_classic_face(temp)
            else:
                self.draw_number_face(temp)
            
            self.root.update()
            # Slow down animation as it progresses
            time.sleep(0.05 + (i * 0.01))
        
        self.roll_button.config(state=tk.NORMAL)

    def roll_die(self, dice: str = None):
        """Roll the dice and display results"""
        if dice is None:
            dice = self.dice

        count, faces = self.parse_dice(dice)
        
        # Perform animation
        self.animate_roll(faces)
        
        # Actual roll
        rolls = [random.randint(1, faces) for _ in range(count)]
        total = sum(rolls)
        
        # Draw final result (first die)
        self.draw_die_outline()
        face_value = rolls[0]
        
        if face_value <= 6:
            self.draw_classic_face(face_value)
        else:
            self.draw_number_face(face_value)
        
        self.result_label.config(
            text=f"{dice} → rolls: {rolls} | total: {total}"
        )
        
        return {
            "dice": dice,
            "rolls": rolls,
            "total": total
        }


# --------------------
# Integration Helper
# --------------------
def roll_dice_themed(dice="1d6", parent=None):
    """
    Convenience function to create and show a themed dice roller
    
    Usage in your game:
        from dice_roller import roll_dice_themed
        roll_dice_themed("2d6", parent=self.root)
    """
    roller = DiceUI(dice=dice, parent=parent)
    roller.root.grab_set()  # Make modal
    return roller


# --------------------
# Example/Testing
# --------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Test different dice types
    roller = DiceUI("2d6")
    
    root.mainloop()