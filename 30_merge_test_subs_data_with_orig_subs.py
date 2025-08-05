
__author__  = 'Abeeb A. Yekeen'
__email__   = 'abeeb.yekeen@utsouthwestern.edu'
__date__    = 'Jan-30-2024'
__version__ = '1.0'
__status__  = 'Beta'


import os, time
import shutil

parent_home = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
parent_intermed8 = "AFcomplex/mpnn_out_clust_fold/af2_init_guess.rec8"
ori_sub_intermed8 = "original_subs/af2_init_guess/data"

with open("../list_of_complexes_dark_confident.dat") as complexes:
    for line_no, kinase_pep in enumerate(complexes):
        print(f"Processing {kinase_pep}")
        kinase_pep = kinase_pep.rstrip("\n")

        if kinase_pep.startswith("#"): continue

        af2_score_des = os.path.join(parent_home,
                                     kinase_pep,
                                     parent_intermed8,
                                     f"{kinase_pep}_merged_scores_pTM-ipTM.csv"
                                     )
        
        af2_score_ori = os.path.join(parent_home,
                                     "original_subs",
                                     kinase_pep,
                                     "af2_init_guess.rec8",
                                     f"{kinase_pep}_merged_scores_pTM-ipTM.csv"
                                     )
        out_file = os.path.join(parent_home,
                                ori_sub_intermed8,
                                kinase_pep,
                                f"{kinase_pep}_merged_scores_pTM-ipTM_with_oriSubs.csv"
                                )
        with open(out_file, "w") as outf:
            with open(af2_score_des) as des:
                for data in des:
                    data = data.rstrip("\n")
                    outf.write(f"{data}\n")
            with open(af2_score_ori) as ori:
                for line_no, line in enumerate(ori):
                    if line_no == 1:
                        print(f"Writing out {line}")
                        outf.write(line)
                        break

        dest = f"{parent_home}/{kinase_pep}/{parent_intermed8}"
        dest_f = f"{kinase_pep}_merged_scores_pTM-ipTM_with_oriSubs.csv"

        if os.path.isfile(f"{dest}/{dest_f}"):
            os.remove(f"{dest}/{dest_f}")
        shutil.copy2(out_file, dest)
        print(" Copying the written data to the home working dir\n")