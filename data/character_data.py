"""
Character Database - Loads and manages character data from CSV
"""
import pandas as pd
from pathlib import Path


class CharacterDatabase:
    def __init__(self, csv_path="D:\\Projects\\XII Project\\Data CSVs\\Character_Info.csv"):
        self.csv_path = Path(csv_path)
        self.characters_df = None
        self.load_data()
    
    def load_data(self):
        """Load character data from CSV"""
        try:
            self.characters_df = pd.read_csv(self.csv_path, delimiter='|')
            print(f"Loaded {len(self.characters_df)} characters")
        except FileNotFoundError:
            print(f"Error: Could not find {self.csv_path}")
            self.characters_df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading character data: {e}")
            self.characters_df = pd.DataFrame()
    
    def get_all_characters(self):
        """Return all characters"""
        return self.characters_df
    
    def get_character_by_id(self, unique_id):
        """Get character by unique_id"""
        if self.characters_df is None or self.characters_df.empty:
            return None
        try:
            result = self.characters_df[self.characters_df['unique_id'] == unique_id]
            return result.iloc[0] if not result.empty else None
        except Exception as e:
            print(f"Error getting character by id: {e}")
            return None
    
    def get_character_by_name(self, name):
        """Get character by name"""
        if self.characters_df is None or self.characters_df.empty:
            return None
        result = self.characters_df[self.characters_df['name'] == name]
        return result.iloc[0] if not result.empty else None
    
    def get_characters_by_location(self, location):
        """Get all characters at a location"""
        if self.characters_df is None or self.characters_df.empty:
            return pd.DataFrame()
        return self.characters_df[self.characters_df['location'] == location]
    
    def get_characters_by_profession(self, profession):
        """Get all characters with a profession"""
        if self.characters_df is None or self.characters_df.empty:
            return pd.DataFrame()
        return self.characters_df[self.characters_df['profession'] == profession]
    
    def get_characters_by_mood(self, mood):
        """Get all characters with a mood"""
        if self.characters_df is None or self.characters_df.empty:
            return pd.DataFrame()
        return self.characters_df[self.characters_df['mood'] == mood]
    
    def search_characters(self, **kwargs):
        """Search characters by multiple criteria"""
        result = self.characters_df
        if result is None or result.empty:
            return result
        for key, value in kwargs.items():
            if key in result.columns:
                result = result[result[key] == value]
        return result
    
    def get_character_tags(self, unique_id):
        """Get favor and hate tags for a character"""
        char = self.get_character_by_id(unique_id)
        if char is not None:
            favor_tags = char['favor_tags'].split(', ') if pd.notna(char['favor_tags']) else []
            hate_tags = char['hate_tags'].split(', ') if pd.notna(char['hate_tags']) else []
            return favor_tags, hate_tags
        return [], []