import tkinter as tk
import random
import time

class DiceUI:
    def __init__(self, dice: str ="1d6", die_size=200):
        self.count, self.faces = self.parse_dice(dice=dice)
        if self.count < 1 or self.faces < 2:
            raise ValueError("Invalid dice notation")

        self.dice = dice
        self.die_size = die_size
        self.dot_radius = 10

        self.root = tk.Toplevel()
        self.root.title(f"Dice Roller ({dice})")

        self.canvas = tk.Canvas(
            self.root,
            width=die_size,
            height=die_size,
            bg="white"
        )
        self.canvas.pack(pady=10)

        self.result_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.result_label.pack()

        self.roll_button = tk.Button(
            self.root,
            text="Roll",
            font=("Arial", 14),
            command=self.roll_die
        )
        self.roll_button.pack(pady=10)

        self.draw_die_outline()

    # --------------------
    # Utilities
    # --------------------
    def parse_dice(self, dice: str):
        count, faces = dice.lower().split("d")
        count = int(count)
        faces = int(faces)

        if count < 1 or faces < 2:
            raise ValueError("Invalid dice notation")

        return count, faces

    # --------------------
    # Drawing
    # --------------------
    def draw_die_outline(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(
            10, 10,
            self.die_size - 10,
            self.die_size - 10,
            width=3
        )

    def draw_dot(self, x, y):
        r = self.dot_radius
        self.canvas.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill="black"
        )

    def draw_classic_face(self, value):
        positions = {
            1: [(100, 100)],
            2: [(60, 60), (140, 140)],
            3: [(60, 60), (100, 100), (140, 140)],
            4: [(60, 60), (140, 60), (60, 140), (140, 140)],
            5: [(60, 60), (140, 60), (100, 100), (60, 140), (140, 140)],
            6: [(60, 60), (140, 60), (60, 100), (140, 100), (60, 140), (140, 140)],
        }
        for x, y in positions[value]:
            self.draw_dot(x, y)

    def draw_number_face(self, value):
        self.canvas.create_text(
            self.die_size // 2,
            self.die_size // 2,
            text=str(value),
            font=("Arial", 48, "bold")
        )

    # --------------------
    # Logic
    # --------------------
    def roll_die(self, dice: str = None):
        if dice is None:
            dice = self.dice
        else:
            self.dice = dice

        count, faces = self.parse_dice(dice)
        self.draw_die_outline()

        # animation (single representative face)
        for _ in range(10):
            temp = random.randint(1, faces)
            self.canvas.delete("temp")
            self.canvas.create_text(
                self.die_size // 2,
                self.die_size // 2,
                text=str(temp),
                font=("Arial", 32),
                tags="temp"
            )
            self.root.update()
            time.sleep(0.05)

        # actual roll
        rolls = [random.randint(1, faces) for _ in range(count)]
        total = sum(rolls)

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

