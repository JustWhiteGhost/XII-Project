"""
Location Database - Loads and manages location data from CSV
"""
import pandas as pd
from pathlib import Path
from Config.Paths import LOCATION_CSV

class LocationDatabase:
    def __init__(self, csv_path=str(LOCATION_CSV)):
        self.csv_path = Path(csv_path)
        self.locations_df = None
        self.load_data()

    def load_data(self):
        """Load location data from CSV"""
        try:
            self.locations_df = pd.read_csv(self.csv_path, delimiter='|')
            print(f"Loaded {len(self.locations_df)} locations")
        except FileNotFoundError:
            print(f"Error: Could not find {self.csv_path}")
            self.locations_df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading location data: {e}")
            self.locations_df = pd.DataFrame()

    def get_all_locations(self):
        """Return all locations"""
        return self.locations_df

    def get_location_by_id(self, location_id):
        """Get location by location_id"""
        if self.locations_df is None or self.locations_df.empty:
            return None
        try:
            result = self.locations_df[self.locations_df['location_id'] == location_id]
            return result.iloc[0] if not result.empty else None
        except Exception as e:
            print(f"Error getting location by id: {e}")
            return None

    def get_location_by_name(self, location_name):
        """Get location by name"""
        if self.locations_df is None or self.locations_df.empty:
            return None
        result = self.locations_df[self.locations_df['location_name'] == location_name]
        return result.iloc[0] if not result.empty else None

    def get_locations_by_weather(self, weather):
        """Get all locations with specific weather"""
        if self.locations_df is None or self.locations_df.empty:
            return pd.DataFrame()
        return self.locations_df[self.locations_df['weather'] == weather]

    def get_locations_by_danger_level(self, danger_level):
        """Get all locations by danger level"""
        if self.locations_df is None or self.locations_df.empty:
            return pd.DataFrame()
        return self.locations_df[self.locations_df['danger_level'] == danger_level]

    def get_locations_by_faction(self, faction):
        """Get all locations controlled by a faction"""
        if self.locations_df is None or self.locations_df.empty:
            return pd.DataFrame()
        return self.locations_df[self.locations_df['faction_territory'] == faction]

    def get_locations_by_shop_type(self, shop_type):
        """Get all locations with a specific shop type"""
        if self.locations_df is None or self.locations_df.empty:
            return pd.DataFrame()
        return self.locations_df[self.locations_df['shop_type'] == shop_type]

    def get_unlocked_locations(self):
        """Get all unlocked locations"""
        if self.locations_df is None or self.locations_df.empty:
            return pd.DataFrame()
        return self.locations_df[self.locations_df['locked'] == False]

    def search_locations(self, **kwargs):
        """Search locations by multiple criteria"""
        result = self.locations_df
        if result is None or result.empty:
            return result
        for key, value in kwargs.items():
            if key in result.columns:
                result = result[result[key] == value]
        return result

    def get_location_coordinates(self, location_id):
        """Get (x, y) coordinates of a location"""
        loc = self.get_location_by_id(location_id)
        if loc is not None:
            return loc['x_coord'], loc['y_coord']
        return None, None

    def get_location_events(self, location_id):
        """Get events available at a location"""
        loc = self.get_location_by_id(location_id)
        if loc is not None and pd.notna(loc['events_available']):
            return loc['events_available'].split(', ')
        return []

    def get_location_bonuses(self, location_id):
        """Get rest and discovery bonuses for a location"""
        loc = self.get_location_by_id(location_id)
        if loc is not None:
            return {
                "rest_bonus": loc['rest_bonus'],
                "discovery_bonus": loc['discovery_bonus']
            }
        return {}
