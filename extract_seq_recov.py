import os
import sys

folders = [f for f in os.listdir() if \
           (os.path.isdir(f) and "tide" in f)]

for folder in folders:
    designs = f"{folder}/AFcomplex/mpnn_out/seqs/all_design.fa"
    seq_rec = f"{folder}/AFcomplex/mpnn_out/seqs/sec_recovery.dat"
    try:
        with open(seq_rec, "w") as dataout:
            with open(designs) as datain:
                print(f"Processing {seq_rec}\n")
                for line in datain:
                    if "=" in line:
                        recdata = line.strip().split("=")
                        recdata = recdata[-1]
                        dataout.write(f"{recdata}\n")
    except FileNotFoundError:
        print(f"{seq_rec} does not exist!")
        sys.exit(1)
sys.exit(0)
