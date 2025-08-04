import glob
import os
import time
import shutil


with open("example_list_of_complexes.dat") as folder_list:
    for f in folder_list:
        f = f.rstrip("\n")
        print(f"Processing {f}\n")
        # time.sleep(1)
        complex_fasta = glob.glob(f"{f}/*.fasta")
        for cfasta in complex_fasta:
            with open(cfasta) as fas:
                for line in fas:
                    if ">" in line:
                        header = line.rstrip("\n").replace(">", "")
                    elif not ">" in line:
                        kinase_seq = line.split(":")[0]

        pathAFcomplex = f"{f}/AFcomplex"
        pathClusters = f"{f}/AFcomplex/mpnn_out_clust"
        pathClustersFold = f"{f}/AFcomplex/mpnn_out_clust_fold"
        pathClustersFoldSeq = f"{f}/AFcomplex/mpnn_out_clust_fold/seqs"
        shutil.rmtree(f"{pathClustersFold}")
        os.makedirs(f"{pathClustersFoldSeq}")
        
        with open(f"{pathClusters}/all_design_clustered.fa") as clus:
            seq_count = 0
            for line in clus:
                if ">" in line:
                    seq_count += 1                    
                    des_header = line.strip("\n").split(",")
                    des_header_pick = des_header[1].strip(" ").replace("=", "")
                    kinase_des_header = f">{seq_count}_{header}_{des_header_pick}"
                    kinase_des_header_filename = kinase_des_header.replace(">", "")
                elif not ">" in line:
                    print(f"{kinase_des_header_filename}\n")
                    sample = line.strip()
                    kinase_des_seq_dir = f"{pathClustersFoldSeq}/{kinase_des_header_filename}"
                    os.mkdir(f"{kinase_des_seq_dir}")
                    with open(f"{kinase_des_seq_dir}/{kinase_des_header_filename}.fasta", "w") as csf:
                        csf.write(f"{kinase_des_header}\n")
                        csf.write(f"{kinase_seq}:{sample}")
