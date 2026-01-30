
import matplotlib
# Use Agg backend for non-interactive saving (headless env)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from typing import Dict, Any

def save_plot(filename: str, output_dir: str):
    """Helper to save and clear plot."""
    path = os.path.join(output_dir, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def plot_jaw_distribution(stats: Dict, output_dir: str):
    data = stats.get("jaw_dist", {})
    if not data: return
    
    labels = list(data.keys())
    values = list(data.values())
    
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=['#3498db', '#e74c3c', '#9b59b6'])
    plt.title("Yaw Distribution")
    plt.xlabel("Jaw Type")
    plt.ylabel("Count")
    save_plot("jaw_distribution.png", output_dir)

def plot_teeth_histogram(stats: Dict, output_dir: str):
    data = stats.get("hist_teeth_per_case", {})
    if not data: return
    
    order = ["1_unit", "2_5_units", "6_9_units", "10_plus_units"]
    labels = [k for k in order if k in data]
    values = [data[k] for k in labels]
    
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color='#2ecc71')
    plt.title("Teeth Per Case (Complexity)")
    plt.xlabel("Case Size")
    plt.ylabel("Count")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    save_plot("teeth_per_case.png", output_dir)

def plot_tooth_frequency(stats: Dict, output_dir: str):
    data = stats.get("crown_counts", {})
    if not data: return
    
    teeth_data = {k: v for k, v in data.items() if isinstance(k, int)}
    sorted_keys = sorted(teeth_data.keys())
    values = [teeth_data[k] for k in sorted_keys]
    str_keys = [str(k) for k in sorted_keys]
    
    plt.figure(figsize=(12, 5))
    plt.bar(str_keys, values, color='#f1c40f', edgecolor='black')
    plt.title("Tooth Frequency Heatmap")
    plt.xlabel("Tooth ISO Number")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    save_plot("tooth_frequency.png", output_dir)

def plot_reconstruction_types(stats: Dict, output_dir: str):
    data = stats.get("reconstruction_stats", {})
    if not data: return
    
    labels = list(data.keys())
    values = list(data.values())
    
    plt.figure(figsize=(7, 7))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#34495e', '#ecf0f1', '#95a5a6'])
    plt.title("Reconstruction Types (Tooth Level)")
    save_plot("reconstruction_types.png", output_dir)

def plot_clinical_case_types(stats: Dict, output_dir: str):
    data = stats.get("clinical_types", {})
    if not data: return
    
    labels = [k for k, v in data.items() if v > 0]
    values = [v for k, v in data.items() if v > 0]
    
    if not values: return

    plt.figure(figsize=(7, 7))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#e67e22', '#27ae60', '#f39c12', '#7f8c8d'])
    plt.title("Clinical Case Types (Case Level)")
    save_plot("clinical_case_types.png", output_dir)

def generate_plots(stats: Dict, output_dir: str):
    """Generates all standard plots for the report."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    plot_jaw_distribution(stats, output_dir)
    plot_teeth_histogram(stats, output_dir)
    plot_tooth_frequency(stats, output_dir)
    plot_reconstruction_types(stats, output_dir)
    plot_clinical_case_types(stats, output_dir)
