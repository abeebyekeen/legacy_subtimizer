__author__  = 'Abeeb A. Yekeen'
__date__    = 'Jan-30-2024'
__version__ = '1.0'
__status__  = 'Beta'

import os
import numpy as np
import pandas as pd
import seaborn as sns
import colorcet as cc
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Set working directory relative to script location
work_home = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
intermed8 = "AFcomplex/mpnn_out_clust_fold"

def main():
    """Main function to generate and save swarm plots for different data ranges."""
    files_list = get_data()
    palette = sns.color_palette(cc.glasbey, n_colors=48)
    raw_data = {}
    pretty_data = {}

    plot_ranges = [
        (0, 11, "1to12", palette[1:13]),
        (12, 23, "13to24", palette[13:25]),
        (24, 35, "25to36", palette[25:37]),
        (36, 47, "37to48", palette[37:48]),
    ]

    for lower, upper, label, pal in plot_ranges:
        print(f"\nPlotting set {label}\n")
        complex_list = make_data_range(files_list, lower, upper)
        plot_swarm(complex_list, label, pal, raw_data, pretty_data)

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    pd.DataFrame.from_dict(raw_data, orient='index').T.to_csv(
        "data/allData_swarmplot_data_raw.csv", index=False)
    pd.DataFrame.from_dict(pretty_data, orient='index').T.to_csv(
        "data/allData_swarmplot_data_pretty.csv", index=False)

def get_data():
    """Fetch list of complexes from a file, excluding commented entries."""
    print("Fetching data\n")
    complexes = []
    excluded = set()
    try:
        with open("../example_list_of_complexes.dat") as inlist:
            for line in inlist:
                line = line.strip()
                if not line.startswith("#") and line not in excluded:
                    complexes.append(line)
    except FileNotFoundError:
        print("Error: '../example_list_of_complexes.dat' not found.")
    return complexes

def make_data_range(complexes, lower_value, upper_value):
    """Returns a sublist of complexes within the specified index range."""
    print("Preparing the required range of data\n")
    return [p for num, p in enumerate(complexes) if lower_value <= num <= upper_value]

def plot_swarm(complex_list, datarange, palettex, raw_data, pretty_data):
    """Plots and saves a swarm plot for the given complex list and data range."""
    print(f"Plotting the figure for {datarange}\n")
    plt.figure(figsize=(6, 10))
    plt.rcParams['axes.linewidth'] = 1.7
    plt.rcParams['xtick.major.width'] = 1.7
    plt.rcParams['ytick.major.width'] = 1.7
    plt.rcParams['xtick.major.size'] = 5.2
    plt.rcParams['ytick.major.size'] = 4.0

    special = {}
    pep_name_replacements = {}

    for idx, complex_name in enumerate(complex_list):
        csvfile = (
            f"{complex_name}_merged_scores_pTM-ipTM.csv"
            if complex_name in special
            else f"{complex_name}_merged_scores_pTM-ipTM_with_oriSubs.csv"
        )

        # Try rec6, then rec8
        file_in = os.path.join(work_home, complex_name, intermed8, "af2_init_guess.rec6", csvfile)
        if not os.path.isfile(file_in):
            file_in = os.path.join(work_home, complex_name, intermed8, "af2_init_guess.rec8", csvfile)
            if not os.path.isfile(file_in):
                print(f"Warning: File not found for {complex_name}")
                continue

        df = pd.read_csv(file_in)
        pae_inter_data = df.iloc[:, 7]

        # Pretty label replacements
        p_name = complex_name
        for old, new in pep_name_replacements.items():
            p_name = p_name.replace(old, new)

        # Store data
        raw_data.setdefault(complex_name, []).extend(pae_inter_data.tolist())
        pretty_data.setdefault(p_name, []).extend(pae_inter_data.tolist())

        # Plot all points except the last one
        ax = sns.swarmplot( y=[p_name] * (len(pae_inter_data) - 1), x=pae_inter_data[:-1], alpha=0.9, color=palettex[idx], size=6)
        # Highlight the last data point
        plt.scatter(y=p_name, x=pae_inter_data.iloc[-1], s=60, color='red', edgecolor='black', zorder=28)      

        print(f"Plotted {complex_name}...\n")

    plt.xticks(np.arange(6.0, 30.5, 4), fontsize=17)
    plt.yticks(fontsize=17)
    plt.ylabel('Kinase-peptide complex', fontsize=20, fontweight='bold')
    plt.xlabel('ipAE' + r' ($\AA$)', fontsize=20, fontweight='bold')
    ax.xaxis.set_major_locator(ticker.MultipleLocator(4))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.tick_params(axis='x', which='major', length=5.2, width=1.7)
    ax.tick_params(axis='x', which='minor', length=4, width=1.4)
    figname = f"data/swarmplot_withOriSubs_portrait_{datarange}_updated.png"
    plt.savefig(figname, dpi=300, bbox_inches='tight')
    plt.clf()

if __name__ == "__main__":
    main()