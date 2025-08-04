#! /bin/bash

for filefolder in *tide
do
    fasta_dir="$filefolder/AFcomplex/mpnn_out/seqs"
    if [[ -d "$fasta_dir" ]]
    then
        pushd "$fasta_dir"
        rm all_design.fa
        echo -e "Processing sequences for ${filefolder}\n"
        touch all_designs.temp
        for fasta in *.fa
        do
            awk 'NR > 2 {print}' "$fasta" >> all_designs.temp
        done
        mv all_designs.temp all_design.fa

        echo -e "Preparing Seq Logo for ${filefolder}\n\n"
        weblogo -f all_design.fa -D fasta -o ${filefolder}_seqlogo.png -F png_print -A 'protein' \
        -s large --errorbars NO --color-scheme chemistry --logo-font Arial-BoldMT -U probability 

        popd
    fi
done