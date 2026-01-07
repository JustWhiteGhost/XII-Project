import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk


class RetroRPGConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Fog-Shrouded Chronicles")
        self.root.configure(bg='#2b2b2b')

        self.root.geometry("1310x930")
        self.root.resizable(False, False)

        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 1310) // 2
        y = (screen_height - 930) // 2
        self.root.geometry(f"1310x930+{x}+{y}")

        self.current_character = None
        self.chat_history = []
        self.navigation_buttons = []
        self.action_buttons = []
        self.border_image = None

        self.setup_ui()

    def set_border_image(self, image_path):
        """
        Set a border image around the entire window.

        Parameters:
            image_path (str): Path to the border image file
        """
        try:
            img = Image.open(image_path)
            img = img.resize((1310, 930), Image.Resampling.LANCZOS)
            self.border_image = ImageTk.PhotoImage(img)
            self.border_canvas.create_image(0, 0, anchor=tk.NW, image=self.border_image)
            self.border_canvas.lower('all')
        except Exception as e:
            print(f"Error loading border image: {e}")

    def set_border_color(self, color):
        """
        Set a solid color border around the window.

        Parameters:
            color (str): Hex color code (e.g., '#8b7355')
        """
        self.border_canvas.configure(bg=color)

    def setup_ui(self):
        # Border canvas layer (behind everything)
        self.border_canvas = tk.Canvas(self.root, width=1310, height=950,
                                       bg='#8b7355', highlightthickness=0)
        self.border_canvas.place(x=0, y=0)

        # Main container frame with border inset
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.place(x=15, y=15, width=1280, height=900)

        # Profile Picture - 300x300
        self.profile_frame = tk.Frame(main_frame, bg='#3d3d3d',
                                      width=300, height=300,
                                      relief=tk.RIDGE, bd=3,
                                      highlightbackground='#8b7355',
                                      highlightthickness=2)
        self.profile_frame.place(x=8, y=8)
        self.profile_frame.pack_propagate(False)

        tk.Label(self.profile_frame, text="Profile Picture",
                 bg='#3d3d3d', fg='#e8e0d5',
                 font=('Georgia', 11, 'bold')).pack(pady=3)

        self.profile_text = tk.Text(
            self.profile_frame,
            bg='#3d3d3d',
            fg='#e8e0d5',
            font=('Courier', 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            cursor='arrow',
            insertbackground='#e8e0d5'
        )
        self.profile_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        # Buttons - 300x145
        btn_frame = tk.Frame(main_frame, bg='#3d3d3d',
                             width=300, height=150,
                             relief=tk.RIDGE, bd=3,
                             highlightbackground='#8b7355',
                             highlightthickness=2)
        btn_frame.place(x=8, y=316)
        btn_frame.pack_propagate(False)

        tk.Label(btn_frame, text="Buttons", bg='#3d3d3d', fg='#e8e0d5',
                 font=('Georgia', 10, 'bold')).pack(pady=2)

        self.nav_btn_container = tk.Frame(btn_frame, bg='#3d3d3d')
        self.nav_btn_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # Info Bulletin - 300x376
        info_frame = tk.Frame(main_frame, bg='#3d3d3d',
                              width=300, height=422,
                              relief=tk.RIDGE, bd=3,
                              highlightbackground='#8b7355',
                              highlightthickness=2)
        info_frame.place(x=8, y=469)
        info_frame.pack_propagate(False)

        tk.Label(info_frame, text="Info Bulletin", bg='#3d3d3d', fg='#8b7355',
                 font=('Georgia', 11, 'bold')).pack(pady=3)

        info_scroll_frame = tk.Frame(info_frame, bg='#3d3d3d')
        info_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)

        info_scrollbar = tk.Scrollbar(info_scroll_frame, bg='#3d3d3d',
                                      troughcolor='#2b2b2b',
                                      activebackground='#8b7355')
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.info_text = tk.Text(
            info_scroll_frame,
            bg='#3d3d3d',
            fg='#8b7355',
            font=('Georgia', 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            yscrollcommand=info_scrollbar.set,
            cursor='arrow',
            insertbackground='#8b7355'
        )
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.config(command=self.info_text.yview)

        # Chat Log - 964x692
        chat_frame = tk.Frame(main_frame, bg='#3d3d3d',
                              width=956, height=692,
                              relief=tk.RIDGE, bd=3,
                              highlightbackground='#8b7355',
                              highlightthickness=2)
        chat_frame.place(x=316, y=8)
        chat_frame.pack_propagate(False)

        tk.Label(chat_frame, text="Chat Log", bg='#3d3d3d', fg='#e8e0d5',
                 font=('Georgia', 12, 'bold')).pack(pady=3)

        chat_scroll_frame = tk.Frame(chat_frame, bg='#3d3d3d')
        chat_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        chat_scrollbar = tk.Scrollbar(chat_scroll_frame, bg='#3d3d3d',
                                      troughcolor='#2b2b2b',
                                      activebackground='#8b7355')
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_log = tk.Text(
            chat_scroll_frame,
            bg='#1e1e1e',
            fg='#e8e0d5',
            font=('Georgia', 11),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            yscrollcommand=chat_scrollbar.set,
            cursor='arrow',
            insertbackground='#e8e0d5'
        )
        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.config(command=self.chat_log.yview)

        # Typing Bar - 964x68
        typing_frame = tk.Frame(main_frame, bg='#3d3d3d',
                                width=956, height=68,
                                relief=tk.RIDGE, bd=3,
                                highlightbackground='#8b7355',
                                highlightthickness=2)
        typing_frame.place(x=316, y=708)
        typing_frame.pack_propagate(False)

        tk.Label(typing_frame, text="Typing Bar", bg='#3d3d3d', fg='#e8e0d5',
                 font=('Georgia', 10, 'bold')).pack(pady=2)

        input_container = tk.Frame(typing_frame, bg='#3d3d3d')
        input_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

        self.input_entry = tk.Entry(
            input_container,
            bg='#1e1e1e',
            fg='#e8e0d5',
            font=('Georgia', 11),
            relief=tk.SUNKEN,
            bd=2,
            insertbackground='#e8e0d5'
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        self.input_entry.bind('<Return>', lambda e: self.on_input_submit())

        send_btn = tk.Button(
            input_container,
            text="Send",
            command=self.on_input_submit,
            bg='#731010',
            fg='#e8e0d5',
            font=('Georgia', 10, 'bold'),
            cursor='hand2',
            width=8,
            relief=tk.RAISED,
            bd=2,
            activebackground='#8b1a1a'
        )
        send_btn.pack(side=tk.RIGHT)

        # Action HUD - 964x140
        action_frame = tk.Frame(main_frame, bg='#3d3d3d',
                                width=956, height=108,
                                relief=tk.RIDGE, bd=3,
                                highlightbackground='#8b7355',
                                highlightthickness=2)
        action_frame.place(x=316, y=784)
        action_frame.pack_propagate(False)

        tk.Label(action_frame, text="Action HUD", bg='#3d3d3d', fg='#8b7355',
                 font=('Georgia', 10, 'bold')).pack(pady=2)

        self.action_btn_container = tk.Frame(action_frame, bg='#3d3d3d')
        self.action_btn_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

    def print_to_chat(self, message, sender="SYSTEM"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {sender}: {message}\n"

        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, formatted_msg)
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

        self.chat_history.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message
        })

    def get_input_text(self):
        return self.input_entry.get().strip()

    def clear_input(self):
        self.input_entry.delete(0, tk.END)

    def set_input_callback(self, callback):
        self.input_callback = callback

    def on_input_submit(self):
        text = self.get_input_text()
        if text:
            if hasattr(self, 'input_callback'):
                self.input_callback(text)
            self.clear_input()

    def update_profile(self, text):
        self.profile_text.config(state=tk.NORMAL)
        self.profile_text.delete(1.0, tk.END)
        self.profile_text.insert(1.0, text)
        self.profile_text.config(state=tk.DISABLED)

    def update_info_bulletin(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state=tk.DISABLED)

    def set_navigation_buttons(self, buttons_config):
        for widget in self.nav_btn_container.winfo_children():
            widget.destroy()
        self.navigation_buttons.clear()

        buttons_config_safe = buttons_config[:4] if buttons_config else []

        for text, callback in buttons_config_safe:
            btn = tk.Button(
                self.nav_btn_container,
                text=text,
                command=callback,
                bg='#731010',
                fg='#e8e0d5',
                font=('Georgia', 9),
                relief=tk.RAISED,
                bd=2,
                cursor='hand2',
                activebackground='#8b1a1a'
            )
            btn.pack(fill=tk.X, pady=1)
            self.navigation_buttons.append(btn)

    def set_action_buttons(self, buttons_config):
        for widget in self.action_btn_container.winfo_children():
            widget.destroy()
        self.action_buttons.clear()

        buttons_config_safe = buttons_config if buttons_config else []

        num_buttons = len(buttons_config_safe)
        cols = 4
        rows = (num_buttons + cols - 1) // cols

        for i, (text, callback) in enumerate(buttons_config_safe):
            row = i // cols
            col = i % cols

            btn = tk.Button(
                self.action_btn_container,
                text=text,
                command=callback,
                bg='#731010',
                fg='#e8e0d5',
                font=('Georgia', 10),
                relief=tk.RAISED,
                bd=2,
                cursor='hand2',
                width=10,
                height=1,
                activebackground='#8b1a1a'
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
            self.action_buttons.append(btn)

        for i in range(cols):
            self.action_btn_container.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.action_btn_container.grid_rowconfigure(i, weight=1)

    def get_chat_history(self):
        return self.chat_history.copy()


# ===== SAMPLE USAGE - REPLACE WITH BACKEND =====
def main():
    root = tk.Tk()
    app = RetroRPGConsole(root)

    # SAMPLE: Set up navigation buttons
    app.set_navigation_buttons([
        ("Character", lambda: app.print_to_chat("Character info")),
        ("Location", lambda: app.print_to_chat("Location info")),
        ("Inventory", lambda: app.print_to_chat("Inventory opened")),
        ("Inventory", lambda: app.print_to_chat("Inventory opened"))
    ])

    # SAMPLE: Set up action buttons
    app.set_action_buttons([
        ("Talk", lambda: app.print_to_chat("You talk...")),
        ("Trade", lambda: app.print_to_chat("Opening trade...")),
        ("Gift", lambda: app.print_to_chat("Select gift...")),
        ("Leave", lambda: app.print_to_chat("You leave")),
        ("Talk", lambda: app.print_to_chat("You talk...")),
        ("Trade", lambda: app.print_to_chat("Opening trade...")),
        ("Gift", lambda: app.print_to_chat("Select gift...")),
        ("Leave", lambda: app.print_to_chat("You leave"))
    ])

    # SAMPLE: Set up profile
    app.update_profile("Character Name\nAge: 34\nMood: Happy")

    # SAMPLE: Set up info bulletin
    app.update_info_bulletin("Welcome!\n\nTurn: 1\nLocation: Inn")

    # SAMPLE: Set up input callback
    def on_player_input(text):
        app.print_to_chat(text, "Player")

    app.set_input_callback(on_player_input)

    app.print_to_chat("Welcome to Fog-Shrouded Chronicles!")

    root.mainloop()


if __name__ == "__main__":
    main()