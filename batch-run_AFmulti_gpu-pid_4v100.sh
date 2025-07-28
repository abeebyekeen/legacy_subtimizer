#!/bin/bash

line_num=0
design_count=0
starting=2
update_start="$starting"
ending=11
firstFour=1

while IFS= read -r line
do
    line_num=$(( line_num + 1 ))
    if (( "$line_num" < "$starting" ))
        then 
            printf "Skipping ${line_num} - ${line}... "
            continue
    elif (( "$line_num" > "$ending" ))
        then break
    elif [[ "$line" == "#"*"tide" ]]
        then
        update_start=$(( update_start + 1 ))
        continue
    elif (( "$line_num" >= "$starting" && "$line_num" <= "$ending" ))
        then
        set_dir="$(pwd)"
        parent_dir="${line}/AFcomplex"
        if (( "$firstFour" >= 1 ))
        then
            mkdir -p ${parent_dir}/mpnn_out_clust_fold/structs
            \cp -f ./runAFm_fold_gpu-pid_4v100.sh "${parent_dir}/mpnn_out_clust_fold/seqs/"
            cd "${parent_dir}/mpnn_out_clust_fold/seqs"
            touch gpu4v100running_job_${line}.job
            echo -e "Launching $line!"
            sleep 1

            sbatch runAFm_fold_gpu-pid_4v100.sh

            design_count=$(( design_count + 1 ))
            echo -e "Folding ${line}: Kinase-pep $update_start of $ending \n"         

            cd "${set_dir}"
            touch gpu4v100running_job_${line}.job

            round_=0
            
            while (( "$(ls gpu4v100running_job*.job | wc -l)" >= 4 ))
            do
                round_=$(( round_ + 1 ))
                if [[ "$round_" == 4 ]]
                then
                    printf "Waiting. "
                    round_=0
                fi
                sleep 15
            done 
            
            firstFour=$(( firstFour - 1 ))
            update_start=$(( update_start + 1 ))
            
        elif (( "$firstFour" < 1 ))
        then
            # echo -e "First job launched\n"
            # sleep 2
            mkdir -p ${parent_dir}/mpnn_out_clust_fold/structs
            \cp -f ./runAFm_fold_gpu-pid_4v100.sh "${parent_dir}/mpnn_out_clust_fold/seqs/"
            cd "${parent_dir}/mpnn_out_clust_fold/seqs"
            touch gpu4v100running_job_${line}.job
            sbatch runAFm_fold_gpu-pid_4v100.sh

            design_count=$(( design_count + 1 ))
            echo -e "Folding ${line}: Kinase-pep $update_start of $ending \n"
            
            cd "$set_dir"
            touch gpu4v100running_job_${line}.job

            round_=0
            while (( "$(ls gpu4v100running_job*.job | wc -l)" >= 4 ))
            do
                round_=$(( round_ + 1 ))
                if [[ "$round_" == 4 ]]
                then
                    printf "Waiting... "
                    round_=0
                fi
                sleep 15
            done
            update_start=$(( update_start + 1 ))
        fi
    fi
done < list_of_complexes_dark_confident_extra.dat
