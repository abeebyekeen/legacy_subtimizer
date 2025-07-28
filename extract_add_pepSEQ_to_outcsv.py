
__author__  = 'Abeeb A. Yekeen'
__email__   = 'abeeb.yekeen@utsouthwestern.edu'
__date__    = 'Feb-07-2024'
__version__ = '1.0'
__status__  = 'Beta'

import os
import glob


work_home = "/work/RADONC/s226058/wspace/proDesign/kinase_pep_design/YST_fixed"
intermed8_ori = "original_subs/af2_init_guess/data"
intermed8 = "AFcomplex/mpnn_out_clust"

special = ["AKT2_gsk3tide_1O6K", "AKT2_gsk3tide_1O6L"]

def main():
    with open("list_of_complexes.dat") as complexes:
        for complex in complexes:
            if complex.startswith("#"): continue
            complex = complex.rstrip("\n")
            
            csvfile = os.path.join(work_home,
                                    # complex,
                                    intermed8_ori,
                                    complex,
                                    f"{complex}_merged_scores_pTM-ipTM_with_oriSubs.csv"
                                    )
            csvfile_out = os.path.join(work_home,
                                        # complex,
                                        intermed8_ori,
                                        complex,
                                        f"{complex}_merged_scores_pTM-ipTM_with_oriSubs_SEQ.csv"
                                        )
            if complex in special:
                csvfile = os.path.join(work_home, "af2_init_guess/data", complex,
                                       f"{complex}_merged_scores_pTM-ipTM.csv"
                                        )
                csvfile_out = os.path.join(work_home, "af2_init_guess/data", complex,
                                            f"{complex}_merged_scores_pTM-ipTM_with_SEQ.csv"
                                            )
            

            cluster_seq = os.path.join(work_home,
                                        complex,
                                        intermed8,
                                        "all_design_clustered.fa"
                                        )

            dict_in = {}
            with open(csvfile) as datafile:
                for num, line in enumerate(datafile, 1):
                    line = line.rstrip("\n").split(",")
                    des_id, des_data = line[0], line
                    if num > 1:
                        des_id = des_id.split("_")
                        des_id = des_id[-1]
                    dict_in[des_id] = des_data
            
            print(f" Data for {complex} read successfully")
            # print(dict_in)

            dict_seq = {}
            with open(cluster_seq) as seqs:
                for seq in seqs:
                    if ">" in seq:
                        header_ = seq.split(",")
                        header_ = header_[1].strip().replace("=","")
                        continue
                    else:
                        seq = seq.rstrip("\n")
                    dict_seq[header_] = seq
            
            files = glob.glob(f"{work_home}/{complex}/AFcomplex/mpnn_out/seqs/*_*_*.fa")
            orig_seq = files[0]

            # print(dict_seq)
            with open(orig_seq) as raw_des:
                for line in raw_des:
                    if ">" in line:
                        header_ = line.split(",")
                        header_ = header_[0]
                        continue
                    else:
                        seq = line.rstrip("\n")
                    dict_seq["ori"] = seq
                    break

            with open(csvfile_out, "w") as outfile:
                for key, value in dict_in.items():
                    for i in value:
                        outfile.write(f"{i},")
                    if "id" in key:
                        outfile.write("key,pep_sequence\n")
                        continue
                    elif not "sample" in key:
                        d_seq = dict_seq["ori"]
                    else:
                        d_seq = dict_seq[key]
                    outfile.write(f"{key},{d_seq}\n")
            print(f" {complex} processed successfully\n")

if __name__ == "__main__":
    main()
