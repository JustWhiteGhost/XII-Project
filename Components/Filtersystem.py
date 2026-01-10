# conversation_manager.py

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional


class ConversationManager:
    """
    Manages chat conversations, filtering, and dumping to files.
    Handles impression tracking and conversation history cleanup.
    """
    
    def __init__(self, dumps_directory: str = "conversation_dumps"):
        """
        Initialize the ConversationManager.
        
        Args:
            dumps_directory: Directory to save conversation dumps
        """
        self.dumps_directory = dumps_directory
        os.makedirs(dumps_directory, exist_ok=True)
    
    
    def filter_chat_history(self, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Filter chat history to:
        1. Remove "You approach X" messages
        2. Consolidate impression changes into session-based summary
        3. Remove "You end the conversation" messages
        4. Keep all actual dialogue and actions
        
        Args:
            chat_history: List of message dictionaries with 'timestamp', 'sender', 'message'
            
        Returns:
            Dictionary with 'messages' (filtered) and 'impression_summary'
        """
        
        filtered_history = []
        impression_tracker = {}
        current_character = None
        
        for msg in chat_history:
            sender = msg.get('sender', '')
            message = msg.get('message', '')
            
            # Track current character being talked to
            if sender == 'SYSTEM' and 'You approach' in message:
                # Extract character name (e.g., "You approach Sofia Redcloak.")
                match = re.search(r'You approach (.+?)\.', message)
                if match:
                    current_character = match.group(1)
                    impression_tracker[current_character] = {
                        'start_impression': 0,
                        'changes': [],
                        'final_impression': 0
                    }
                continue  # Skip this message
            
            # Track impression changes
            if sender == 'SYSTEM' and 'Impression' in message:
                if current_character:
                    # Extract impression change (e.g., "(Impression +2)")
                    match = re.search(r'Impression ([+-]\d+)', message)
                    if match:
                        change = int(match.group(1))
                        impression_tracker[current_character]['changes'].append(change)
                        impression_tracker[current_character]['final_impression'] += change
                continue  # Skip this message
            
            # Skip "end conversation" messages
            if sender == 'SYSTEM' and 'You end the conversation' in message:
                continue
            
            # Keep everything else (dialogue, actions, other system messages)
            filtered_history.append(msg)
        
        return {
            'messages': filtered_history,
            'impression_summary': impression_tracker
        }
    
    
    def format_filtered_history(self, filtered_data: Dict[str, Any]) -> str:
        """
        Format the filtered history into a readable string with impression summary.
        
        Args:
            filtered_data: Dictionary with 'messages' and 'impression_summary'
            
        Returns:
            Formatted string representation
        """
        
        output = []
        
        # Add messages
        for msg in filtered_data['messages']:
            timestamp = msg.get('timestamp', '')
            sender = msg.get('sender', '')
            message = msg.get('message', '')
            
            output.append(f"[{timestamp}] {sender}: {message}")
        
        # Add impression summary at the end
        if filtered_data['impression_summary']:
            output.append("\n" + "=" * 50)
            output.append("RELATIONSHIP SUMMARY")
            output.append("=" * 50)
            
            for character, data in filtered_data['impression_summary'].items():
                if data['changes']:
                    changes_str = " → ".join([f"{c:+d}" for c in data['changes']])
                    output.append(f"{character}:")
                    output.append(f"  Changes: {changes_str}")
                    output.append(f"  Final Impression: {data['final_impression']:+d}")
                    output.append("")
        
        return "\n".join(output)
    
    
    def dump_conversation_text(
        self, 
        chat_history: List[Dict[str, Any]], 
        char: Dict[str, Any],
        filename: Optional[str] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Dump filtered conversation to a text file.
        
        Args:
            chat_history: List of message dictionaries
            char: Character dictionary with name and other info
            filename: Optional custom filename
            include_metadata: Whether to include character metadata header
            
        Returns:
            Path to the saved file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_char_name = char['name'].replace(" ", "_")
            filename = f"{safe_char_name}_filtered_{timestamp}.txt"
        
        filepath = os.path.join(self.dumps_directory, filename)
        
        # Filter the history
        filtered_data = self.filter_chat_history(chat_history)
        
        # Format it
        formatted_output = self.format_filtered_history(filtered_data)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            if include_metadata:
                f.write(f"=== Filtered Conversation Log ===\n")
                f.write(f"Character: {char.get('name', 'Unknown')}\n")
                f.write(f"Character ID: {char.get('unique_id', 'N/A')}\n")
                f.write(f"Profession: {char.get('profession', 'N/A')}\n")
                f.write(f"Nature: {char.get('nature', 'N/A')}\n")
                f.write(f"Mood: {char.get('mood', 'N/A')}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
            
            f.write(formatted_output)
        
        return filepath
    
    
    def dump_conversation_json(
        self,
        chat_history: List[Dict[str, Any]],
        char: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Dump filtered conversation in JSON format for vector DB and knowledge graphs.
        
        Args:
            chat_history: List of message dictionaries
            char: Character dictionary
            filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_char_name = char['name'].replace(" ", "_")
            filename = f"{safe_char_name}_filtered_{timestamp}.json"
        
        filepath = os.path.join(self.dumps_directory, filename)
        
        # Filter the history
        filtered_data = self.filter_chat_history(chat_history)
        
        # Count dialogue turns
        dialogue_turns = sum(1 for msg in filtered_data['messages'] 
                            if msg.get('sender') in ['Player', char.get('name')])
        
        # Structure for vector DB and knowledge graph
        output_data = {
            "metadata": {
                "character_name": char.get('name', 'Unknown'),
                "character_id": char.get('unique_id'),
                "profession": char.get('profession'),
                "nature": char.get('nature'),
                "mood": char.get('mood'),
                "description": char.get('description'),
                "favor_tags": char.get('favor_tags', []),
                "hate_tags": char.get('hate_tags', []),
                "timestamp": datetime.now().isoformat(),
                "total_messages": len(filtered_data['messages']),
                "dialogue_turns": dialogue_turns
            },
            "conversation": filtered_data['messages'],
            "relationships": [],
            "summary": {
                "total_characters_interacted": len(filtered_data['impression_summary']),
                "total_impression_change": sum(
                    data['final_impression'] 
                    for data in filtered_data['impression_summary'].values()
                )
            }
        }
        
        # Add relationship summary
        for character, data in filtered_data['impression_summary'].items():
            output_data['relationships'].append({
                "character": character,
                "impression_changes": data['changes'],
                "total_change": data['final_impression'],
                "num_interactions": len(data['changes']),
                "average_change": (
                    data['final_impression'] / len(data['changes']) 
                    if data['changes'] else 0
                )
            })
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    
    def dump_both_formats(
        self,
        chat_history: List[Dict[str, Any]],
        char: Dict[str, Any],
        base_filename: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Dump conversation in both text and JSON formats.
        
        Args:
            chat_history: List of message dictionaries
            char: Character dictionary
            base_filename: Optional base filename (extensions will be added)
            
        Returns:
            Dictionary with 'text' and 'json' file paths
        """
        
        if base_filename:
            text_filename = f"{base_filename}.txt"
            json_filename = f"{base_filename}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_char_name = char['name'].replace(" ", "_")
            text_filename = f"{safe_char_name}_filtered_{timestamp}.txt"
            json_filename = f"{safe_char_name}_filtered_{timestamp}.json"
        
        return {
            'text': self.dump_conversation_text(chat_history, char, text_filename),
            'json': self.dump_conversation_json(chat_history, char, json_filename)
        }
    
    
    def get_conversation_summary(
        self,
        chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get a quick summary of the conversation without dumping to file.
        
        Args:
            chat_history: List of message dictionaries
            
        Returns:
            Summary dictionary with key statistics
        """
        
        filtered_data = self.filter_chat_history(chat_history)
        
        summary = {
            'total_messages': len(filtered_data['messages']),
            'player_messages': sum(1 for msg in filtered_data['messages'] 
                                  if msg.get('sender') == 'Player'),
            'action_messages': sum(1 for msg in filtered_data['messages'] 
                                   if msg.get('sender') == 'ACTION'),
            'characters_met': list(filtered_data['impression_summary'].keys()),
            'total_impression_changes': {}
        }
        
        for character, data in filtered_data['impression_summary'].items():
            summary['total_impression_changes'][character] = data['final_impression']
        
        return summary


# Example usage and helper function
def create_conversation_manager(dumps_dir: str = "conversation_dumps") -> ConversationManager:
    """
    Factory function to create a ConversationManager instance.
    
    Args:
        dumps_dir: Directory to save conversation dumps
        
    Returns:
        ConversationManager instance
    """
    return ConversationManager(dumps_directory=dumps_dir)