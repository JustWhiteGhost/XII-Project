"""
Session Analytics - Track player progress in real-time
Demonstrates Pandas time-series analysis and live Matplotlib updates
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
from pathlib import Path


class SessionTracker:
    """
    Tracks player actions, decisions, and progress during gameplay
    Showcases Pandas DataFrame operations and time-series analysis
    """
    
    def __init__(self, save_dir='saves/sessions'):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize tracking DataFrames
        self.actions_df = pd.DataFrame(columns=[
            'timestamp', 'turn', 'action_type', 'target', 'success', 
            'gold_change', 'hp_change', 'location'
        ])
        
        self.conversations_df = pd.DataFrame(columns=[
            'timestamp', 'npc_name', 'npc_id', 'impression_change', 
            'total_impression', 'duration_minutes'
        ])
        
        self.inventory_df = pd.DataFrame(columns=[
            'timestamp', 'action', 'item', 'quantity', 'total_value'
        ])
        
        self.session_start = datetime.now()
        self.current_turn = 0
        self.current_location = None
        
    def log_action(self, action_type, target=None, success=True, 
                   gold_change=0, hp_change=0, location=None):
        """
        Log a player action (Pandas DataFrame append)
        
        Args:
            action_type: 'talk', 'fight', 'trade', 'explore', etc.
            target: NPC name or object
            success: Whether action succeeded
            gold_change: Gold gained/lost
            hp_change: HP gained/lost
            location: Current location ID
        """
        new_row = pd.DataFrame([{
            'timestamp': datetime.now(),
            'turn': self.current_turn,
            'action_type': action_type,
            'target': target,
            'success': success,
            'gold_change': gold_change,
            'hp_change': hp_change,
            'location': location or self.current_location
        }])
        
        self.actions_df = pd.concat([self.actions_df, new_row], ignore_index=True)
        self.current_turn += 1
    
    def log_conversation(self, npc_name, npc_id, impression_change, total_impression):
        """Log NPC conversation"""
        # Calculate duration
        if len(self.conversations_df) > 0:
            last_conv = self.conversations_df.iloc[-1]['timestamp']
            duration = (datetime.now() - last_conv).total_seconds() / 60
        else:
            duration = 0
        
        new_row = pd.DataFrame([{
            'timestamp': datetime.now(),
            'npc_name': npc_name,
            'npc_id': npc_id,
            'impression_change': impression_change,
            'total_impression': total_impression,
            'duration_minutes': duration
        }])
        
        self.conversations_df = pd.concat([self.conversations_df, new_row], ignore_index=True)
    
    def log_inventory_change(self, action, item, quantity, total_value):
        """Log inventory changes"""
        new_row = pd.DataFrame([{
            'timestamp': datetime.now(),
            'action': action,  # 'bought', 'sold', 'found', 'used'
            'item': item,
            'quantity': quantity,
            'total_value': total_value
        }])
        
        self.inventory_df = pd.concat([self.inventory_df, new_row], ignore_index=True)
    
    # ==================== PANDAS ANALYSIS METHODS ====================
    
    def get_action_summary(self):
        """Summarize actions taken (Pandas groupby)"""
        if len(self.actions_df) == 0:
            return pd.DataFrame()
        
        summary = self.actions_df.groupby('action_type').agg({
            'success': ['count', 'sum', 'mean'],
            'gold_change': 'sum',
            'hp_change': 'sum'
        }).round(2)
        
        summary.columns = ['Total', 'Successful', 'Success_Rate', 'Gold_Change', 'HP_Change']
        return summary
    
    def get_conversation_stats(self):
        """Analyze conversation patterns"""
        if len(self.conversations_df) == 0:
            return pd.DataFrame()
        
        stats = self.conversations_df.groupby('npc_name').agg({
            'impression_change': ['sum', 'mean', 'count'],
            'total_impression': 'last',
            'duration_minutes': 'sum'
        }).round(2)
        
        stats.columns = ['Total_Impression_Change', 'Avg_Change', 'Interactions', 
                        'Final_Impression', 'Total_Time_Minutes']
        return stats.sort_values('Final_Impression', ascending=False)
    
    def get_gold_timeline(self):
        """Get cumulative gold over time (Pandas cumsum)"""
        if len(self.actions_df) == 0:
            return pd.Series()
        
        timeline = self.actions_df.set_index('timestamp')['gold_change'].cumsum()
        return timeline
    
    def get_hp_timeline(self):
        """Get HP changes over time"""
        if len(self.actions_df) == 0:
            return pd.Series()
        
        timeline = self.actions_df.set_index('timestamp')['hp_change'].cumsum()
        return timeline
    
    def get_most_visited_locations(self):
        """Analyze location visit frequency"""
        if len(self.actions_df) == 0:
            return pd.Series()
        
        return self.actions_df['location'].value_counts()
    
    def get_inventory_value_timeline(self):
        """Track total inventory value over time"""
        if len(self.inventory_df) == 0:
            return pd.Series()
        
        self.inventory_df['cumulative_value'] = self.inventory_df['total_value'].cumsum()
        return self.inventory_df.set_index('timestamp')['cumulative_value']
    
    def export_session_report(self, filename=None):
        """Export session data to Excel (Pandas to_excel)"""
        if filename is None:
            filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = self.save_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Write each DataFrame to separate sheet
            self.actions_df.to_excel(writer, sheet_name='Actions', index=False)
            self.conversations_df.to_excel(writer, sheet_name='Conversations', index=False)
            self.inventory_df.to_excel(writer, sheet_name='Inventory', index=False)
            
            # Summary sheets
            self.get_action_summary().to_excel(writer, sheet_name='Action_Summary')
            self.get_conversation_stats().to_excel(writer, sheet_name='NPC_Relationships')
        
        print(f"Session report exported to: {filepath}")
        return filepath
    
    def save_session_json(self, filename=None):
        """Save session as JSON for later analysis"""
        if filename is None:
            filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.save_dir / filename
        
        session_data = {
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'total_turns': self.current_turn,
            'actions': self.actions_df.to_dict('records'),
            'conversations': self.conversations_df.to_dict('records'),
            'inventory': self.inventory_df.to_dict('records')
        }
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        return filepath


class SessionDashboard(tk.Toplevel):
    """
    Live dashboard showing session progress with auto-updating charts
    """
    
    def __init__(self, parent, tracker):
        super().__init__(parent)
        self.tracker = tracker
        
        self.title("Live Session Analytics")
        self.geometry("1000x700")
        self.configure(bg='#2b2b2b')
        
        # Create notebook
        self.notebook = tk.ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_progress_tab()
        self.create_relationships_tab()
        self.create_summary_tab()
        
        # Auto-refresh every 5 seconds
        self.auto_refresh()
    
    def create_progress_tab(self):
        """Tab showing gold/HP timeline"""
        tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tab, text='Progress')
        
        # Create figure
        self.progress_fig, (self.gold_ax, self.hp_ax) = plt.subplots(2, 1, figsize=(10, 6))
        self.progress_fig.patch.set_facecolor('#1e1e1e')
        
        # Initial empty plots
        self.update_progress_charts()
        
        # Embed
        self.progress_canvas = FigureCanvasTkAgg(self.progress_fig, tab)
        self.progress_canvas.draw()
        self.progress_canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def update_progress_charts(self):
        """Update progress charts with latest data"""
        # Clear axes
        self.gold_ax.clear()
        self.hp_ax.clear()
        
        # Gold timeline
        gold_timeline = self.tracker.get_gold_timeline()
        if len(gold_timeline) > 0:
            # CRITICAL FIX: Convert to plain Python lists
            x_values = list(range(len(gold_timeline)))
            y_values = [float(v) for v in gold_timeline.values]  # Ensure float type
            
            # Plot line
            self.gold_ax.plot(x_values, y_values, 
                            color='#FFD700', linewidth=2, marker='o', markersize=4)
            
            # Fill with explicit y1=0 baseline
            try:
                self.gold_ax.fill_between(x_values, 0, y_values, 
                                         alpha=0.3, color='#FFD700')
            except Exception as e:
                # Skip fill if it fails - plot still works
                print(f"Fill_between skipped: {e}")
            
            self.gold_ax.set_xlabel('Turn', color='#e8e0d5')
        else:
            # Show empty state
            self.gold_ax.text(0.5, 0.5, 'No data yet - start playing!', 
                            ha='center', va='center', transform=self.gold_ax.transAxes,
                            color='#8b7355', fontsize=12)
        
        self.gold_ax.set_ylabel('Cumulative Gold', color='#e8e0d5')
        self.gold_ax.set_title('Gold Over Time', color='#8b7355', fontsize=12)
        self.gold_ax.set_facecolor('#2b2b2b')
        self.gold_ax.tick_params(colors='#e8e0d5')
        self.gold_ax.grid(True, alpha=0.2, color='#8b7355')
        self.gold_ax.spines['bottom'].set_color('#8b7355')
        self.gold_ax.spines['left'].set_color('#8b7355')
        self.gold_ax.spines['top'].set_visible(False)
        self.gold_ax.spines['right'].set_visible(False)
        
        # HP timeline
        hp_timeline = self.tracker.get_hp_timeline()
        if len(hp_timeline) > 0:
            # CRITICAL FIX: Convert to plain Python lists
            x_values = list(range(len(hp_timeline)))
            y_values = [float(v) for v in hp_timeline.values]  # Ensure float type
            
            self.hp_ax.plot(x_values, y_values, 
                          color='#FF6B6B', linewidth=2, marker='s', markersize=4)
            self.hp_ax.set_xlabel('Turn', color='#e8e0d5')
        else:
            self.hp_ax.text(0.5, 0.5, 'No data yet - start playing!', 
                          ha='center', va='center', transform=self.hp_ax.transAxes,
                          color='#8b7355', fontsize=12)
        
        self.hp_ax.axhline(y=0, color='#8b7355', linestyle='--', alpha=0.5)
        self.hp_ax.set_ylabel('HP Change', color='#e8e0d5')
        self.hp_ax.set_title('Health Changes', color='#8b7355', fontsize=12)
        self.hp_ax.set_facecolor('#2b2b2b')
        self.hp_ax.tick_params(colors='#e8e0d5')
        self.hp_ax.grid(True, alpha=0.2, color='#8b7355')
        self.hp_ax.spines['bottom'].set_color('#8b7355')
        self.hp_ax.spines['left'].set_color('#8b7355')
        self.hp_ax.spines['top'].set_visible(False)
        self.hp_ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
    
    def create_relationships_tab(self):
        """Tab showing NPC relationship chart"""
        tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tab, text='Relationships')
        
        self.rel_fig, self.rel_ax = plt.subplots(figsize=(10, 6))
        self.rel_fig.patch.set_facecolor('#1e1e1e')
        
        self.update_relationships_chart()
        
        self.rel_canvas = FigureCanvasTkAgg(self.rel_fig, tab)
        self.rel_canvas.draw()
        self.rel_canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def update_relationships_chart(self):
        """Update relationship visualization"""
        self.rel_ax.clear()
        
        conv_stats = self.tracker.get_conversation_stats()
        
        if len(conv_stats) > 0:
            npcs = conv_stats.index.tolist()
            impressions = conv_stats['Final_Impression'].values
            
            # Color code: positive = green, negative = red
            colors = ['#4ECDC4' if x > 0 else '#FF6B6B' for x in impressions]
            
            self.rel_ax.barh(range(len(npcs)), impressions, color=colors, edgecolor='#8b7355')
            self.rel_ax.set_yticks(range(len(npcs)))
            self.rel_ax.set_yticklabels(npcs, color='#e8e0d5')
            self.rel_ax.set_xlabel('Impression Score', color='#e8e0d5')
            self.rel_ax.set_title('NPC Relationships', color='#8b7355', fontsize=12)
            self.rel_ax.axvline(x=0, color='#8b7355', linestyle='--', alpha=0.5)
        
        self.rel_ax.set_facecolor('#2b2b2b')
        self.rel_ax.tick_params(colors='#e8e0d5')
        plt.tight_layout()
    
    def create_summary_tab(self):
        """Tab showing text summary"""
        tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tab, text='Summary')
        
        # Text widget for summary
        self.summary_text = tk.Text(tab, bg='#2b2b2b', fg='#e8e0d5', 
                                   font=('Courier', 10), wrap=tk.WORD)
        self.summary_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Export button
        export_btn = tk.Button(tab, text="Export Session Report", 
                              command=self.export_report,
                              bg='#731010', fg='#e8e0d5', font=('Georgia', 11, 'bold'))
        export_btn.pack(pady=10)
        
        self.update_summary()
    
    def update_summary(self):
        """Update text summary"""
        self.summary_text.delete(1.0, tk.END)
        
        summary_text = f"""
╔══════════════════════════════════════════════════════════╗
║              SESSION SUMMARY (Pandas Analysis)           ║
╚══════════════════════════════════════════════════════════╝

Session Duration: {(datetime.now() - self.tracker.session_start).total_seconds() / 60:.1f} minutes
Total Turns: {self.tracker.current_turn}

═══════════════════════════════════════════════════════════

ACTION SUMMARY:
{self.tracker.get_action_summary().to_string() if len(self.tracker.actions_df) > 0 else "No actions yet"}

═══════════════════════════════════════════════════════════

NPC RELATIONSHIPS:
{self.tracker.get_conversation_stats().to_string() if len(self.tracker.conversations_df) > 0 else "No conversations yet"}

═══════════════════════════════════════════════════════════

MOST VISITED LOCATIONS:
{self.tracker.get_most_visited_locations().to_string() if len(self.tracker.actions_df) > 0 else "No locations visited"}
"""
        
        self.summary_text.insert(1.0, summary_text)
    
    def auto_refresh(self):
        """Auto-refresh charts every 5 seconds"""
        self.update_progress_charts()
        self.progress_canvas.draw()
        
        self.update_relationships_chart()
        self.rel_canvas.draw()
        
        self.update_summary()
        
        # Schedule next refresh
        self.after(5000, self.auto_refresh)
    
    def export_report(self):
        """Export session report"""
        filepath = self.tracker.export_session_report()
        tk.messagebox.showinfo("Export Complete", f"Report saved to:\n{filepath}")


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Test the tracker
    tracker = SessionTracker()
    
    # Simulate some actions
    tracker.log_action('explore', location='10101', success=True, gold_change=50)
    tracker.log_action('talk', target='Emma Thorne', success=True)
    tracker.log_conversation('Emma Thorne', 'A1B2C3', impression_change=2, total_impression=2)
    tracker.log_action('fight', target='Goblin', success=True, gold_change=25, hp_change=-10)
    tracker.log_inventory_change('found', 'Health Potion', 1, 50)
    
    # Show dashboard
    root = tk.Tk()
    root.withdraw()
    
    dashboard = SessionDashboard(root, tracker)
    
    root.mainloop()