#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import os
import sys


dot_size = 105
fig_size = (16, 18)

TITLE_SIZE = 22
LABEL_SIZE = 23
# TICK_SIZE = 20
TEXT_SIZE = 24
FONT_SIZE = 22

def calculate_ranks(df, columns_directions):
    """Calculates ranks for specified columns based on direction."""
    ranked_df = df.copy()
    for col, direction in columns_directions.items():
        ascending = True if direction == 'ascending' else False
        ranked_df[f'{col}_rank'] = df[col].rank(ascending=ascending, method='min')
    return ranked_df

def get_stats(x, y):
    """Calculates regression statistics."""
    if len(x) < 2:
        return np.nan, np.nan, np.nan, np.nan
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope, intercept, r_value**2, r_value

def apply_custom_style(ax, x_ticks_cfg=None, y_ticks_cfg=None):
    """Applies the specific styling requested by the user."""
    
    # 1. Apply customized ticks if provided
    if x_ticks_cfg:
        ax.set_xticks(x_ticks_cfg['major'])
        # Set tick labels with specific font properties
        ax.set_xticklabels([f"{t:.1f}" if isinstance(t, float) else str(int(t)) for t in x_ticks_cfg['major']], 
                           fontsize=FONT_SIZE, fontweight='bold')
        if x_ticks_cfg.get('minor') is not None:
            ax.set_xticks(x_ticks_cfg['minor'], minor=True)
            
    if y_ticks_cfg:
        ax.set_yticks(y_ticks_cfg['major'])
        # Set tick labels with specific font properties
        ax.set_yticklabels([f"{t:.1f}" if isinstance(t, float) else str(int(t)) for t in y_ticks_cfg['major']], 
                           fontsize=FONT_SIZE, fontweight='bold')
        if y_ticks_cfg.get('minor') is not None:
            ax.set_yticks(y_ticks_cfg['minor'], minor=True)

    # 2. General Tick Parameters (Length/Width)
    ax.tick_params(axis='both', which='major', length=7, width=1.8, labelsize=FONT_SIZE)
    ax.tick_params(axis='x', which='minor', length=5.5, width=1.6)
    ax.tick_params(axis='y', which='minor', length=5.5, width=1.6)
    
    # Ensure existing labels are bold (if not set by set_xticklabels above)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(FONT_SIZE)
        label.set_fontweight('bold')

    # 3. Customize Axis Spines
    for spine in ax.spines.values():
        spine.set_linewidth(1.7)

def plot_scatter_with_regression(ax, data, x_col, y_col, title_prefix, color, text_size, label_size, title_size, tick_size):
    x = data[x_col]
    y = data[y_col]
    
    if len(data) < 2:
        return

    slope, intercept, r_squared, pearson_r = get_stats(x, y)
    
    # Scatter Plot
    ax.scatter(x, y, alpha=0.8, edgecolors='w', s=dot_size, color=color)
    
    # Regression Line
    line_x = np.array([x.min(), x.max()])
    line_y = slope * line_x + intercept
    ax.plot(line_x, line_y, color='red', linewidth=2, linestyle='--')
    
    # Stats Annotation
    text_str = f'$\mathbf{{r = {pearson_r:.3f}}}$'
    ax.text(0.05, 0.96, text_str, transform=ax.transAxes, fontsize=TEXT_SIZE, edgecolor='none',
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Rank Annotations
    x_rank_col = f'{x_col}_rank'
    y_rank_col = f'{y_col}_rank'
    
    for idx, row in data.iterrows():
        label = f"({int(row[x_rank_col])},{int(row[y_rank_col])})"
        ax.annotate(label, (row[x_col], row[y_col]), 
                    xytext=(5, 5), textcoords='offset points', 
                    fontsize=9, alpha=0.8)

    # Labels and Title
    ax.set_xlabel(f"{x_col}", fontsize=label_size, fontweight='bold')
    ax.set_ylabel(y_col, fontsize=label_size, fontweight='bold')
    # ax.set_title(f'{title_prefix}: {y_col} vs {x_col}', fontsize=title_size, fontweight='bold')
    
    # Apply Style (No specific ticks for Top 20 as they are subsets)
    apply_custom_style(ax)

def generate_plots_and_stats(input_file):
    output_dir = os.path.dirname(os.path.abspath(input_file))
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Load data
    try:
        df = pd.read_csv(input_file)
        df = df.rename(columns={
            'pae_interaction': 'ipAE',
            'plddt_binder': 'pLDDT_peptide'
        })
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return

    # Configuration
    pairs_config = [
        ('ipTM', 'ipSAE', 'descending', 'descending'),           
        ('pTM_ipTM', 'ipSAE', 'descending', 'descending'),       
        ('ipAE', 'ipSAE', 'ascending', 'descending'),            
        ('pLDDT_peptide', 'ipSAE', 'descending', 'descending'),  
        ('pLDDT_peptide', 'pTM_ipTM', 'descending', 'descending'),
        ('pLDDT_peptide', 'ipTM', 'descending', 'descending')     
    ]
    
    # Axis Limits (Ranges)
    axis_limits = {
        'ipSAE': (-0.01, 0.85),
        'ipAE': (6, 30),
        'pLDDT_peptide': (25, 82),
        'ipTM': (0.25, 0.99),
        'pTM_ipTM': (0.25, 0.99)
    }

    # Axis Ticks (Major and Minor definitions based on ranges)
    axis_ticks = {
        'ipSAE': {'major': np.arange(0, 0.9, 0.2), 'minor': np.arange(0, 0.9, 0.1)},
        'ipAE': {'major': np.arange(6, 31, 6), 'minor': np.arange(6, 31, 3)},
        'pLDDT_peptide': {'major': np.arange(40, 81, 20), 'minor': np.arange(30, 81, 10)},
        'ipTM': {'major': np.arange(0.3, 1.1, 0.2), 'minor': np.arange(0.3, 1.1, 0.1)},
        'pTM_ipTM': {'major': np.arange(0.3, 1.1, 0.2), 'minor': np.arange(0.3, 1.1, 0.1)}
    }
    
    # Calculate ranks
    rank_cols = {}
    for y, x, y_dir, x_dir in pairs_config:
        rank_cols[y] = y_dir
        rank_cols[x] = x_dir
        
    df_ranked = calculate_ranks(df, rank_cols)
    stats_data = []

    
    # --- 1. All Data ---
    fig1, axes1 = plt.subplots(3, 2, figsize=fig_size)
    axes1 = axes1.flatten()
    for i, (y_col, x_col, y_dir, x_dir) in enumerate(pairs_config):
        ax = axes1[i]
        x = df[x_col]
        y = df[y_col]
        
        slope, intercept, r_squared, pearson_r = get_stats(x, y)
        stats_data.append({'Pair': f'{y_col} vs {x_col}', 'Scenario': 'All Data', 'R_squared': r_squared, 'Pearson_r': pearson_r})

        ax.scatter(x, y, alpha=0.6, edgecolors='w', s=dot_size, color='blue')
        line_x = np.array([x.min(), x.max()])
        ax.plot(line_x, slope * line_x + intercept, color='red', linewidth=2, linestyle='--')
        
        text_str = f'$\mathbf{{r = {pearson_r:.3f}}}$'
        ax.text(0.05, 0.96, text_str, transform=ax.transAxes, fontsize=TEXT_SIZE, fontweight='bold',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
        
        # Apply specific axis limits
        if x_col in axis_limits:
            ax.set_xlim(axis_limits[x_col])
        if y_col in axis_limits:
            ax.set_ylim(axis_limits[y_col])
            
        ax.set_xlabel(x_col, fontsize=LABEL_SIZE, fontweight='bold')
        ax.set_ylabel(y_col, fontsize=LABEL_SIZE, fontweight='bold')
        # ax.set_title(f'{y_col} vs {x_col}', fontsize=TITLE_SIZE, fontweight='bold')
        
        # Apply Custom Styling and Ticks
        apply_custom_style(ax, 
                           x_ticks_cfg=axis_ticks.get(x_col), 
                           y_ticks_cfg=axis_ticks.get(y_col))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{base_name}_plots_all_new_16_18_fixed.png'))
    plt.close()
    
    # --- Save Statistics Table ---
    df_stats = pd.DataFrame(stats_data)
    
    # Pivot to wide format
    df_pivot = df_stats.pivot(index='Pair', columns='Scenario', values=['R_squared', 'Pearson_r'])
    df_pivot.columns = ['_'.join(col).strip() for col in df_pivot.columns.values]
    df_pivot.reset_index(inplace=True)
    
    # Sort
    pair_order = [f'{y} vs {x}' for y, x, _, _ in pairs_config]
    df_pivot['Pair'] = pd.Categorical(df_pivot['Pair'], categories=pair_order, ordered=True)
    df_pivot.sort_values('Pair', inplace=True)
    
    output_csv = os.path.join(output_dir, f'{base_name}_regression_stats_new.csv')
    df_pivot.to_csv(output_csv, index=False)
    print(f"Stats table saved to: {output_csv}")
    print("All plots generated successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
    else:
        generate_plots_and_stats(sys.argv[1])