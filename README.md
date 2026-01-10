# 🌫️ Fog-Shrouded Chronicles

**AI-Powered Virtual D&D Experience**

An immersive text-based RPG where an AI Dungeon Master guides you through a fog-shrouded medieval fantasy world. Features 80+ unique NPCs, dynamic storytelling, turn-based combat, and persistent memory that remembers your choices.

---

## ⚡ Quick Start

### 1️⃣ Install Dependencies

Open Command Prompt/Terminal in this folder and run:

```bash
python setup.py
```

The setup script will automatically check and install everything you need.

### 2️⃣ Get Groq API Key (FREE)

1. Visit: [https://console.groq.com/](https://console.groq.com/)
2. Sign up (completely free)
3. Create an API key
4. Copy the key

### 3️⃣ Configure the Game

- Open `config.json` in a text editor
- Replace `YOUR_API_KEY_HERE` with your actual Groq API key
- Save the file

### 4️⃣ Run the Game

**Windows:**
```bash
LAUNCH.bat
```

**Mac/Linux:**
```bash
./launch.sh
```

Or run directly:
```bash
python Main.py
```

---

## 📦 Manual Installation

If automatic setup fails, install manually:

### Install Python
Download Python 3.8 or higher from: [https://www.python.org/](https://www.python.org/)

### Install Requirements

**Option 1:** Use requirements file
```bash
pip install -r requirements.txt
```

**Option 2:** Install individually
```bash
pip install pandas groq sentence-transformers networkx numpy Pillow
```

---

## 💻 System Requirements

### Minimum
- **Python:** 3.8 or higher
- **RAM:** 4 GB
- **Internet:** Required (for AI)
- **Storage:** 500 MB free space on pendrive

### Recommended
- **Python:** 3.10+
- **RAM:** 8 GB
- **Internet:** Stable connection
- **Storage:** 1 GB free space

---

## 📁 Pendrive Structure

```
FogShroudedChronicles/
├── Main.py                      # Game launcher
├── setup.py                     # Setup script
├── requirements.txt             # Python packages
├── config.json                  # Configuration (add API key here!)
├── README.md                    # This file
│
├── game/                        # Game logic
│   ├── game_manager.py
│   ├── game_state.py
│   └── combat_system.py
│
├── ui/                          # User interface
│   └── console.py
│
├── data/                        # Data handlers
│   └── character_data.py
│
├── Data CSVs/                   # Game databases
│   ├── Character_Info.csv
│   └── Location_Info.csv
│
├── saves/                       # Player save files
│   └── (created automatically)
│
└── memory/                      # AI memory storage
    └── (created automatically)
```

---

## 🎮 Features

- ✅ **AI-Powered Dungeon Master** - Uses Groq's Llama 3.1 70B model
- ✅ **80+ Unique Characters** - Each with distinct personalities, moods, and motivations
- ✅ **Knowledge Graph** - Tracks relationships and world state
- ✅ **Semantic Memory** - AI remembers past events and references them
- ✅ **Turn-Based Combat** - Strategic combat with dice rolls and abilities
- ✅ **Natural Language Input** - Type what you want to do, AI understands
- ✅ **Persistent Saves** - All progress saved to pendrive
- ✅ **Fully Portable** - Works on any PC with Python

---

## 🛠️ Troubleshooting

### `ModuleNotFoundError: No module named 'pandas'`
**Solution:** Run `setup.py` or install manually:
```bash
pip install pandas
```

### `No module named 'tkinter'`
**Solution:** Reinstall Python with tkinter support enabled
- Windows: Use official Python installer (tkinter included by default)
- Linux: `sudo apt install python3-tk`
- Mac: Reinstall Python via Homebrew

### `API key not configured`
**Solution:** Edit `config.json` and add your Groq API key

### `No internet connection`
**Solution:** Connect to internet - the AI requires it to function

### `Character_Info.csv not found`
**Solution:** Make sure `Data CSVs` folder is on the pendrive

### Game runs slow
**Solution:** 
- Check internet connection speed
- Close other programs
- Try a different AI model in config.json (e.g., `llama-3.1-8b-instant` is faster but less creative)

---

## 💰 Cost

The game uses Groq's API which offers:

| Tier | Cost | Details |
|------|------|---------|
| **Free** | $0 | Generous limits for testing and casual play |
| **Pay-as-you-go** | ~$3/month | For daily play (100+ turns/day) |

**No hidden costs. No subscriptions required.**

---

## 🎯 How to Play

### Combat Example
```
You: I attack the goblin with my sword
DM: You swing your blade in a wide arc! Roll: 16
    The goblin tries to dodge but your steel finds its mark.
    The creature staggers back, blood seeping from the wound. [8 damage]
    The goblin snarls, "You'll regret that, human!"
```

### Dialogue Example
```
You: I ask Emma about the mysterious fog
DM: Emma's expression darkens as she leans closer, voice dropping to a whisper.
    "The fog... it's been here for months now. Started after the old temple 
    burned down. Some say it's cursed, others claim it's hiding something.
    My father won't talk about it, but I've seen strange shadows moving in 
    the mist at night." She glances nervously at the window.
```

### Exploration Example
```
You: I search the abandoned house for clues
DM: You carefully push open the creaking door. Inside, dust motes dance in 
    the dim light filtering through broken shutters. The place has been 
    ransacked - furniture overturned, drawers pulled open. But something 
    catches your eye: fresh footprints in the dust, leading to the cellar door.
```

---

## 🔧 Configuration Options

Edit `config.json` to customize your experience:

```json
{
  "groq_api_key": "your_api_key_here",
  
  "model": "llama-3.1-70b-versatile",
  // Options: 
  //   "llama-3.1-70b-versatile" - Best quality, slower
  //   "llama-3.1-8b-instant" - Faster, less creative
  
  "max_tokens": 800,
  // Higher = longer DM responses (200-1000)
  
  "temperature": 0.85,
  // Higher = more creative/random (0.0-1.0)
  
  "game_settings": {
    "auto_save": true,
    "save_interval": 10,        // Save every N turns
    "max_history": 100          // Keep last N turns in memory
  }
}
```

---

## 🚀 Advanced Usage

### Running Without Launcher

```bash
# Windows
python Main.py

# Mac/Linux  
python3 Main.py
```

### Custom Save Location

Edit in `Main.py`:
```python
paths = PortablePathManager()
paths.saves_dir = Path("D:/MyCustomSaves")  # Custom location
```

### Debug Mode

Add to `config.json`:
```json
{
  "debug": true,
  "verbose_logging": true
}
```

---

## 📚 For Developers

### Project Structure

```python
# Entry point
Main.py                 # Initializes game, handles main loop

# Core systems
game/
  ├── game_manager.py   # Orchestrates all game systems
  ├── game_state.py     # Tracks player state, inventory, flags
  └── combat_system.py  # Combat mechanics and resolution

# UI
ui/
  └── console.py        # Tkinter-based retro RPG interface

# Data
data/
  └── character_data.py # CSV loading and character queries

# AI Integration  
Components/
  └── AIConnection.py   # Groq API wrapper
```

### Adding New Characters

Edit `Data CSVs/Character_Info.csv`:
```csv
unique_id|name|age|relation|money|mood|nature|profession|location|favor_tags|hate_tags|description
X1Y2Z5|Your Character|30|7|5000|Happy|Brave|Warrior|10101|combat,honor,ale|cowardice,theft,lies|A fierce warrior...
```

### Adding New Locations

Create `Data CSVs/Location_Info.csv`:
```csv
location_id|name|description|type|danger_level
10101|The Foggy Inn|A weathered tavern...|Safe|1
40103|The Dark Harbor|Rotting docks...|Dangerous|5
```

---

## 🤝 Contributing

This is an educational project. Feel free to:
- Fork and modify for your own campaigns
- Add new characters and locations
- Improve the AI prompts
- Create new game mechanics

---

## 📄 License

This game is for **educational and portfolio purposes**.

- Game code: Original work
- Character data: Original content
- AI Models: Provided by Groq (Llama 3.1 by Meta)

---

## 🆘 Support

### Common Issues

**Q: Can I play offline?**  
A: No, the AI Dungeon Master requires internet to generate responses.

**Q: Is my data private?**  
A: Game saves stay on your pendrive. Only your inputs are sent to Groq's API (read their privacy policy).

**Q: Can I use ChatGPT instead of Groq?**  
A: Yes! Modify `AIConnection.py` to use OpenAI's API instead.

**Q: How much does it cost to run?**  
A: Approximately $0.001 per turn. A 4-hour session (100 turns) costs ~$0.10.

**Q: Can I share this with friends?**  
A: Absolutely! Just copy the entire folder to their pendrive.

---

## 🎨 Credits

**Developer:** White Ghost(Tushar Kr) 
**AI Model:** Llama 3.1 by Meta, via Groq  
**Inspired by:** Classic CRPGs, D&D, AI Dungeon  

---

## 🌟 Enjoy Your Adventure!

*The fog awaits, traveler. Your story begins now...*

---

## 📞 Contact

- **Issues:** Check troubleshooting section above
- **GitHub:** [JustWhiteGhost :D](https://github.com/JustWhiteGhost)
- **Email:** [Click :3](mrsama5990@gmail.com)

---

**Version:** 0.0.2  
**Last Updated:** January 2026