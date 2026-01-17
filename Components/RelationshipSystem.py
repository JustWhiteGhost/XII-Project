"""
Relationship System - Tracks NPC relationships and manages relation changes over time
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import json


class RelationshipSystem:
    def __init__(
        self, 
        characters_csv_path: str,
        relationship_log_path: str = "saves/relationship_history.csv"
    ):
        """
        Initialize the relationship tracking system.
        
        Args:
            characters_csv_path: Path to Character_Info.csv
            relationship_log_path: Path to save relationship change history
        """
        self.characters_df = pd.read_csv(characters_csv_path, sep='|')
        self.relationship_log_path = relationship_log_path
        
        # Initialize relationship tracking dictionary
        # Format: {npc_id: current_relation_score}
        self.relationships = {}
        
        # Load base relations from CSV
        for _, char in self.characters_df.iterrows():
            self.relationships[char['unique_id']] = int(char['relation'])
        
        # Load or create relationship history
        try:
            self.relationship_history_df = pd.read_csv(relationship_log_path)
        except FileNotFoundError:
            self.relationship_history_df = pd.DataFrame(columns=[
                'timestamp', 'npc_id', 'npc_name', 'interaction_type',
                'impression_change', 'relation_before', 'relation_after',
                'location', 'notes'
            ])
    
    def get_relation(self, npc_id: str) -> int:
        """
        Get current relationship score with an NPC.
        
        Args:
            npc_id: Unique ID of the character
            
        Returns:
            Relation score (-10 to +10)
        """
        return self.relationships.get(npc_id, 0)
    
    def get_relation_tier(self, relation_score: int) -> str:
        """
        Convert numeric relation to descriptive tier.
        
        Args:
            relation_score: Integer from -10 to +10
            
        Returns:
            String description of relationship
        """
        if relation_score >= 9:
            return "Devoted"
        elif relation_score >= 7:
            return "Trusted Friend"
        elif relation_score >= 5:
            return "Friend"
        elif relation_score >= 3:
            return "Friendly"
        elif relation_score >= 1:
            return "Acquaintance"
        elif relation_score == 0:
            return "Neutral"
        elif relation_score >= -2:
            return "Unfriendly"
        elif relation_score >= -4:
            return "Hostile"
        elif relation_score >= -6:
            return "Enemy"
        elif relation_score >= -8:
            return "Hated"
        else:
            return "Mortal Enemy"
    
    def modify_relation(
        self,
        npc_id: str,
        change: int,
        interaction_type: str = "conversation",
        location: str = "Unknown",
        notes: str = ""
    ) -> Dict:
        """
        Change relationship score with an NPC.
        
        Args:
            npc_id: Unique ID of the character
            change: Amount to change (-5 to +5 typically)
            interaction_type: Type of interaction (conversation, trade, gift, quest, etc.)
            location: Where the interaction happened
            notes: Additional context
            
        Returns:
            Dictionary with results of the change
        """
        # Get character info
        char = self.characters_df[self.characters_df['unique_id'] == npc_id]
        if char.empty:
            return {
                'success': False,
                'message': "Character not found."
            }
        
        char = char.iloc[0]
        
        # Get current relation
        old_relation = self.get_relation(npc_id)
        
        # Apply change with bounds checking (-10 to +10)
        new_relation = max(-10, min(10, old_relation + change))
        
        # Update internal tracking
        self.relationships[npc_id] = new_relation
        
        # Get tier descriptions
        old_tier = self.get_relation_tier(old_relation)
        new_tier = self.get_relation_tier(new_relation)
        
        # Log the change
        self._log_relationship_change(
            npc_id=npc_id,
            npc_name=char['name'],
            interaction_type=interaction_type,
            impression_change=change,
            relation_before=old_relation,
            relation_after=new_relation,
            location=location,
            notes=notes
        )
        
        # Determine if tier changed
        tier_changed = old_tier != new_tier
        
        return {
            'success': True,
            'npc_name': char['name'],
            'change': change,
            'relation_before': old_relation,
            'relation_after': new_relation,
            'tier_before': old_tier,
            'tier_after': new_tier,
            'tier_changed': tier_changed,
            'message': self._generate_feedback_message(
                char['name'], change, old_tier, new_tier, tier_changed
            )
        }
    
    def _generate_feedback_message(
        self,
        npc_name: str,
        change: int,
        old_tier: str,
        new_tier: str,
        tier_changed: bool
    ) -> str:
        """Generate a descriptive message about the relationship change."""
        if tier_changed:
            if change > 0:
                return f"{npc_name} now considers you a {new_tier}! (was {old_tier})"
            else:
                return f"{npc_name}'s opinion of you has worsened to {new_tier}. (was {old_tier})"
        else:
            if change > 0:
                return f"{npc_name} likes you more. ({new_tier}, {change:+d})"
            elif change < 0:
                return f"{npc_name} likes you less. ({new_tier}, {change:+d})"
            else:
                return f"Your relationship with {npc_name} remains unchanged."
    
    def _log_relationship_change(
        self,
        npc_id: str,
        npc_name: str,
        interaction_type: str,
        impression_change: int,
        relation_before: int,
        relation_after: int,
        location: str,
        notes: str
    ):
        """Internal method to log relationship changes for visualization."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'npc_id': npc_id,
            'npc_name': npc_name,
            'interaction_type': interaction_type,
            'impression_change': impression_change,
            'relation_before': relation_before,
            'relation_after': relation_after,
            'location': location,
            'notes': notes
        }
        
        # Add to DataFrame
        new_row = pd.DataFrame([log_entry])
        self.relationship_history_df = pd.concat(
            [self.relationship_history_df, new_row], 
            ignore_index=True
        )
        
        # Save to CSV
        self.relationship_history_df.to_csv(self.relationship_log_path, index=False)
    
    def get_relationship_summary(self) -> Dict:
        """Get summary statistics of all relationships."""
        if not self.relationships:
            return {
                'total_npcs_met': 0,
                'friends': 0,
                'enemies': 0,
                'average_relation': 0,
                'best_friend': None,
                'worst_enemy': None
            }
        
        relations = list(self.relationships.values())
        
        friends = sum(1 for r in relations if r >= 3)
        enemies = sum(1 for r in relations if r <= -3)
        
        # Find best friend and worst enemy
        best_npc_id = max(self.relationships, key=self.relationships.get)
        worst_npc_id = min(self.relationships, key=self.relationships.get)
        
        best_char = self.characters_df[self.characters_df['unique_id'] == best_npc_id]
        worst_char = self.characters_df[self.characters_df['unique_id'] == worst_npc_id]
        
        return {
            'total_npcs_met': len(self.relationships),
            'friends': friends,
            'enemies': enemies,
            'neutral': len(relations) - friends - enemies,
            'average_relation': sum(relations) / len(relations),
            'best_friend': {
                'name': best_char.iloc[0]['name'] if not best_char.empty else None,
                'relation': self.relationships[best_npc_id]
            },
            'worst_enemy': {
                'name': worst_char.iloc[0]['name'] if not worst_char.empty else None,
                'relation': self.relationships[worst_npc_id]
            }
        }
    
    def get_npc_relationships(self, relation_threshold: int = 0) -> List[Dict]:
        """
        Get all NPCs above a certain relation threshold.
        
        Args:
            relation_threshold: Minimum relation score
            
        Returns:
            List of dictionaries with NPC data
        """
        results = []
        
        for npc_id, relation in self.relationships.items():
            if relation >= relation_threshold:
                char = self.characters_df[self.characters_df['unique_id'] == npc_id]
                if not char.empty:
                    char = char.iloc[0]
                    results.append({
                        'unique_id': npc_id,
                        'name': char['name'],
                        'relation': relation,
                        'tier': self.get_relation_tier(relation),
                        'profession': char['profession'],
                        'location': char['location']
                    })
        
        # Sort by relation (highest first)
        results.sort(key=lambda x: x['relation'], reverse=True)
        
        return results
    
    def get_interaction_history(self, npc_id: str) -> pd.DataFrame:
        """
        Get all past interactions with a specific NPC.
        
        Args:
            npc_id: Unique ID of the character
            
        Returns:
            DataFrame of all interactions
        """
        if self.relationship_history_df.empty:
            return pd.DataFrame()
        
        return self.relationship_history_df[
            self.relationship_history_df['npc_id'] == npc_id
        ].copy()
    
    def export_relationships(self, filepath: str = "saves/current_relationships.json"):
        """Export current relationship state to JSON."""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'relationships': {}
        }
        
        for npc_id, relation in self.relationships.items():
            char = self.characters_df[self.characters_df['unique_id'] == npc_id]
            if not char.empty:
                char = char.iloc[0]
                export_data['relationships'][npc_id] = {
                    'name': char['name'],
                    'relation': relation,
                    'tier': self.get_relation_tier(relation),
                    'profession': char['profession'],
                    'location': char['location']
                }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath