"""
Travel System - Manages location transitions and door locks
"""
import pandas as pd


class TravelSystem:
    """Handles travel between locations and lock verification."""
    
    def __init__(self, locations_csv_path, location_locks_csv_path, items_csv_path):
        """Initialize travel system with location data."""
        self.locations_df = pd.read_csv(locations_csv_path, sep='|')
        self.locks_df = pd.read_csv(location_locks_csv_path, sep='|')
        self.items_df = pd.read_csv(items_csv_path, sep='|')
        
        # Create lookup maps
        self.location_map = {
            row['location_id']: row for _, row in self.locations_df.iterrows()
        }
        self.locks_map = {
            row['location_id']: row for _, row in self.locks_df.iterrows()
        }
    
    def get_location_by_id(self, location_id):
        """Get location data by ID."""
        return self.location_map.get(location_id)
    
    def get_all_locations(self):
        """Get all available locations."""
        return self.locations_df.to_dict('records')
    
    def is_location_locked(self, location_id):
        """Check if a location is locked."""
        lock_info = self.locks_map.get(location_id)
        if lock_info is None:
            return False
        val = lock_info.get('requires_key', False)
        try:
            return str(val).strip().lower() in ('true', '1', 'yes', 'y')
        except Exception:
            return bool(val)
    
    def get_lock_info(self, location_id):
        """Get lock information for a location."""
        return self.locks_map.get(location_id)
    
    def required_key_id(self, location_id):
        """Get the key item ID required for a location."""
        lock_info = self.locks_map.get(location_id)
        if lock_info is None:
            return None
        key_id = lock_info.get('key_item_id')
        if key_id is None:
            return None
        try:
            s = str(key_id).strip()
        except Exception:
            return None
        if not s or s.lower() in ('null', 'none', 'n/a'):
            return None
        return s.upper()
    
    def check_access(self, location_id, player_inventory_dict):
        """
        Check if player can access a location.
        
        Args:
            location_id: Target location ID
            player_inventory_dict: Dict with weapon_ids, armor_id, ammunition_ids, equipment_ids
        
        Returns:
            dict with 'can_access': bool, 'message': str, 'reason': str
        """
        if not self.is_location_locked(location_id):
            return {
                'can_access': True,
                'message': '',
                'reason': 'unlocked'
            }
        
        lock_info = self.get_lock_info(location_id)
        location = self.get_location_by_id(location_id)
        
        required_key_id = self.required_key_id(location_id)
        
        if required_key_id:
            # Check if player has the key
            has_key = False
            # Support both raw ids string and parsed equipment list
            equipment_ids = player_inventory_dict.get('equipment_ids', [])
            equipment_list = player_inventory_dict.get('equipment', [])
            
            if isinstance(equipment_ids, str):
                equipment_ids = [x.strip() for x in equipment_ids.split(',') if x.strip()]
            
            if required_key_id in equipment_ids:
                has_key = True
            else:
                # Check parsed equipment list of dicts
                try:
                    has_key = any(str(it.get('item_id', '')).strip().upper() == required_key_id for it in equipment_list)
                except Exception:
                    has_key = False
            
            if has_key:
                return {
                    'can_access': True,
                    'message': f"You use your key to unlock the {location['location_name']}.",
                    'reason': 'key_used'
                }
            else:
                key_name = lock_info.get('key_name', 'Key')
                return {
                    'can_access': False,
                    'message': f"This location is locked. You need the '{key_name}' to enter.",
                    'reason': 'locked_need_key'
                }
        
        return {
            'can_access': True,
            'message': '',
            'reason': 'no_key_required'
        }
    
    def get_accessible_locations(self, current_location_id, player_inventory_dict):
        """
        Get list of locations accessible from current location.
        For now, all locations are accessible from any location if keys are available.
        
        Returns:
            list of location dicts that player can access
        """
        accessible = []
        
        for location in self.get_all_locations():
            loc_id = location['location_id']
            if loc_id == current_location_id:
                continue  # Don't include current location
            
            access = self.check_access(loc_id, player_inventory_dict)
            if access['can_access']:
                accessible.append(location)
        
        return accessible
