import os
import pandas as pd
import shutil
import time


work_home = os.getcwd()
intermed8 = "AFcomplex/mpnn_out_clust_fold"

with open("list_of_complexes_dark_confident.dat") as complexes:
    for line_no, kinase_pep in enumerate(complexes):
        kinase_pep = kinase_pep.rstrip("\n")
        if not kinase_pep.startswith("#"):
            file_in = os.path.join(work_home,
                                    kinase_pep,
                                    intermed8,
                                    "af2_init_guess.rec8",
                                    f"{kinase_pep}_merged_scores.csv"
                                    )

            df = pd.read_csv(file_in)
            print(f" Data for {kinase_pep} read successfully\n")

            # Check if columns 4 and 5 are numeric
            if df.iloc[:, 3].dtype.kind in 'biufc' and df.iloc[:, 4].dtype.kind in 'biufc':
                # Calculate the sum of weighted columns 4 (pTM) and 5 (ipTM)
                confidence_column = (0.2 * df.iloc[:, 3] + 0.8 * df.iloc[:, 4]).round(3)

                df.insert(5, 'pTM_ipTM', confidence_column)

                file_out = os.path.join(work_home,
                                        kinase_pep,
                                        intermed8,
                                        "af2_init_guess.rec8",
                                        f"{kinase_pep}_merged_scores_pTM-ipTM.csv"
                                        )

                df.to_csv(file_out, index=False)
                print(f"pTM+ipTM column added successfully for {kinase_pep}\n")

                dest = f"{work_home}/af2_init_guess/data/{kinase_pep}/"

                shutil.copy2(file_out, dest)
                print(" Copying the updated data to the home working dir (af2_init_guess)\n")  
                time.sleep(1)          
            
            else:
                print(f"Columns 4 and 5 are not numeric for {kinase_pep}\n")
