import pandas as pd
from typing import Dict, List, Optional, Union

class CharacterParser:
    def __init__(self, character_csv: str, items_csv: str, skills_csv: str):
        self.character_csv_path = character_csv
        self.characters_df = pd.read_csv(character_csv, sep='|')
        self.items_df = pd.read_csv(items_csv, sep='|')
        self.skills_df = pd.read_csv(skills_csv, sep='|')
        
        # Store current character (defaults to first character)
        self.current_character = None
        if len(self.characters_df) > 0:
            self.current_character = self.characters_df.iloc[0].to_dict()
    
    def set_character(self, character_name: str) -> bool:
        char = self.characters_df[self.characters_df['character_name'] == character_name]
        if len(char) > 0:
            self.current_character = char.iloc[0].to_dict()
            return True
        return False
    
    def save_current_character(self) -> bool:
        """
        Save current character changes back to the CSV file.
        
        Returns:
            bool: True if save was successful
        """
        if not self.current_character:
            return False
        
        # Find the character's row index in the dataframe
        char_name = self.current_character['character_name']
        char_idx = self.characters_df[self.characters_df['character_name'] == char_name].index
        
        if len(char_idx) == 0:
            return False
        
        # Update the dataframe with current character data
        for col in self.current_character.keys():
            if col in self.characters_df.columns:
                self.characters_df.at[char_idx[0], col] = self.current_character[col]
        
        # Save to CSV
        try:
            self.characters_df.to_csv(self.character_csv_path, sep='|', index=False)
            return True
        except Exception as e:
            print(f"Error saving character: {e}")
            return False
    
    def get_basic_info(self) -> Dict:
        """Get basic character information."""
        if not self.current_character:
            return {}
        
        return {
            'name': self.current_character['character_name'],
            'player': self.current_character['player_name'],
            'age': self.current_character['age'],
            'race': self.current_character['race'],
            'class': self.current_character['class'],
            'level': self.current_character['level'],
            'background': self.current_character['background']
        }
    
    def get_ability_scores(self) -> Dict:
        """Get all ability scores and modifiers."""
        if not self.current_character:
            return {}
        
        return {
            'strength': {
                'score': self.current_character['strength'],
                'modifier': self.current_character['strength_mod']
            },
            'dexterity': {
                'score': self.current_character['dexterity'],
                'modifier': self.current_character['dexterity_mod']
            },
            'constitution': {
                'score': self.current_character['constitution'],
                'modifier': self.current_character['constitution_mod']
            },
            'intelligence': {
                'score': self.current_character['intelligence'],
                'modifier': self.current_character['intelligence_mod']
            },
            'wisdom': {
                'score': self.current_character['wisdom'],
                'modifier': self.current_character['wisdom_mod']
            },
            'charisma': {
                'score': self.current_character['charisma'],
                'modifier': self.current_character['charisma_mod']
            }
        }
    
    def get_combat_stats(self) -> Dict:
        """Get combat-related statistics."""
        if not self.current_character:
            return {}
        
        return {
            'hp': {
                'current': self.current_character['current_hp'],
                'max': self.current_character['max_hp']
            },
            'armor_class': self.current_character['armor_class'],
            'speed': self.current_character['speed'],
            'proficiency_bonus': self.current_character['proficiency_bonus'],
            'sanity': {
                'current': self.current_character['sanity'],
                'max': self.current_character['max_sanity']
            }
        }
    
    def get_skills(self) -> List[Dict]:
        if not self.current_character:
            return []
        
        skill_ids = str(self.current_character['skills_proficient']).split(', ')
        skills = []
        
        for skill_id in skill_ids:
            skill_id = skill_id.strip()
            skill_data = self.skills_df[self.skills_df['skill_id'] == skill_id]
            
            if len(skill_data) > 0:
                skill = skill_data.iloc[0].to_dict()
                # Add calculated bonus
                ability = skill['governing_ability'].lower()
                modifier_key = f"{ability}_mod"
                if modifier_key in self.current_character:
                    modifier = int(str(self.current_character[modifier_key]).replace('+', ''))
                    proficiency = int(str(self.current_character['proficiency_bonus']).replace('+', ''))
                    skill['total_bonus'] = modifier + proficiency
                
                skills.append(skill)
        
        return skills
    
    def get_skill_bonus(self, skill_id: str) -> Optional[int]:
        """
        Calculate total bonus for a specific skill.
        
        Args:
            skill_id: ID of the skill (e.g., 'SKL008')
            
        Returns:
            Total bonus or None if not proficient
        """
        if not self.current_character:
            return None
        
        skill_ids = str(self.current_character['skills_proficient']).split(', ')
        
        if skill_id not in skill_ids:
            return None
        
        skill_data = self.skills_df[self.skills_df['skill_id'] == skill_id]
        if len(skill_data) == 0:
            return None
        
        ability = skill_data.iloc[0]['governing_ability'].lower()
        modifier_key = f"{ability}_mod"
        
        if modifier_key in self.current_character:
            modifier = int(str(self.current_character[modifier_key]).replace('+', ''))
            proficiency = int(str(self.current_character['proficiency_bonus']).replace('+', ''))
            return modifier + proficiency
        
        return None
    
    def get_weapons(self) -> List[Dict]:
        """
        Get all equipped weapons with full stats.
        
        Returns:
            List of weapon dictionaries
        """
        if not self.current_character:
            return []
        
        weapon_ids = str(self.current_character['weapon_ids']).split(', ')
        weapons = []
        
        for weapon_id in weapon_ids:
            weapon_id = weapon_id.strip()
            weapon_data = self.items_df[self.items_df['item_id'] == weapon_id]
            
            if len(weapon_data) > 0:
                weapon = weapon_data.iloc[0].to_dict()
                
                # Calculate attack bonus
                if 'firearm' in str(weapon['subtype']).lower() or 'ranged' in str(weapon['subtype']).lower():
                    # Use DEX for ranged weapons
                    modifier = int(str(self.current_character['dexterity_mod']).replace('+', ''))
                else:
                    # Use STR for melee weapons
                    modifier = int(str(self.current_character['strength_mod']).replace('+', ''))
                
                proficiency = int(str(self.current_character['proficiency_bonus']).replace('+', ''))
                weapon['attack_bonus'] = modifier + proficiency
                weapon['damage_bonus'] = modifier
                
                weapons.append(weapon)
        
        return weapons
    
    def get_armor(self) -> Optional[Dict]:
        """
        Get equipped armor details.
        
        Returns:
            Armor dictionary or None
        """
        if not self.current_character:
            return None
        
        armor_id = str(self.current_character['armor_id']).strip()
        armor_data = self.items_df[self.items_df['item_id'] == armor_id]
        
        if len(armor_data) > 0:
            return armor_data.iloc[0].to_dict()
        
        return None
    
    def get_ammunition(self) -> List[Dict]:
        """
        Get ammunition with quantities.
        
        Returns:
            List of ammunition dictionaries with quantities
        """
        if not self.current_character:
            return []
        
        ammo_str = str(self.current_character['ammunition_ids'])
        if ammo_str == 'nan' or not ammo_str:
            return []
        
        ammo_entries = ammo_str.split(', ')
        ammunition = []
        
        for entry in ammo_entries:
            parts = entry.split(':')
            ammo_id = parts[0].strip()
            quantity = int(parts[1]) if len(parts) > 1 else 0
            
            ammo_data = self.items_df[self.items_df['item_id'] == ammo_id]
            if len(ammo_data) > 0:
                ammo = ammo_data.iloc[0].to_dict()
                ammo['quantity'] = quantity
                ammunition.append(ammo)
        
        return ammunition
    
    def get_inscribed_spells(self) -> List[Dict]:
        """
        Get inscribed spells with quantities.
        
        Returns:
            List of spell dictionaries with quantities
        """
        if not self.current_character:
            return []
        
        spell_str = str(self.current_character['inscribed_spell_ids'])
        if spell_str == 'nan' or not spell_str:
            return []
        
        spell_entries = spell_str.split(', ')
        spells = []
        
        for entry in spell_entries:
            parts = entry.split(':')
            spell_id = parts[0].strip()
            quantity = int(parts[1]) if len(parts) > 1 else 0
            
            spell_data = self.items_df[self.items_df['item_id'] == spell_id]
            if len(spell_data) > 0:
                spell = spell_data.iloc[0].to_dict()
                spell['quantity'] = quantity
                spells.append(spell)
        
        return spells
    
    def get_equipment(self) -> List[Dict]:
        """
        Get all equipment items.
        
        Returns:
            List of equipment dictionaries
        """
        if not self.current_character:
            return []
        
        equip_str = str(self.current_character['equipment_ids'])
        if equip_str == 'nan' or not equip_str:
            return []
        
        equip_ids = equip_str.split(', ')
        equipment = []
        
        for equip_id in equip_ids:
            equip_id = equip_id.strip()
            equip_data = self.items_df[self.items_df['item_id'] == equip_id]
            
            if len(equip_data) > 0:
                equipment.append(equip_data.iloc[0].to_dict())
        
        return equipment
    
    def get_light_sources(self) -> List[Dict]:
        """
        Get light sources with quantities.
        
        Returns:
            List of light source dictionaries with quantities
        """
        if not self.current_character:
            return []
        
        light_str = str(self.current_character['light_source_ids'])
        if light_str == 'nan' or not light_str:
            return []
        
        light_entries = light_str.split(', ')
        lights = []
        
        for entry in light_entries:
            parts = entry.split(':')
            light_id = parts[0].strip()
            quantity = int(parts[1]) if len(parts) > 1 else 0
            
            light_data = self.items_df[self.items_df['item_id'] == light_id]
            if len(light_data) > 0:
                light = light_data.iloc[0].to_dict()
                light['quantity'] = quantity
                lights.append(light)
        
        return lights
    
    def get_consumables(self) -> List[Dict]:
        """
        Get consumable items with quantities.
        
        Returns:
            List of consumable dictionaries with quantities
        """
        if not self.current_character:
            return []
        
        cons_str = str(self.current_character['consumable_ids'])
        if cons_str == 'nan' or not cons_str:
            return []
        
        cons_entries = cons_str.split(', ')
        consumables = []
        
        for entry in cons_entries:
            parts = entry.split(':')
            cons_id = parts[0].strip()
            quantity = int(parts[1]) if len(parts) > 1 else 0
            
            cons_data = self.items_df[self.items_df['item_id'] == cons_id]
            if len(cons_data) > 0:
                cons = cons_data.iloc[0].to_dict()
                cons['quantity'] = quantity
                consumables.append(cons)
        
        return consumables
    
    def get_all_inventory(self) -> Dict:
        """
        Get complete inventory organized by type.
        
        Returns:
            Dictionary with all inventory items organized
        """
        return {
            'weapons': self.get_weapons(),
            'armor': self.get_armor(),
            'ammunition': self.get_ammunition(),
            'inscribed_spells': self.get_inscribed_spells(),
            'equipment': self.get_equipment(),
            'light_sources': self.get_light_sources(),
            'consumables': self.get_consumables(),
            'currency': self.current_character.get('currency', '0gp') if self.current_character else '0gp'
        }
    def get_location(self) -> str:
        """Get current character's location."""
        if not self.current_character:
            return {}
        
        return self.current_character.get('location_id', 000000)
    def get_abilities_and_traits(self) -> Dict:
        """Get class features, racial traits, and special abilities."""
        if not self.current_character:
            return {}
        
        return {
            'class_features': self.current_character.get('class_features', ''),
            'racial_traits': self.current_character.get('racial_traits', ''),
            'combat_style': self.current_character.get('combat_style', ''),
            'special_abilities': self.current_character.get('special_abilities', '')
        }
    
    def get_conditions_and_modifiers(self) -> Dict:
        """Get current conditions and situational modifiers."""
        if not self.current_character:
            return {}
        
        return {
            'resistances': self.current_character.get('resistances', 'None'),
            'vulnerabilities': self.current_character.get('vulnerabilities', 'None'),
            'current_conditions': self.current_character.get('current_conditions', 'None'),
            'advantage_situations': self.current_character.get('advantage_situations', ''),
            'disadvantage_situations': self.current_character.get('disadvantage_situations', '')
        }
    
    def get_character_profile(self) -> Dict:
        """Get personality, appearance, and character details."""
        if not self.current_character:
            return {}
        
        return {
            'personality_traits': self.current_character.get('personality_traits', ''),
            'appearance': self.current_character.get('appearance', ''),
            'fears': self.current_character.get('fears', ''),
            'goals': self.current_character.get('goals', ''),
            'special_notes': self.current_character.get('special_notes', '')
        }
    
    def get_complete_character_sheet(self) -> Dict:
        """
        Get everything about the character in one organized dictionary.
        
        Returns:
            Complete character information
        """
        return {
            'basic_info': self.get_basic_info(),
            'ability_scores': self.get_ability_scores(),
            'combat_stats': self.get_combat_stats(),
            'skills': self.get_skills(),
            'inventory': self.get_all_inventory(),
            'abilities': self.get_abilities_and_traits(),
            'conditions': self.get_conditions_and_modifiers(),
            'profile': self.get_character_profile()
        }
    
    def format_for_ai_gm(self) -> str:
        """
        Format character data as a readable string for AI Game Master.
        
        Returns:
            Formatted character sheet as string
        """
        char = self.get_complete_character_sheet()
        
        output = f"""
CHARACTER SHEET: {char['basic_info']['name']}
{'='*60}

BASIC INFORMATION:
- Name: {char['basic_info']['name']}
- Player: {char['basic_info']['player']}
- Race: {char['basic_info']['race']}, Age: {char['basic_info']['age']}
- Class: {char['basic_info']['class']} (Level {char['basic_info']['level']})
- Background: {char['basic_info']['background']}

ABILITY SCORES:
- Strength: {char['ability_scores']['strength']['score']} ({char['ability_scores']['strength']['modifier']})
- Dexterity: {char['ability_scores']['dexterity']['score']} ({char['ability_scores']['dexterity']['modifier']})
- Constitution: {char['ability_scores']['constitution']['score']} ({char['ability_scores']['constitution']['modifier']})
- Intelligence: {char['ability_scores']['intelligence']['score']} ({char['ability_scores']['intelligence']['modifier']})
- Wisdom: {char['ability_scores']['wisdom']['score']} ({char['ability_scores']['wisdom']['modifier']})
- Charisma: {char['ability_scores']['charisma']['score']} ({char['ability_scores']['charisma']['modifier']})

COMBAT STATS:
- HP: {char['combat_stats']['hp']['current']}/{char['combat_stats']['hp']['max']}
- AC: {char['combat_stats']['armor_class']}
- Speed: {char['combat_stats']['speed']} ft
- Proficiency Bonus: {char['combat_stats']['proficiency_bonus']}
- Sanity: {char['combat_stats']['sanity']['current']}/{char['combat_stats']['sanity']['max']}

PROFICIENT SKILLS:
"""
        for skill in char['skills']:
            output += f"- {skill['skill_name']} ({skill['governing_ability']}): +{skill.get('total_bonus', 0)}\n"
        
        output += "\nWEAPONS:\n"
        for weapon in char['inventory']['weapons']:
            output += f"- {weapon['item_name']}: +{weapon['attack_bonus']} to hit, {weapon['damage_dice']}+{weapon['damage_bonus']} {weapon['damage_type']}\n"
            if weapon.get('range_normal', 0) > 0:
                output += f"  Range: {weapon['range_normal']}/{weapon['range_max']} ft\n"
        
        output += f"\nARMOR:\n"
        if char['inventory']['armor']:
            armor = char['inventory']['armor']
            output += f"- {armor['item_name']}: AC {armor['armor_class_bonus']} + DEX\n"
        
        output += "\nAMMUNITION:\n"
        for ammo in char['inventory']['ammunition']:
            output += f"- {ammo['item_name']}: {ammo['quantity']} remaining\n"
        
        output += "\nINSCRIBED SPELLS (One-time use magic):\n"
        for spell in char['inventory']['inscribed_spells']:
            output += f"- {spell['item_name']}: {spell['quantity']} remaining\n  Effect: {spell['special_effects']}\n"
        
        output += "\nLIGHT SOURCES:\n"
        for light in char['inventory']['light_sources']:
            output += f"- {light['item_name']}: {light['quantity']} remaining\n"
        
        output += "\nEQUIPMENT & CONSUMABLES:\n"
        for item in char['inventory']['equipment']:
            output += f"- {item['item_name']}\n"
        for cons in char['inventory']['consumables']:
            output += f"- {cons['item_name']}: {cons['quantity']} remaining\n"
        
        output += f"\nCURRENCY: {char['inventory']['currency']}\n"
        
        output += f"\nCLASS FEATURES:\n{char['abilities']['class_features']}\n"
        output += f"\nRACIAL TRAITS:\n{char['abilities']['racial_traits']}\n"
        output += f"\nCOMBAT STYLE:\n{char['abilities']['combat_style']}\n"
        output += f"\nSPECIAL ABILITIES:\n{char['abilities']['special_abilities']}\n"
        
        output += f"\nCONDITIONS & MODIFIERS:\n"
        output += f"- Current Conditions: {char['conditions']['current_conditions']}\n"
        output += f"- Advantage On: {char['conditions']['advantage_situations']}\n"
        output += f"- Disadvantage On: {char['conditions']['disadvantage_situations']}\n"
        
        output += f"\nCHARACTER PROFILE:\n"
        output += f"- Personality: {char['profile']['personality_traits']}\n"
        output += f"- Appearance: {char['profile']['appearance']}\n"
        output += f"- Fears: {char['profile']['fears']}\n"
        output += f"- Goals: {char['profile']['goals']}\n"
        output += f"\nNOTES: {char['profile']['special_notes']}\n"
        
        return output