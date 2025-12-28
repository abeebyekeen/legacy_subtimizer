
__author__  = 'Abeeb A. Yekeen'
__email__   = 'abeeb.yekeen@utsouthwestern.edu'
__date__    = 'Jan-30-2024'
__version__ = '1.0'
__status__  = 'Beta'


import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# from matplotlib import font_manager

from matplotlib import rcParams
# font_manager._rebuild()

# font_path = "/work/.conda/envs/af2_des/fonts/Arial.ttf"
# matplotlib.rcParams['font.family'] = matplotlib.font_manager.FontProperties(fname=font_path).get_name()
# arial_font = font_manager.FontProperties(fname=font_path).get_name()
matplotlib.rcParams['font.family'] = 'Arial'
plt.rcParams['font.family'] = 'Arial'

# ALK_axltide_merged_scores_pTM-ipTM_with_oriSubs_SEQ_with_ipSAE_14_14_parental_LAST.csv

work_home = "/work/RADONC/s226058/wspace/proDesign/kinase_pep_design/YST_fixed"
# intermed8 = "AFcomplex/mpnn_out_clust_fold"
ori_sub_intermed8 = "original_subs/af2_init_guess/data"

special = ["AKT2_gsk3tide_1O6K", "AKT2_gsk3tide_1O6L"]

with open("../list_of_complexes.dat") as complexes:
    for line_no, kinase_pep in enumerate(complexes):
        kinase_pep = kinase_pep.rstrip("\n")
        if not kinase_pep.startswith("#"):
        # if kinase_pep == "ABL1_abltide":
            if kinase_pep in special:
                csvfile = f"{kinase_pep}_merged_scores_pTM-ipTM.csv"
            else:
                csvfile = f"{kinase_pep}_merged_scores_pTM-ipTM_with_oriSubs_SEQ_with_ipSAEmin_15_15.csv"
            file_in = os.path.join(work_home,
                                    # intermed8,
                                    ori_sub_intermed8,
                                    kinase_pep,
                                    f"{csvfile}"
                                    )

            df = pd.read_csv(file_in)
            print(f" Data for {kinase_pep} read successfully\n")

            # Check if columns 6 and 8 are numeric
            if df.iloc[:, 5].dtype.kind in 'biufc' and df.iloc[:, 7].dtype.kind in 'biufc':
                # Plot a pTM+ipTM vs pae_interaction
                plt.figure()
                # ptm_iptm_score = df.iloc[:, 5]
                # pae_inter_score = df.iloc[:, 7]
                # plt.scatter(ptm_iptm_score, pae_inter_score)

                marker="*"
                # size=150
                size=100
                size_star=600
                star_edge_thickness=4

                if kinase_pep in special:
                    plt.scatter(x=df['pTM_ipTM'][:-1], y=df['pae_interaction'][:-1], s=size)
                else:
                    scatter = plt.scatter(x=df['pTM_ipTM'][:-1], y=df['pae_interaction'][:-1], s=size)

                # Highlight the last data point with a different symbol
                plt.scatter(x=df['pTM_ipTM'].iloc[-1], y=df['pae_interaction'].iloc[-1], marker=marker,
                             c='red', s=size_star, edgecolor='black', linewidths=star_edge_thickness, label='Parental')

                plt.ylabel(r'$\mathbf{ipAE}$' + r' ($\AA$)', fontsize=21)
                plt.xlabel(r'$\mathbf{0.2pTM+0.8ipTM}$', fontsize=21)
                plt.title(f'{kinase_pep}')
                figname = f"data/{kinase_pep}/{kinase_pep}_scatter_pTM-ipTM_vs_pae-inter_withOriSubs_fixOrdiAbsci_opt_bigfont_arial_upd40_pt2pt8.png"
                plt.legend(loc='lower left', fontsize=14)
                # plt.yticks(np.arange(6.0, 30.5, 2))
                plt.yticks(np.arange(6.0, 30.5, 6), fontsize=20, fontweight='bold')
                plt.xticks(np.arange(0.4, 1.0, 0.2), fontsize=20, fontweight='bold')
                plt.xticks(np.arange(0.4, 1.0, 0.1), minor=True)
                plt.tick_params(axis='both', which='major', length=6, width=1.7)
                plt.tick_params(axis='x', which='minor', length=4, width=1.5)
                plt.xlim(0.35, 0.96)
                plt.ylim(5.7, 30)

                # Customize axis lines thickness
                ax = plt.gca()  # Get the current axis
                ax.spines['top'].set_linewidth(1.5)
                ax.spines['right'].set_linewidth(1.5)
                ax.spines['left'].set_linewidth(1.5)
                ax.spines['bottom'].set_linewidth(1.5)

                plt.savefig(figname, dpi=300, bbox_inches='tight')
                figname_ = os.path.join(work_home, ori_sub_intermed8, kinase_pep,
                                        f"{kinase_pep}_scatter_pTM-ipTM_vs_pae-inter_withOriSubs_fixOrdiAbsci_opt_bigfont_arial_upd40_pt2pt8.png"
                                        )
                
                # plt.savefig(figname_, dpi=300, bbox_inches='tight')
                
                print(f"Plot 1 successfully generated for {kinase_pep}\n")
                plt.close()

                # Plot a 0.2pTM+0.8ipTM vs pae_interaction vs ipSAE_min
                fig, ax = plt.subplots()  # Create a figure and an axes

                # Define the fixed range for the color normalization
                fixed_min, fixed_max = 0.05, 0.35
                norm = plt.Normalize(fixed_min, fixed_max)

                # Pre-calculate the colors for each point
                colors = plt.cm.turbo_r(norm(df['ipSAE_min']))

                if kinase_pep in special:
                    ax.scatter(x=df['pTM_ipTM'][:-1], y=df['pae_interaction'][:-1], c=colors[:-1], s=size)
                
                else:
                    ax.scatter(x=df['pTM_ipTM'][:-1], y=df['pae_interaction'][:-1], c=colors[:-1], s=size)
                    
                    ax.scatter(x=df['pTM_ipTM'].iloc[-1], y=df['pae_interaction'].iloc[-1], s=size_star, 
                                marker=marker, linewidths=star_edge_thickness, edgecolor='black', label='Parental', c=[colors[-1]])
                
                # Create a ScalarMappable for the colorbar and add it to the axes
                sm = plt.cm.ScalarMappable(cmap='turbo_r', norm=norm)
                cbar = fig.colorbar(sm, ax=ax, label='ipSAE_min')

                # Make the colorbar tick labels bold
                cbar.ax.tick_params(labelsize=19)  # Set the size
                cbar.ax.yaxis.set_tick_params(labelsize=19, which='both')  # Apply to both major and minor ticks
                for label in cbar.ax.get_yticklabels():
                    label.set_fontweight('bold')  # Set bold weight

                # cbar.ax.tick_params(labelsize=19, fontweight='bold')  # Increase tick size for colorbar
                # cbar.set_label(r'$\mathbf{ipSAE_min}$' + r'_$\mathbf{max}$', fontsize=21)
                cbar.set_label(r'$\mathbf{ipSAE}$' + r'_$\mathbf{min}$', fontsize=21)

                ax.set_ylabel(r'$\mathbf{ipAE}$' + r' ($\AA$)', fontsize=21)
                ax.set_xlabel(r'$\mathbf{0.2pTM+0.8ipTM}$', fontsize=21)
                ax.set_title(f'{kinase_pep}', fontsize=10)
                
                plt.yticks(np.arange(6.0, 30.5, 6), fontsize=20, fontweight='bold')
                # plt.xticks(np.arange(0.3, 1.01, 0.1), fontsize=14)
                plt.xticks(np.arange(0.4, 1.0, 0.2), fontsize=20, fontweight='bold')
                plt.xticks(np.arange(0.4, 1.0, 0.1), minor=True)

                if kinase_pep not in special:
                    ax.legend(loc='lower left', fontsize=14)

                plt.xticks(np.arange(0.4, 1.0, 0.1), minor=True)
                plt.tick_params(axis='both', which='major', length=6, width=1.7)
                plt.tick_params(axis='x', which='minor', length=4, width=1.5)
                plt.xlim(0.35, 0.96)
                plt.ylim(5.7, 30)

                # Customize axis lines thickness
                ax = plt.gca()  # Get the current axis
                ax.spines['top'].set_linewidth(1.5)
                ax.spines['right'].set_linewidth(1.5)
                ax.spines['left'].set_linewidth(1.5)
                ax.spines['bottom'].set_linewidth(1.5)

                figname2 = f"data/{kinase_pep}/{kinase_pep}_scatter_pTM-ipTM_vs_pae-inter_vs_ipSAE_min_withOriSubs_bigfont_arial_pt2pt8.png"
                fig.savefig(figname2, dpi=300, bbox_inches='tight')

                figname2_ = os.path.join(work_home, ori_sub_intermed8, kinase_pep,
                                        f"{kinase_pep}_scatter_pTM-ipTM_vs_pae-inter_vs_ipSAE_min_withOriSubs_bigfont_arial_pt2pt8.png"
                                        )
                fig.savefig(figname2_, dpi=300, bbox_inches='tight')

                print(f"Plot 2 successfully generated for {kinase_pep}\n")

                # Identify the 5 points with the lowest paes (Column 6) values
                lowest_paes = df.nsmallest(5, 'pae_interaction')
                # Label each point with the a segment of the id (in column 1)
                for _, row in lowest_paes.iterrows():
                    id_full = row['id']
                    # Using the last segment and replacing 'sample' with 'des'
                    label = id_full.split('_')[-1].replace('sample', 'des')
                    plt.text(row['pTM_ipTM'], row['pae_interaction'], label, fontsize=10)

                plt.yticks(np.arange(6.0, 30.5, 6), fontsize=20, fontweight='bold')
                plt.xticks(np.arange(0.4, 1.0, 0.2), fontsize=20, fontweight='bold')
                plt.xticks(np.arange(0.4, 1.0, 0.1), minor=True)

                plt.tick_params(axis='both', which='major', length=6, width=1.7)
                plt.tick_params(axis='x', which='minor', length=4, width=1.5)
                plt.xlim(0.35, 0.96)
                plt.ylim(5.7, 30)

                # Customize axis lines thickness
                ax = plt.gca()  # Get the current axis
                ax.spines['top'].set_linewidth(1.5)
                ax.spines['right'].set_linewidth(1.5)
                ax.spines['left'].set_linewidth(1.5)
                ax.spines['bottom'].set_linewidth(1.5)

                figname3 = f"data/{kinase_pep}/{kinase_pep}_scatter_pTM-ipTM_vs_pae-inter_vs_ipSAE_min_labelled_withOriSubs_bigfont_arial_pt2pt8.png"
                if kinase_pep not in special:
                    ax.legend(loc='lower left', fontsize=14)
                fig.savefig(figname3, dpi=300, bbox_inches='tight')

                figname3_ = os.path.join(work_home, ori_sub_intermed8, kinase_pep,
                                        f"{kinase_pep}_scatter_pTM-ipTM_vs_pae-inter_vs_ipSAE_min_labelled_withOriSubs_bigfont_arial_pt2pt8.png"
                                        )
                fig.savefig(figname3_, dpi=300, bbox_inches='tight')

                print(f"Plot 3 successfully generated for {kinase_pep}\n")
                plt.close()
                
            else:
                print(f"Columns 6 and 8 are not numeric for {kinase_pep}\n")
