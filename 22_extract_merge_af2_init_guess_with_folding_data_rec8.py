
__author__  = 'Abeeb A. Yekeen'
__email__   = 'abeeb.yekeen@utsouthwestern.edu'
__date__    = 'Jan-24-2024'
__version__ = '1.0'
__status__  = 'Beta'


import os
import time
import shutil

work_home = os.getcwd()
intermed8 = "AFcomplex/mpnn_out_clust_fold"

def main():
    with open("example_list_of_complexes.dat") as complexes:
        for line_no, kinase_pep in enumerate(complexes):
            kinase_pep = kinase_pep.rstrip("\n")
            af2_sc_file = get_af2_score_file(kinase_pep)
            if af2_sc_file == "nil": continue
            mergedict = merge_metrics(kinase_pep, af2_sc_file)
            write_out_data(kinase_pep, mergedict)
            print(f" {kinase_pep} processed succesfully...\n")

def get_af2_score_file(kinase_pep):
    if not kinase_pep.startswith("#"):
        print(f"\n Getting af2_score.dat file for {kinase_pep}\n")
        # time.sleep(1)
        kinase_pep = kinase_pep.rstrip("\n")
        af2score_file = os.path.join(work_home,
                                    kinase_pep,
                                    intermed8,
                                    "af2_init_guess.rec8/af2score.dat"
                                    )
        return af2score_file
    elif kinase_pep.startswith("#"):
        af2score_file = "nil"
        return af2score_file
                                     
def merge_metrics(kinase_pep, af2score_file):
    merger_dict = {}
    with open(af2score_file) as af2_file:
        print(f" Opening af2score.dat for {kinase_pep}\n")
        # time.sleep(1)
        for num, line in enumerate(af2_file):
            merger_sample = []
            line = line.rstrip("\n")
            line_split = line.split()
            
            del line_split[0]  # delete "SCORE:" from the the line
            del line_split[6]  # delete time column

            if num == 0:
                headers = ["ipTM", "pTM", "pLDDT", "fold", "id"]
                for_insertn = headers
                dict_key = "header"
                del line_split[-1] # delete description
        
            elif num > 0:
                # print(f"printing line at merge_metrics -> {line}\n")
                descriptn = line_split[-1].split("_unrelaxed_")
                design_id = descriptn[0]

                del line_split[-1] # delete description

                # print(f"Printing design ID -> {design_id}\n")
                dict_key = design_id
                clust_fold_file = os.path.join(work_home,
                                            kinase_pep,
                                            intermed8,
                                            "seqs",
                                            design_id,
                                            "log.txt"
                                            )
                with open(clust_fold_file) as cff:
                    for i in cff:
                        if "rank_001" in i:
                            # print(f"printing rank_001 -> {i}\n")
                            dataline = i.rstrip("\n").split()
                            break
                iptm = dataline[-1].replace("ipTM=", "")
                ptm = dataline[-2].replace("pTM=", "")
                plddt = dataline[-3].replace("pLDDT=", "")
                fld = dataline[-4].split("_v3_")
                fld = fld[0]
                scores = [iptm, ptm, plddt, fld, design_id]
                for_insertn = scores
            
            for i in for_insertn: line_split.insert(0, i)
            merger_dict[dict_key] = line_split

        merger_dict
        return merger_dict
        
def write_out_data(kinase_pep, data_dict):
    print(f" Writing out the data for {kinase_pep}\n")
    merged_data = os.path.join(work_home,
                               kinase_pep,
                               intermed8,
                               "af2_init_guess.rec8",
                               f"{kinase_pep}_merged_scores.csv"
                               )
    with open(merged_data, "w") as mdata:
        for metric_list in data_dict.values():
            for i in metric_list:
                if i == metric_list[-1]: mdata.write(f"{i}\n")
                else: mdata.write(f"{i},")
    
    dest = f"{work_home}/af2_init_guess/data/{kinase_pep}/"

    if not os.path.exists(dest):
        os.makedirs(dest)

    shutil.copy2(merged_data, dest)
    print(" Copying the written data to the home working dir (af2_init_guess)\n")

if __name__ == "__main__":
    main()