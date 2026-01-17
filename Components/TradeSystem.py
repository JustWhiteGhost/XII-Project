"""
Trade System - Handles buying/selling items and currency management
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class TradeSystem:
    def __init__(self, items_csv_path: str, trade_log_path: str = "saves/trade_history.csv", 
                 merchant_inventory_path: str = "Data CSVs/Merchant_Inventory.csv"):
        """
        Initialize the trade system.
        
        Args:
            items_csv_path: Path to Item_Lookup.csv
            trade_log_path: Path to save trade transaction history
            merchant_inventory_path: Path to Merchant_Inventory.csv
        """
        self.items_df = pd.read_csv(items_csv_path, sep='|')
        self.trade_log_path = trade_log_path
        self.merchant_inventory_path = merchant_inventory_path
        self.trade_history = []
        
        # Load merchant inventory
        try:
            self.merchant_inventory_df = pd.read_csv(merchant_inventory_path, sep='|')
        except FileNotFoundError:
            self.merchant_inventory_df = pd.DataFrame(columns=[
                'npc_id', 'npc_name', 'item_id', 'quantity', 'price_modifier', 'always_stock'
            ])
        
        # Load existing trade history if it exists
        try:
            self.trade_history_df = pd.read_csv(trade_log_path)
        except FileNotFoundError:
            self.trade_history_df = pd.DataFrame(columns=[
                'timestamp', 'transaction_type', 'item_id', 'item_name', 
                'quantity', 'unit_price', 'total_cost', 'npc_name', 
                'player_gold_before', 'player_gold_after'
            ])
    
    def parse_currency(self, currency_str: str) -> int:
        """
        Convert currency string (e.g., '85gp', '28gp 7sp') to integer copper pieces.
        1 gp = 100 cp, 1 sp = 10 cp
        
        Args:
            currency_str: String like '85gp', '5sp', or '28gp 7sp 3cp'
            
        Returns:
            Total value in copper pieces
        """
        currency_str = str(currency_str).lower().strip()
        
        total_cp = 0
        
        # Parse gold (gp)
        if 'gp' in currency_str:
            gp_part = currency_str.split('gp')[0].strip()
            # Extract just the number before gp (handle "28gp 7sp" -> "28")
            gp_num = ''.join(c for c in gp_part.split()[-1] if c.isdigit())
            if gp_num:
                total_cp += int(gp_num) * 100
        
        # Parse silver (sp)
        if 'sp' in currency_str:
            # Get text between gp and sp, or before sp if no gp
            if 'gp' in currency_str:
                sp_part = currency_str.split('gp')[1].split('sp')[0].strip()
            else:
                sp_part = currency_str.split('sp')[0].strip()
            sp_num = ''.join(c for c in sp_part.split()[-1] if c.isdigit())
            if sp_num:
                total_cp += int(sp_num) * 10
        
        # Parse copper (cp)
        if 'cp' in currency_str and 'gp' not in currency_str:
            # Get text before cp
            if 'sp' in currency_str:
                cp_part = currency_str.split('sp')[1].split('cp')[0].strip()
            else:
                cp_part = currency_str.split('cp')[0].strip()
            cp_num = ''.join(c for c in cp_part.split()[-1] if c.isdigit())
            if cp_num:
                total_cp += int(cp_num)
        
        return total_cp
    
    def format_currency(self, copper_pieces: int) -> str:
        """
        Convert copper pieces to readable currency string.
        
        Args:
            copper_pieces: Total value in copper
            
        Returns:
            Formatted string like '8gp 5sp 3cp'
        """
        gp = copper_pieces // 100
        remaining = copper_pieces % 100
        sp = remaining // 10
        cp = remaining % 10
        
        parts = []
        if gp > 0:
            parts.append(f"{gp}gp")
        if sp > 0:
            parts.append(f"{sp}sp")
        if cp > 0:
            parts.append(f"{cp}cp")
        
        return " ".join(parts) if parts else "0cp"
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get item data by ID."""
        result = self.items_df[self.items_df['item_id'] == item_id]
        return result.iloc[0].to_dict() if not result.empty else None
    
    def calculate_price(
        self, 
        item_id: str, 
        quantity: int = 1,
        npc_relation: int = 0,
        player_charisma_mod: int = 0,
        is_buying: bool = True
    ) -> Tuple[int, float]:
        """
        Calculate final price with modifiers.
        
        Args:
            item_id: ID of the item
            quantity: How many items
            npc_relation: NPC's relation score (-10 to +10)
            player_charisma_mod: Player's charisma modifier
            is_buying: True if player is buying, False if selling
            
        Returns:
            Tuple of (total_price_in_cp, discount_percentage)
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return 0, 0.0
        
        # Base price in copper pieces
        base_price_cp = self.parse_currency(item['cost'])
        
        # Calculate discount based on relationship and charisma
        # Relation: -10 to +10 gives -50% to +50% discount
        # Charisma: -2 to +5 gives -10% to +25% discount
        relation_discount = (npc_relation / 10) * 0.5  # -50% to +50%
        charisma_discount = (player_charisma_mod / 10) * 0.25  # -10% to +25%
        
        total_discount = relation_discount + charisma_discount
        
        # If selling, player gets less money (inverse the discount)
        if not is_buying:
            total_discount = -total_discount * 0.5  # Selling is always worse
        
        # Clamp discount between -80% and +80%
        total_discount = max(-0.8, min(0.8, total_discount))
        
        # Calculate final price
        final_price = base_price_cp * (1 - total_discount) * quantity
        final_price = int(final_price)
        
        return final_price, total_discount * 100
    
    def buy_item(
        self,
        item_id: str,
        quantity: int,
        player_gold_cp: int,
        npc_name: str = "Merchant",
        npc_relation: int = 0,
        player_charisma_mod: int = 0
    ) -> Dict:
        """
        Attempt to buy an item.
        
        Returns:
            Dictionary with transaction result and updated gold
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return {
                'success': False,
                'message': "Item not found.",
                'player_gold_after': player_gold_cp
            }
        
        # Calculate price
        total_cost, discount = self.calculate_price(
            item_id, quantity, npc_relation, player_charisma_mod, is_buying=True
        )
        
        # Check if player can afford it
        if player_gold_cp < total_cost:
            return {
                'success': False,
                'message': f"Not enough gold! Need {self.format_currency(total_cost)}, have {self.format_currency(player_gold_cp)}.",
                'player_gold_after': player_gold_cp,
                'required_gold': total_cost,
                'discount_percentage': discount
            }
        
        # Process transaction
        new_gold = player_gold_cp - total_cost
        
        # Log transaction
        self._log_transaction(
            transaction_type='BUY',
            item_id=item_id,
            item_name=item['item_name'],
            quantity=quantity,
            unit_price=total_cost // quantity,
            total_cost=total_cost,
            npc_name=npc_name,
            player_gold_before=player_gold_cp,
            player_gold_after=new_gold
        )
        
        return {
            'success': True,
            'message': f"Purchased {quantity}x {item['item_name']} for {self.format_currency(total_cost)} ({discount:+.1f}% discount).",
            'item_id': item_id,
            'item_name': item['item_name'],
            'quantity': quantity,
            'total_cost': total_cost,
            'discount_percentage': discount,
            'player_gold_before': player_gold_cp,
            'player_gold_after': new_gold
        }
    
    def sell_item(
        self,
        item_id: str,
        quantity: int,
        player_gold_cp: int,
        npc_name: str = "Merchant",
        npc_relation: int = 0,
        player_charisma_mod: int = 0
    ) -> Dict:
        """
        Sell an item to NPC.
        
        Returns:
            Dictionary with transaction result and updated gold
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return {
                'success': False,
                'message': "Item not found.",
                'player_gold_after': player_gold_cp
            }
        
        # Calculate sell price (usually lower than buy price)
        total_value, discount = self.calculate_price(
            item_id, quantity, npc_relation, player_charisma_mod, is_buying=False
        )
        
        # Process transaction
        new_gold = player_gold_cp + total_value
        
        # Log transaction
        self._log_transaction(
            transaction_type='SELL',
            item_id=item_id,
            item_name=item['item_name'],
            quantity=quantity,
            unit_price=total_value // quantity,
            total_cost=total_value,
            npc_name=npc_name,
            player_gold_before=player_gold_cp,
            player_gold_after=new_gold
        )
        
        return {
            'success': True,
            'message': f"Sold {quantity}x {item['item_name']} for {self.format_currency(total_value)} ({discount:+.1f}% modifier).",
            'item_id': item_id,
            'item_name': item['item_name'],
            'quantity': quantity,
            'total_value': total_value,
            'discount_percentage': discount,
            'player_gold_before': player_gold_cp,
            'player_gold_after': new_gold
        }
    
    def _log_transaction(
        self,
        transaction_type: str,
        item_id: str,
        item_name: str,
        quantity: int,
        unit_price: int,
        total_cost: int,
        npc_name: str,
        player_gold_before: int,
        player_gold_after: int
    ):
        """Internal method to log transactions for data visualization."""
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'transaction_type': transaction_type,
            'item_id': item_id,
            'item_name': item_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_cost': total_cost,
            'npc_name': npc_name,
            'player_gold_before': player_gold_before,
            'player_gold_after': player_gold_after
        }
        
        # Add to history
        self.trade_history.append(transaction)
        
        # Update DataFrame
        new_row = pd.DataFrame([transaction])
        self.trade_history_df = pd.concat([self.trade_history_df, new_row], ignore_index=True)
        
        # Save to CSV
        self.trade_history_df.to_csv(self.trade_log_path, index=False)
    
    def get_trade_summary(self) -> Dict:
        """Get summary statistics of all trades."""
        if self.trade_history_df.empty:
            return {
                'total_transactions': 0,
                'total_spent': 0,
                'total_earned': 0,
                'net_change': 0,
                'most_bought_item': None,
                'most_sold_item': None,
                'favorite_merchant': None
            }
        
        buys = self.trade_history_df[self.trade_history_df['transaction_type'] == 'BUY']
        sells = self.trade_history_df[self.trade_history_df['transaction_type'] == 'SELL']
        
        total_spent = buys['total_cost'].sum() if not buys.empty else 0
        total_earned = sells['total_cost'].sum() if not sells.empty else 0
        
        return {
            'total_transactions': len(self.trade_history_df),
            'total_bought': len(buys),
            'total_sold': len(sells),
            'total_spent': total_spent,
            'total_earned': total_earned,
            'net_change': total_earned - total_spent,
            'most_bought_item': buys['item_name'].mode()[0] if not buys.empty else None,
            'most_sold_item': sells['item_name'].mode()[0] if not sells.empty else None,
            'favorite_merchant': self.trade_history_df['npc_name'].mode()[0] if not self.trade_history_df.empty else None
        }
    
    def get_merchant_inventory(self, npc_id: str) -> List[Dict]:
        """
        Get items available from a specific merchant.
        
        Args:
            npc_id: Unique ID of the merchant NPC
            
        Returns:
            List of items with details
        """
        merchant_items = self.merchant_inventory_df[
            self.merchant_inventory_df['npc_id'] == npc_id
        ]
        
        inventory = []
        for _, row in merchant_items.iterrows():
            item = self.get_item_by_id(row['item_id'])
            if item:
                inventory.append({
                    'item_id': row['item_id'],
                    'item_name': item['item_name'],
                    'quantity': row['quantity'],
                    'base_price': item['cost'],
                    'price_modifier': row['price_modifier'],
                    'always_stock': row['always_stock']
                })
        
        return inventory
    
    def update_merchant_inventory(self, npc_id: str, item_id: str, quantity_change: int):
        """
        Update merchant's inventory after a trade.
        
        Args:
            npc_id: Unique ID of the merchant NPC
            item_id: Item being traded
            quantity_change: Negative for items sold to player, positive for items bought from player
        """
        # Find the merchant's item entry
        mask = (self.merchant_inventory_df['npc_id'] == npc_id) & \
               (self.merchant_inventory_df['item_id'] == item_id)
        
        if mask.any():
            # Update existing entry
            idx = self.merchant_inventory_df[mask].index[0]
            current_qty = self.merchant_inventory_df.at[idx, 'quantity']
            new_qty = max(0, current_qty + quantity_change)
            self.merchant_inventory_df.at[idx, 'quantity'] = new_qty
        else:
            # Add new entry if merchant doesn't have this item
            if quantity_change > 0:  # Only add if player is selling to merchant
                new_row = pd.DataFrame([{
                    'npc_id': npc_id,
                    'npc_name': self.merchant_inventory_df[
                        self.merchant_inventory_df['npc_id'] == npc_id
                    ]['npc_name'].iloc[0] if not self.merchant_inventory_df[
                        self.merchant_inventory_df['npc_id'] == npc_id
                    ].empty else 'Unknown',
                    'item_id': item_id,
                    'quantity': quantity_change,
                    'price_modifier': 1.0,
                    'always_stock': False
                }])
                self.merchant_inventory_df = pd.concat([self.merchant_inventory_df, new_row], ignore_index=True)
        
        # Save to CSV
        self.merchant_inventory_df.to_csv(self.merchant_inventory_path, sep='|', index=False)
    
    def check_merchant_has_item(self, npc_id: str, item_id: str, quantity: int) -> bool:
        """
        Check if merchant has enough of an item in stock.
        
        Args:
            npc_id: Unique ID of the merchant NPC
            item_id: Item to check
            quantity: Required quantity
            
        Returns:
            True if merchant has enough stock
        """
        mask = (self.merchant_inventory_df['npc_id'] == npc_id) & \
               (self.merchant_inventory_df['item_id'] == item_id)
        
        if not mask.any():
            return False
        
        merchant_qty = self.merchant_inventory_df[mask]['quantity'].iloc[0]
        always_stock = self.merchant_inventory_df[mask]['always_stock'].iloc[0]
        
        # If always_stock is true, merchant has unlimited supply
        return always_stock or merchant_qty >= quantity