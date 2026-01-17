"""
Analytics Core Module - 2 Day Implementation
Demonstrates Pandas data analysis and Matplotlib visualization
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import numpy as np
from pathlib import Path


class RPGAnalytics:
    """
    Core analytics system for Fog-Shrouded Chronicles
    Showcases Pandas and Matplotlib capabilities
    """
    
    def __init__(self, character_csv, location_csv):
        """Initialize with CSV paths"""
        self.char_df = pd.read_csv(character_csv, sep='|')
        self.loc_df = pd.read_csv(location_csv, sep='|')
        
        # Clean data
        self.char_df['money'] = pd.to_numeric(self.char_df['money'], errors='coerce')
        self.char_df['age'] = pd.to_numeric(self.char_df['age'], errors='coerce')
        self.char_df['relation'] = pd.to_numeric(self.char_df['relation'], errors='coerce')
        
        print("Analytics initialized with:")
        print(f"  - {len(self.char_df)} characters")
        print(f"  - {len(self.loc_df)} locations")
    
    # ==================== PANDAS ANALYSIS METHODS ====================
    
    def get_profession_stats(self):
        """Analyze character professions (Pandas groupby)"""
        return self.char_df['profession'].value_counts()
    
    def get_mood_distribution(self):
        """Analyze mood distribution"""
        return self.char_df['mood'].value_counts()
    
    def get_wealth_by_profession(self):
        """Calculate average wealth by profession (Pandas groupby + agg)"""
        wealth_stats = self.char_df.groupby('profession')['money'].agg([
            ('count', 'count'),
            ('avg_wealth', 'mean'),
            ('total_wealth', 'sum'),
            ('max_wealth', 'max')
        ]).round(0)
        return wealth_stats.sort_values('avg_wealth', ascending=False)
    
    def get_location_npc_density(self):
        """Count NPCs per location (Pandas merge + groupby)"""
        npc_counts = self.char_df.groupby('location').size().reset_index(name='npc_count')
        location_density = self.loc_df.merge(
            npc_counts, 
            left_on='location_id', 
            right_on='location', 
            how='left'
        )
        location_density['npc_count'] = location_density['npc_count'].fillna(0)
        return location_density[['location_name', 'npc_count', 'danger_level']]
    
    def get_age_demographics(self):
        """Analyze age distribution with bins"""
        bins = [0, 25, 35, 50, 100]
        labels = ['Young (0-25)', 'Adult (26-35)', 'Middle-aged (36-50)', 'Elder (51+)']
        self.char_df['age_group'] = pd.cut(self.char_df['age'], bins=bins, labels=labels)
        return self.char_df['age_group'].value_counts().sort_index()
    
    def get_relationship_analysis(self):
        """Analyze relationship scores (Pandas statistics)"""
        stats = self.char_df['relation'].describe()
        return stats
    
    def get_mood_nature_crosstab(self):
        """Cross-tabulation of mood vs nature (Pandas crosstab)"""
        crosstab = pd.crosstab(
            self.char_df['mood'], 
            self.char_df['nature'],
            margins=True
        )
        return crosstab
    
    def get_location_danger_stats(self):
        """Analyze locations by danger level"""
        danger_stats = self.loc_df.groupby('danger_level').agg({
            'location_name': 'count',
            'crowd_density': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
        }).rename(columns={'location_name': 'location_count'})
        return danger_stats
    
    def get_wealthy_npcs(self, top_n=10):
        """Get top N wealthiest NPCs (Pandas sorting + filtering)"""
        wealthy = self.char_df.nlargest(top_n, 'money')[
            ['name', 'profession', 'money', 'location', 'mood']
        ]
        return wealthy
    
    def export_summary_report(self, filepath='analytics_report.csv'):
        """Export comprehensive report (Pandas to_csv)"""
        summary = pd.DataFrame({
            'Total_Characters': [len(self.char_df)],
            'Total_Locations': [len(self.loc_df)],
            'Total_Wealth': [self.char_df['money'].sum()],
            'Avg_Age': [self.char_df['age'].mean()],
            'Most_Common_Profession': [self.char_df['profession'].mode()[0]],
            'Most_Common_Mood': [self.char_df['mood'].mode()[0]]
        })
        summary.to_csv(filepath, index=False)
        print(f"Report exported to {filepath}")
        return summary


class AnalyticsViewer(tk.Toplevel):
    """
    Tkinter window to display analytics with Matplotlib charts
    """
    
    def __init__(self, parent, analytics):
        super().__init__(parent)
        self.analytics = analytics
        
        self.title("RPG Analytics Dashboard")
        self.geometry("1200x800")
        self.configure(bg='#2b2b2b')
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#2b2b2b')
        style.configure('TNotebook.Tab', background='#3d3d3d', foreground='#e8e0d5')
        
        # Create tabs
        self.create_profession_tab()
        self.create_wealth_tab()
        self.create_location_tab()
        self.create_demographics_tab()
    
    def create_profession_tab(self):
        """Tab 1: Profession Analysis"""
        tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tab, text='Professions')
        
        # Get data
        prof_counts = self.analytics.get_profession_stats()
        
        # Create matplotlib figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor('#1e1e1e')
        
        # Bar chart
        ax1.bar(range(len(prof_counts)), prof_counts.values, color='#731010', edgecolor='#8b7355')
        ax1.set_xticks(range(len(prof_counts)))
        ax1.set_xticklabels(prof_counts.index, rotation=45, ha='right', color='#e8e0d5')
        ax1.set_ylabel('Count', color='#e8e0d5')
        ax1.set_title('NPCs by Profession', color='#8b7355', fontsize=14)
        ax1.set_facecolor('#2b2b2b')
        ax1.tick_params(colors='#e8e0d5')
        ax1.spines['bottom'].set_color('#8b7355')
        ax1.spines['left'].set_color('#8b7355')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Pie chart
        colors = plt.cm.Oranges(np.linspace(0.4, 0.8, len(prof_counts)))
        ax2.pie(prof_counts.values, labels=prof_counts.index, autopct='%1.1f%%',
                colors=colors, textprops={'color': '#e8e0d5'})
        ax2.set_title('Profession Distribution', color='#8b7355', fontsize=14)
        ax2.set_facecolor('#2b2b2b')
        
        plt.tight_layout()
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_wealth_tab(self):
        """Tab 2: Wealth Analysis"""
        tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tab, text='Wealth')
        
        # Get data
        wealth_stats = self.analytics.get_wealth_by_profession()
        top_wealthy = self.analytics.get_wealthy_npcs(10)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor('#1e1e1e')
        
        # Average wealth by profession
        top_10_prof = wealth_stats.head(10)
        ax1.barh(range(len(top_10_prof)), top_10_prof['avg_wealth'], color='#731010', edgecolor='#8b7355')
        ax1.set_yticks(range(len(top_10_prof)))
        ax1.set_yticklabels(top_10_prof.index, color='#e8e0d5')
        ax1.set_xlabel('Average Wealth (Gold)', color='#e8e0d5')
        ax1.set_title('Top 10 Professions by Avg Wealth', color='#8b7355', fontsize=14)
        ax1.set_facecolor('#2b2b2b')
        ax1.tick_params(colors='#e8e0d5')
        ax1.spines['bottom'].set_color('#8b7355')
        ax1.spines['left'].set_color('#8b7355')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Top 10 wealthiest NPCs
        ax2.barh(range(len(top_wealthy)), top_wealthy['money'], color='#8b7355', edgecolor='#731010')
        ax2.set_yticks(range(len(top_wealthy)))
        ax2.set_yticklabels(top_wealthy['name'], color='#e8e0d5', fontsize=9)
        ax2.set_xlabel('Wealth (Gold)', color='#e8e0d5')
        ax2.set_title('Top 10 Wealthiest NPCs', color='#8b7355', fontsize=14)
        ax2.set_facecolor('#2b2b2b')
        ax2.tick_params(colors='#e8e0d5')
        ax2.spines['bottom'].set_color('#8b7355')
        ax2.spines['left'].set_color('#8b7355')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_location_tab(self):
        """Tab 3: Location Analysis"""
        tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tab, text='Locations')
        
        # Get data
        location_density = self.analytics.get_location_npc_density()
        danger_stats = self.analytics.get_location_danger_stats()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor('#1e1e1e')
        
        # NPC density scatter plot
        scatter = ax1.scatter(
            location_density['danger_level'],
            location_density['npc_count'],
            s=100,
            c=location_density['danger_level'],
            cmap='YlOrRd',
            edgecolors='#8b7355',
            alpha=0.7
        )
        ax1.set_xlabel('Danger Level', color='#e8e0d5')
        ax1.set_ylabel('NPC Count', color='#e8e0d5')
        ax1.set_title('NPC Density vs Danger Level', color='#8b7355', fontsize=14)
        ax1.set_facecolor('#2b2b2b')
        ax1.tick_params(colors='#e8e0d5')
        ax1.grid(True, alpha=0.2, color='#8b7355')
        ax1.spines['bottom'].set_color('#8b7355')
        ax1.spines['left'].set_color('#8b7355')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Locations by danger level
        ax2.bar(danger_stats.index, danger_stats['location_count'], color='#731010', edgecolor='#8b7355')
        ax2.set_xlabel('Danger Level', color='#e8e0d5')
        ax2.set_ylabel('Number of Locations', color='#e8e0d5')
        ax2.set_title('Locations by Danger Level', color='#8b7355', fontsize=14)
        ax2.set_facecolor('#2b2b2b')
        ax2.tick_params(colors='#e8e0d5')
        ax2.spines['bottom'].set_color('#8b7355')
        ax2.spines['left'].set_color('#8b7355')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def create_demographics_tab(self):
        """Tab 4: Demographics"""
        tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tab, text='Demographics')
        
        # Get data
        age_dist = self.analytics.get_age_demographics()
        mood_dist = self.analytics.get_mood_distribution()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor('#1e1e1e')
        
        # Age distribution
        colors_age = ['#731010', '#8b1a1a', '#a52a2a', '#c04040']
        ax1.pie(age_dist.values, labels=age_dist.index, autopct='%1.1f%%',
                colors=colors_age, textprops={'color': '#e8e0d5'})
        ax1.set_title('Age Distribution', color='#8b7355', fontsize=14)
        ax1.set_facecolor('#2b2b2b')
        
        # Mood distribution
        ax2.bar(range(len(mood_dist)), mood_dist.values, color='#8b7355', edgecolor='#731010')
        ax2.set_xticks(range(len(mood_dist)))
        ax2.set_xticklabels(mood_dist.index, rotation=45, ha='right', color='#e8e0d5')
        ax2.set_ylabel('Count', color='#e8e0d5')
        ax2.set_title('Mood Distribution', color='#8b7355', fontsize=14)
        ax2.set_facecolor('#2b2b2b')
        ax2.tick_params(colors='#e8e0d5')
        ax2.spines['bottom'].set_color('#8b7355')
        ax2.spines['left'].set_color('#8b7355')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

