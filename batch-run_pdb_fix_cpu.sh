#!/bin/bash

line_num=0
starting=11
update_start="$starting"
ending=11
firstFour=8

while IFS= read -r line
do
    line_num=$(( line_num + 1 ))
    if [[ "$line" == "#"*"tid"* ]] ; then
        (( update_start++ ))
        echo -e " Skipping $line -- excluded...\n"
        sleep 1
        continue
    fi
    if (( "$line_num" < "$starting" )) ; then 
        printf "Skipping ${line_num} - ${line}... "
        continue
    elif (( "$line_num" > "$ending" ))
        then break
    elif (( "$line_num" >= "$starting" && "$line_num" <= "$ending" ))
        then
        set_dir="$(pwd)"
        parent_dir="${line}/AFcomplex"
        if (( "$firstFour" > 1 )) ; then
            if [[ -d "${parent_dir}/mpnn_out_clust_fold/af2_init_guess_in" ]]
                then rm -rf ${parent_dir}/mpnn_out_clust_fold/af2_init_guess_in/*
            elif [[ ! -d "${parent_dir}/mpnn_out_clust_fold/af2_init_guess_in" ]]
                then mkdir ${parent_dir}/mpnn_out_clust_fold/af2_init_guess_in
            fi
            \cp -f ./run_pdb_fix_cpu.sh "${parent_dir}/mpnn_out_clust_fold/"
            cd "${parent_dir}/mpnn_out_clust_fold/"
            touch running_job_${line}.job
            echo -e "Launching $line!"
            sleep 1

            sbatch run_pdb_fix_cpu.sh

            echo -e "Fixed ${line}: Kinase-pep $update_start of $ending \n"         

            cd "${set_dir}"
            touch running_job_${line}.job
            sleep 1

            round_=0
            while (( "$(ls running_job*.job | wc -l)" >= 11 ))
            do
                round_=$(( round_ + 1 ))
                if [[ "$round_" == 6 ]]
                then
                    printf "Waiting... "
                    round_=0
                fi
                sleep 20
            done            
            
            firstFour=$(( firstFour - 1 ))
            update_start=$(( update_start + 1 ))
            
        elif (( "$firstFour" < 2 ))
        then
            # echo -e "First job launched\n"
            sleep 3              

            if [[ -d "${parent_dir}/mpnn_out_clust_fold/af2_init_guess_in" ]]
                then rm -rf ${parent_dir}/mpnn_out_clust_fold/af2_init_guess_in/*
            elif [[ ! -d "${parent_dir}/mpnn_out_clust_fold/af2_init_guess_in" ]]
                then mkdir ${parent_dir}/mpnn_out_clust_fold/af2_init_guess_in
            fi            
            \cp -f ./run_pdb_fix_cpu.sh "${parent_dir}/mpnn_out_clust_fold/"
            cd "${parent_dir}/mpnn_out_clust_fold/"
            touch running_job_${line}.job
            echo -e "Launching $line!"
            sleep 1

            sbatch run_pdb_fix_cpu.sh

            echo -e "Fixing ${line}: Kinase-pep $update_start of $ending \n"         

            cd "${set_dir}"
            touch running_job_${line}.job
            sleep 1

            round_=0
            while (( "$(ls running_job*.job | wc -l)" >= 11 ))
            do
                round_=$(( round_ + 1 ))
                if [[ "$round_" == 6 ]]
                then
                    printf "Waiting... "
                    round_=0
                fi
                sleep 20
            done 
            update_start=$(( update_start + 1 ))
        fi
    fi
done < list_of_complexes_dark_confident_extra.dat