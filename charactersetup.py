from Components.AIConnection import AIConnection
from data.HeroData import CharacterParser
import json
import os
from pathlib import Path
from Config.Paths import HERO_CSV, ITEM_CSV, SKILL_CSV

class CharacterSetup:
    def __init__(self):
        self.phraser = CharacterParser(str(HERO_CSV),
                                       str(ITEM_CSV),
                                       str(SKILL_CSV))
        self.ai = AIConnection()
    def summarize_hero(self):
        path = Path(__file__).parent / "data.txt"
        data = []
        df = self.phraser.characters_df.to_dict('records')
        for char in df:
            self.phraser.set_character(char['character_name'])
            hero_data = self.phraser.format_for_ai_gm()
            data.append(f"Profile for {char['character_name']}:\n" + "".join(self.ai.characterProfiler(hero_data)))
        full_summary = "\n\n".join(data)
        try:
            with open(path, "w") as file:
                file.write(full_summary)
        except Exception as e:
            print(f"Error writing to file: {e}")



if __name__ == "__main__":
    setup = CharacterSetup()
    setup.summarize_hero()