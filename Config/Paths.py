from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "Data CSVs"
SAVES_DIR = PROJECT_ROOT / "saves"
MEMORY_DIR = PROJECT_ROOT / "memory"

# CSV files
CHARACTER_CSV = DATA_DIR / "Character_Info.csv"
LOCATION_CSV = DATA_DIR / "Location_Info.csv"
HERO_CSV = DATA_DIR / "Hero.csv"
ITEM_CSV = DATA_DIR / "Item_Lookup.csv"
SKILL_CSV = DATA_DIR / "Skill_Lookup.csv"

# Generated files
HERO_SUMMARY = PROJECT_ROOT / "data.txt"
CONFIG_FILE = PROJECT_ROOT / "config.json"

def ensure_directories():
    SAVES_DIR.mkdir(exist_ok=True)
    MEMORY_DIR.mkdir(exist_ok=True)

ensure_directories()