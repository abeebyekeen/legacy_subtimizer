
__author__  = 'Abeeb A. Yekeen'
__email__   = 'abeeb.yekeen@utsouthwestern.edu'
__date__    = 'Jan-30-2024'
__version__ = '1.0'
__status__  = 'Beta'

import os
import time
import numpy as np
import pandas as pd
import seaborn as sns
import colorcet as cc
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

work_home = "/work/RADONC/s226058/wspace/proDesign/kinase_pep_design/YST_fixed"
intermed8 = "AFcomplex/mpnn_out_clust_fold"


def main():
    files_list = get_data()
    palette = sns.color_palette(cc.glasbey, n_colors=48)
    
    raw_data = {}      # original complex name
    pretty_data = {}   # edited label
    
    print("\nPlotting set 1\n")
    # lower_value, upper_value= 0, 13
    complexList = make_data_range(files_list, 0, 11)
    # combineddata = make_dataframe(complexList)
    # palette1 = palette[:10]
    palette1 = palette[1:13]
    plot_swarm(complexList, "1to12", palette1, raw_data, pretty_data)
    
    print("\nPlotting set 2\n")
    # # lower_value, upper_value= 12, 33
    complexList = make_data_range(files_list, 12, 23)
    # palette1 = palette[10:21]
    palette1 = palette[13:25]
    # plot_swarm(complexList, "11to20", palette1, raw_data, pretty_data)
    plot_swarm(complexList, "13to24", palette1, raw_data, pretty_data)
    
    print("\nPlotting set 3\n")
    # # lower_value, upper_value= 0, 13
    complexList = make_data_range(files_list, 24, 35)
    palette1 = palette[25:37]
    # plot_swarm(complexList, "21to29", palette1, raw_data, pretty_data)
    plot_swarm(complexList, "25to36", palette1, raw_data, pretty_data)

    print("\nPlotting set 4\n")
    # # lower_value, upper_value= 0, 13
    complexList = make_data_range(files_list, 36, 47)
    # combineddata = make_dataframe(complexList)
    # palette1 = palette[21:30]
    palette1 = palette[37:48]
    # plot_swarm(complexList, "21to29", palette1, raw_data, pretty_data)
    plot_swarm(complexList, "37to48", palette1, raw_data, pretty_data)    

    df_raw = pd.DataFrame.from_dict(raw_data, orient='index').T
    df_pretty = pd.DataFrame.from_dict(pretty_data, orient='index').T

    df_raw.to_csv("data/allData_swarmplot_data_raw.csv", index=False)
    df_pretty.to_csv("data/allData_swarmplot_data_pretty.csv", index=False)


def get_data():
    print("Fetching data\n")
    # time.sleep(1)
    complexes = []
    excluded = {
                # "FGFR1_csktide", "FGFR1_srctide",
                # "FGFR4_csktide", "VEGFR2_jaktide"
                }
    with open("../list_of_complexes_upd.dat") as inlist:
        for f in inlist:
            f = f.strip()
            if not f.startswith("#") and f not in excluded:
                complexes.append(f)
    return complexes

def make_data_range(complexes, lower_value, upper_value):
    print("Preparing the required range of data\n")
    # time.sleep(1)

    complex_list = []
    
    for num, p in enumerate(complexes):
        if lower_value <= num <= upper_value:
            complex_list.append(p)
    return complex_list

def plot_swarm(complex_list, datarange, palettex, raw_data, pretty_data):
    print(f"Plotting the figure for {datarange}\n")
    plt.figure(figsize=(6, 10))
    plt.rcParams['axes.linewidth'] = 1.7
    plt.rcParams['xtick.major.width'] = 1.7
    plt.rcParams['ytick.major.width'] = 1.7
    plt.rcParams['xtick.major.size'] = 5.2 #3.7
    plt.rcParams['ytick.major.size'] = 4.0 #3.7

    special = {"AKT2_gsk3tide_1O6K", "AKT2_gsk3tide_1O6L"}
    for idx, complex in enumerate(complex_list):
        if complex in special:
            csvfile = f"{complex}_merged_scores_pTM-ipTM.csv"
        else:
            csvfile = f"{complex}_merged_scores_pTM-ipTM_with_oriSubs.csv"

        try:
            file_in = os.path.join(work_home, complex, intermed8, 
                                   "af2_init_guess.rec6", csvfile
                               )
            df = pd.read_csv(file_in)
        except FileNotFoundError:
            file_in = os.path.join(work_home, complex, intermed8,
                                   "af2_init_guess.rec8", csvfile
                               )
            df = pd.read_csv(file_in)        
        pae_inter_data = df.iloc[:, 7]
        
        # if "tide_" in complex:
        #     # p_name = complex[:4] + complex[-5:]
        #     p_name = complex
        # else:
        #     # p_name = complex[:-4]
        #     p_name = complex
        pepNamereplacements = {
            "1akt1tide": "akt1tide1",
            "2akt1tide": "akt1tide2",
            "1csktide": "csktide1",
            "2csktide": "csktide2",
            "1srctide": "srctide1",
            "2srctide": "srctide2",
            "EGFRm": "EGFR L858R",
            "_": "."
        }

        p_name = complex
        for old, new in pepNamereplacements.items():
            p_name = p_name.replace(old, new)

        # Store under original name
        if complex not in raw_data:
            raw_data[complex] = []
        raw_data[complex].extend(pae_inter_data.tolist())

        # Store under pretty label
        if p_name not in pretty_data:
            pretty_data[p_name] = []
        pretty_data[p_name].extend(pae_inter_data.tolist())

        # Plot all points except the last one
        # swarm = sns.swarmplot(x=[p_name]*len(pae_inter_data[:-1]), y=pae_inter_data[:-1], 
                    #   alpha=0.9, color=palettex[idx], size=4)

        ax = sns.swarmplot(y=[p_name]*len(pae_inter_data[:-1]), x=pae_inter_data[:-1], 
                      alpha=0.9, color=palettex[idx], size=6)
        # Highlight the last data point
        # sns.swarmplot(x=[p_name], y=pae_inter_data.iloc[-1], s=12, 
        #               color=palettex[idx], edgecolor='black')#, marker='*')#color='red', 

        plt.scatter(y=p_name, x=pae_inter_data.iloc[-1], s=60, 
                    color='red', edgecolor='black', zorder=28)
        
        print(f"Plotted {complex}...\n")

    # sns.swarmplot(x='Kinase-peptide complex', y='pae_interaction', data=combined_data, 
    #                       hue="Kinase-peptide complex", alpha = 0.9, palette = palettex, size=4)
    
    # plt.xticks(rotation=75, ha='right')
    plt.xticks(np.arange(6.0, 30.5, 4), fontsize=17)
    plt.yticks(fontsize=17)
    plt.ylabel('Kinase-peptide complex', fontsize=20, fontweight='bold')
    plt.xlabel('ipAE'+r' ($\AA$)', fontsize=20, fontweight='bold')
    ax.xaxis.set_major_locator(ticker.MultipleLocator(4))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))
    ax.tick_params(axis='x', which='major', length=5.2, width=1.7)
    ax.tick_params(axis='x', which='minor', length=4, width=1.4)      
    # plt.tight_layout()
    figname = f"data/swarmplot_withOriSubs_portrait_{datarange}_updated.png"
    plt.savefig(figname, dpi=300, bbox_inches='tight')
    plt.clf()

if __name__ == "__main__":
    main()
