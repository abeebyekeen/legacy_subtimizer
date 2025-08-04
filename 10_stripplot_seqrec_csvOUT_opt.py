
__author__  = 'Abeeb A. Yekeen'
__email__   = 'abeeb.yekeen@utsouthwestern.edu'
__date__    = 'Jan-04-2024'
__version__ = '1.0'
__status__  = 'Beta'

import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import colorcet as cc
import time


#fetch kinase-peptide complex data
def get_data():
    # excluded = {"AKT1_3akt1tide", "AKT2_3akt1tide", "AKT3_3akt1tide", "SGK1_3akt1tide"}
    excluded = {}
    with open("example_list_of_complexes.dat") as file:
        return [line.strip() for line in file if line.strip() not in excluded]

#make a dict of sequence recovery data for a range of files
def make_dict_range(files, start, end):
    secrecSet = {}
    for num, p in enumerate(files[start:end+1], start):
        print(f"Reading data from {p}")
        path = f"{p}/AFcomplex/mpnn_out/seqs/sec_recovery.dat"
        try:
            with open(path) as file:
                secrecSet[p] = [float(line.strip()) for line in file]
        except FileNotFoundError:
            print(f"Missing file: {path}")
    return secrecSet

#generate and save strip plot from seq rec data
def plot_strip(secrecSet, datarange, palettex):
    data = pd.DataFrame.from_dict(secrecSet, orient="index").T
    data.to_csv(f"strip_plot_data_{datarange}_upd.csv")
    
    long_data = data.melt(var_name="Kinase-peptide complex",
                          value_name="Fraction of peptide sequence recovered")

    # plt.figure(figsize=(10, 6))
    sns.stripplot(x="Kinase-peptide complex",
                  y="Fraction of peptide sequence recovered",
                  data=long_data, hue="Kinase-peptide complex",
                  alpha=0.5, palette=palettex)

    plt.xticks(rotation=75)
    plt.yticks(np.arange(0, 1, 0.1))
    plt.ylim(-0.0225, 0.95)
    plt.legend([],[], frameon=False)
    plt.tight_layout()
    plt.savefig(f"Complex_{datarange}_stripplot.png", dpi=300)
    plt.clf()


def main():
    files_list = get_data()
    palette = sns.color_palette(cc.glasbey, n_colors=48)
    ranges = [(0, 11)]#, (12, 23), (24, 35), (36, 47)]

    for idx, (start, end) in enumerate(ranges, 1):
        print(f"\nPlotting set {idx} ({start+1} to {end+1})\n")
        time.sleep(1)
        data_dict = make_dict_range(files_list, start, end)
        palette_subset = palette[start:end+1]
        plot_strip(data_dict, f"{start+1}to{end+1}", palette_subset)


if __name__ == "__main__":
    main()
