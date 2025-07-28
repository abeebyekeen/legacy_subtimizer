#!/bin/bash

line_num=0
design_count=0
starting=18
update_start="$starting"
ending=41
while IFS= read -r line
do
    line_num=$(( line_num + 1 ))
    if (( "$line_num" < "$starting" ))
        then continue
    elif (( "$line_num" > "$ending" ))
        then break
    elif (( "$line_num" >= "$starting" && "$line_num" <= "$ending" ))
        then
        parent_dir="${line}/AFcomplex"
        rm -rf ${parent_dir}/mpnn_out_clust && mkdir ${parent_dir}/mpnn_out_clust
        \cp ${parent_dir}/mpnn_out/seqs/all_design.fa ${parent_dir}/mpnn_out_clust/
        \cp ./run-cdhit.sh ${parent_dir}/mpnn_out_clust/
        pushd "${parent_dir}/mpnn_out_clust"
        sbatch run-cdhit.sh
        design_count=$(( design_count + 1 ))
        echo -e "Clustering ${line}: Design $update_start of $ending \n"
        sleep 1
        
        if (( "$design_count" >= 4 ))
            then sleep 20
            design_count=0
        fi
            
        echo -e "${line} clustered"
        sleep 1
        popd
        update_start=$(( update_start + 1 ))
    fi
done < example_list_of_complexes.dat