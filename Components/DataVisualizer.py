"""
Data Visualizer - Creates matplotlib graphs for game statistics
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
from datetime import datetime
from typing import Optional


class DataVisualizer:
    """Creates beautiful graphs for trade and relationship data."""
    
    # Theme colors matching your game
    THEME = {
        'bg_dark': '#2b2b2b',
        'bg_medium': '#3d3d3d',
        'border': '#8b7355',
        'text': '#e8e0d5',
        'accent': '#731010',
        'positive': '#4a7c59',
        'negative': '#8b1a1a',
        'neutral': '#8b7355'
    }
    
    def __init__(self, parent_window: Optional[tk.Tk] = None):
        """
        Initialize the visualizer.
        
        Args:
            parent_window: Parent Tkinter window (optional)
        """
        self.parent = parent_window
        self._setup_matplotlib_style()
    
    def _setup_matplotlib_style(self):
        """Configure matplotlib to match game aesthetic."""
        plt.style.use('dark_background')
        plt.rcParams.update({
            'figure.facecolor': self.THEME['bg_dark'],
            'axes.facecolor': self.THEME['bg_medium'],
            'axes.edgecolor': self.THEME['border'],
            'axes.labelcolor': self.THEME['text'],
            'text.color': self.THEME['text'],
            'xtick.color': self.THEME['text'],
            'ytick.color': self.THEME['text'],
            'grid.color': self.THEME['border'],
            'grid.alpha': 0.3,
            'font.family': 'serif',
            'font.size': 10
        })
    
    def create_graph_window(self, title: str, width: int = 900, height: int = 600):
        """Create a themed window for displaying graphs."""
        window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        window.title(title)
        window.configure(bg=self.THEME['bg_dark'])
        window.geometry(f"{width}x{height}")
        
        # Center window
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
        
        return window
    
    # ==================== GOLD TRACKING ====================
    
    def plot_gold_over_time(self, trade_history_df: pd.DataFrame, show: bool = True):
        """
        Plot player gold balance over time.
        
        Args:
            trade_history_df: DataFrame from TradeSystem
            show: Whether to display in new window
        """
        if trade_history_df.empty:
            print("No trade data to visualize.")
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Convert timestamp to datetime
        trade_history_df['timestamp'] = pd.to_datetime(trade_history_df['timestamp'])
        
        # Plot gold after each transaction
        ax.plot(
            trade_history_df['timestamp'],
            trade_history_df['player_gold_after'],
            color=self.THEME['accent'],
            linewidth=2,
            marker='o',
            markersize=4,
            label='Gold Balance'
        )
        
        # Fill area under curve
        ax.fill_between(
            trade_history_df['timestamp'],
            trade_history_df['player_gold_after'],
            alpha=0.3,
            color=self.THEME['accent']
        )
        
        # Formatting
        ax.set_title('Gold Balance Over Time', fontsize=16, color=self.THEME['border'], pad=20)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Gold (cp)', fontsize=12)
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        if show:
            window = self.create_graph_window("Gold Over Time")
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig
    
    # ==================== TRADE ANALYSIS ====================
    
    def plot_trade_summary(self, trade_history_df: pd.DataFrame, show: bool = True):
        """
        Create a summary visualization of all trades.
        
        Args:
            trade_history_df: DataFrame from TradeSystem
            show: Whether to display in new window
        """
        if trade_history_df.empty:
            print("No trade data to visualize.")
            return None
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Trade Analysis Dashboard', fontsize=18, color=self.THEME['border'])
        
        # 1. Buy vs Sell Count
        transaction_counts = trade_history_df['transaction_type'].value_counts()
        ax1.bar(
            transaction_counts.index,
            transaction_counts.values,
            color=[self.THEME['negative'], self.THEME['positive']],
            edgecolor=self.THEME['border'],
            linewidth=2
        )
        ax1.set_title('Transactions: Buy vs Sell', fontsize=12)
        ax1.set_ylabel('Count')
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Gold Spent vs Earned
        buys = trade_history_df[trade_history_df['transaction_type'] == 'BUY']
        sells = trade_history_df[trade_history_df['transaction_type'] == 'SELL']
        
        gold_summary = [
            buys['total_cost'].sum() if not buys.empty else 0,
            sells['total_cost'].sum() if not sells.empty else 0
        ]
        
        ax2.bar(
            ['Spent', 'Earned'],
            gold_summary,
            color=[self.THEME['negative'], self.THEME['positive']],
            edgecolor=self.THEME['border'],
            linewidth=2
        )
        ax2.set_title('Gold Spent vs Earned', fontsize=12)
        ax2.set_ylabel('Gold (cp)')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(gold_summary):
            ax2.text(i, v + max(gold_summary) * 0.02, str(int(v)), 
                    ha='center', va='bottom', fontsize=10)
        
        # 3. Most Traded Items
        item_counts = trade_history_df['item_name'].value_counts().head(5)
        ax3.barh(
            item_counts.index,
            item_counts.values,
            color=self.THEME['accent'],
            edgecolor=self.THEME['border'],
            linewidth=2
        )
        ax3.set_title('Top 5 Most Traded Items', fontsize=12)
        ax3.set_xlabel('Transactions')
        ax3.grid(axis='x', alpha=0.3)
        
        # 4. Trading Partners
        npc_counts = trade_history_df['npc_name'].value_counts().head(5)
        ax4.barh(
            npc_counts.index,
            npc_counts.values,
            color=self.THEME['neutral'],
            edgecolor=self.THEME['border'],
            linewidth=2
        )
        ax4.set_title('Top 5 Trading Partners', fontsize=12)
        ax4.set_xlabel('Transactions')
        ax4.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if show:
            window = self.create_graph_window("Trade Summary", 1000, 700)
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig
    
    # ==================== RELATIONSHIP TRACKING ====================
    
    def plot_relationship_timeline(
        self, 
        relationship_history_df: pd.DataFrame,
        npc_id: Optional[str] = None,
        show: bool = True
    ):
        """
        Plot relationship changes over time.
        
        Args:
            relationship_history_df: DataFrame from RelationshipSystem
            npc_id: Optional - show only specific NPC's timeline
            show: Whether to display in new window
        """
        if relationship_history_df.empty:
            print("No relationship data to visualize.")
            return None
        
        # Filter by NPC if specified
        if npc_id:
            data = relationship_history_df[relationship_history_df['npc_id'] == npc_id].copy()
            title = f"Relationship Timeline: {data.iloc[0]['npc_name']}"
        else:
            data = relationship_history_df.copy()
            title = "All Relationships Over Time"
        
        if data.empty:
            print(f"No data for NPC: {npc_id}")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convert timestamp
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Plot each NPC's relationship line
        if npc_id:
            # Single NPC - detailed view
            ax.plot(
                data['timestamp'],
                data['relation_after'],
                color=self.THEME['accent'],
                linewidth=2.5,
                marker='o',
                markersize=6,
                label=data.iloc[0]['npc_name']
            )
            
            # Mark positive and negative changes differently
            positive = data[data['impression_change'] > 0]
            negative = data[data['impression_change'] < 0]
            
            ax.scatter(
                positive['timestamp'],
                positive['relation_after'],
                color=self.THEME['positive'],
                s=100,
                marker='^',
                label='Positive',
                zorder=5
            )
            
            ax.scatter(
                negative['timestamp'],
                negative['relation_after'],
                color=self.THEME['negative'],
                s=100,
                marker='v',
                label='Negative',
                zorder=5
            )
        else:
            # Multiple NPCs - overview
            for npc in data['npc_id'].unique():
                npc_data = data[data['npc_id'] == npc]
                ax.plot(
                    npc_data['timestamp'],
                    npc_data['relation_after'],
                    linewidth=2,
                    marker='o',
                    markersize=4,
                    label=npc_data.iloc[0]['npc_name'],
                    alpha=0.8
                )
        
        # Add horizontal lines for relationship tiers
        ax.axhline(y=0, color=self.THEME['text'], linestyle='--', alpha=0.3, label='Neutral')
        ax.axhline(y=5, color=self.THEME['positive'], linestyle='--', alpha=0.2)
        ax.axhline(y=-5, color=self.THEME['negative'], linestyle='--', alpha=0.2)
        
        # Formatting
        ax.set_title(title, fontsize=16, color=self.THEME['border'], pad=20)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Relationship Score', fontsize=12)
        ax.set_ylim(-11, 11)
        ax.legend(loc='best', framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if show:
            window = self.create_graph_window(title, 1000, 600)
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig
    
    def plot_relationship_distribution(
        self,
        relationships_dict: dict,
        characters_df: pd.DataFrame,
        show: bool = True
    ):
        """
        Show distribution of relationship tiers.
        
        Args:
            relationships_dict: Dictionary of {npc_id: relation_score}
            characters_df: Character DataFrame for names
            show: Whether to display in new window
        """
        if not relationships_dict:
            print("No relationship data to visualize.")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Count relationships by tier
        tiers = {
            'Mortal Enemy': 0, 'Hated': 0, 'Enemy': 0, 'Hostile': 0,
            'Unfriendly': 0, 'Neutral': 0, 'Acquaintance': 0,
            'Friendly': 0, 'Friend': 0, 'Trusted Friend': 0, 'Devoted': 0
        }
        
        from Components.RelationshipSystem import RelationshipSystem
        temp_system = RelationshipSystem.__new__(RelationshipSystem)
        
        for relation in relationships_dict.values():
            tier = temp_system.get_relation_tier(relation)
            tiers[tier] = tiers.get(tier, 0) + 1
        
        # Remove empty tiers
        tiers = {k: v for k, v in tiers.items() if v > 0}
        
        # 1. Bar chart of tiers
        colors = []
        for tier in tiers.keys():
            if 'Enemy' in tier or tier == 'Hated' or tier == 'Hostile':
                colors.append(self.THEME['negative'])
            elif tier == 'Neutral' or tier == 'Unfriendly':
                colors.append(self.THEME['neutral'])
            else:
                colors.append(self.THEME['positive'])
        
        ax1.barh(
            list(tiers.keys()),
            list(tiers.values()),
            color=colors,
            edgecolor=self.THEME['border'],
            linewidth=2
        )
        ax1.set_title('Relationship Distribution', fontsize=14, pad=15)
        ax1.set_xlabel('Number of NPCs')
        ax1.grid(axis='x', alpha=0.3)
        
        # 2. Pie chart of positive/neutral/negative
        sentiment_counts = {
            'Positive': sum(1 for r in relationships_dict.values() if r >= 3),
            'Neutral': sum(1 for r in relationships_dict.values() if -2 <= r < 3),
            'Negative': sum(1 for r in relationships_dict.values() if r < -2)
        }
        
        sentiment_counts = {k: v for k, v in sentiment_counts.items() if v > 0}
        
        ax2.pie(
            sentiment_counts.values(),
            labels=sentiment_counts.keys(),
            colors=[self.THEME['positive'], self.THEME['neutral'], self.THEME['negative']],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 12}
        )
        ax2.set_title('Relationship Sentiment', fontsize=14, pad=15)
        
        plt.tight_layout()
        
        if show:
            window = self.create_graph_window("Relationship Analysis", 1000, 500)
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig
    
    # ==================== COMBINED DASHBOARD ====================
    
    def create_full_dashboard(
        self,
        trade_history_df: pd.DataFrame,
        relationship_history_df: pd.DataFrame,
        show: bool = True
    ):
        """
        Create a comprehensive dashboard with all statistics.
        
        Args:
            trade_history_df: Trade data
            relationship_history_df: Relationship data
            show: Whether to display
        """
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle('Fog-Shrouded Chronicles - Player Dashboard', 
                     fontsize=20, color=self.THEME['border'], y=0.98)
        
        # Create grid layout
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Top row - Gold tracking
        ax1 = fig.add_subplot(gs[0, :])
        if not trade_history_df.empty:
            trade_history_df['timestamp'] = pd.to_datetime(trade_history_df['timestamp'])
            ax1.plot(trade_history_df['timestamp'], trade_history_df['player_gold_after'],
                    color=self.THEME['accent'], linewidth=2, marker='o', markersize=3)
            ax1.fill_between(trade_history_df['timestamp'], trade_history_df['player_gold_after'],
                            alpha=0.3, color=self.THEME['accent'])
            ax1.set_title('Gold Balance', fontsize=12)
            ax1.grid(True, alpha=0.3)
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Middle left - Trade summary
        ax2 = fig.add_subplot(gs[1, 0])
        if not trade_history_df.empty:
            transaction_counts = trade_history_df['transaction_type'].value_counts()
            ax2.bar(transaction_counts.index, transaction_counts.values,
                   color=[self.THEME['negative'], self.THEME['positive']],
                   edgecolor=self.THEME['border'], linewidth=2)
            ax2.set_title('Buy vs Sell', fontsize=11)
            ax2.grid(axis='y', alpha=0.3)
        
        # Middle center - Top items
        ax3 = fig.add_subplot(gs[1, 1])
        if not trade_history_df.empty:
            top_items = trade_history_df['item_name'].value_counts().head(5)
            ax3.barh(top_items.index, top_items.values,
                    color=self.THEME['accent'], edgecolor=self.THEME['border'], linewidth=2)
            ax3.set_title('Top Traded Items', fontsize=11)
            ax3.grid(axis='x', alpha=0.3)
        
        # Middle right - Relationship sentiment
        ax4 = fig.add_subplot(gs[1, 2])
        if not relationship_history_df.empty:
            # Get latest relations
            latest_relations = relationship_history_df.groupby('npc_id')['relation_after'].last()
            sentiment = {
                'Positive': sum(1 for r in latest_relations if r >= 3),
                'Neutral': sum(1 for r in latest_relations if -2 <= r < 3),
                'Negative': sum(1 for r in latest_relations if r < -2)
            }
            sentiment = {k: v for k, v in sentiment.items() if v > 0}
            ax4.pie(sentiment.values(), labels=sentiment.keys(),
                   colors=[self.THEME['positive'], self.THEME['neutral'], self.THEME['negative']],
                   autopct='%1.0f%%', textprops={'fontsize': 9})
            ax4.set_title('Relationships', fontsize=11)
        
        # Bottom row - Relationship timeline
        ax5 = fig.add_subplot(gs[2, :])
        if not relationship_history_df.empty:
            relationship_history_df['timestamp'] = pd.to_datetime(relationship_history_df['timestamp'])
            for npc in relationship_history_df['npc_id'].unique()[:5]:  # Show top 5
                npc_data = relationship_history_df[relationship_history_df['npc_id'] == npc]
                ax5.plot(npc_data['timestamp'], npc_data['relation_after'],
                        linewidth=1.5, marker='o', markersize=3,
                        label=npc_data.iloc[0]['npc_name'], alpha=0.8)
            ax5.axhline(y=0, color=self.THEME['text'], linestyle='--', alpha=0.3)
            ax5.set_title('Relationship Changes (Top 5)', fontsize=12)
            ax5.legend(loc='best', fontsize=8, framealpha=0.9)
            ax5.grid(True, alpha=0.3)
            ax5.set_ylim(-11, 11)
            plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        if show:
            window = self.create_graph_window("Player Dashboard", 1200, 800)
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return fig