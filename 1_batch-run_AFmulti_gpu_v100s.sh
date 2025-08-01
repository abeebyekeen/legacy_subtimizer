#!/bin/bash

line_num=0
design_count=0
starting=1
update_start="$starting"
ending=4
firstBatch=2

while IFS= read -r line
do
    line_num=$(( line_num + 1 ))
    if (( "$line_num" < "$starting" ))
        then 
            printf "Skipping ${line_num} - ${line}... "
            continue
    elif (( "$line_num" > "$ending" ))
        then break
    elif (( "$line_num" >= "$starting" && "$line_num" <= "$ending" ))
        then
        set_dir="$(pwd)"
        parent_dir="${line}"
        fasta=$(ls ${parent_dir}/*.fasta)
        fasta_base=$(basename ${fasta} ".fasta")

        if [[ -f "${parent_dir}/AFcomplex/round_1/${fasta_base}.done.txt" ]]
        then
            echo -e "${line} is done, skipping..."
            continue
        fi
        if (( "$firstBatch" >= 1  && "$(ls running_job*.job | wc -l)" >= 4 ))
        then
            while (( "$(ls running_job*.job | wc -l)" >= 4 ))
            do
                round_=$(( round_ + 1 ))
                if [[ "$round_" == 3 ]]
                then
                    printf "Waiting... "
                    round_=0
                fi
                sleep 15
            done
        fi
        if (( "$firstBatch" >= 1  && "$(ls running_job*.job | wc -l)" < 4 ))
        then
            if [[ -f "${parent_dir}/runAFmulti_gpu-v100s.sh" ]]
            then
                rm ${parent_dir}/runAFmulti_gpu-v100s.sh
            fi
            \cp -f ./runAFmulti_gpu-v100s.sh "${parent_dir}"
            cd "${parent_dir}"
            
            echo -e "Launching $line!"
            sleep 1

            sbatch runAFmulti_gpu-v100s.sh

            touch ../running_job_${line}.job

            design_count=$(( design_count + 1 ))
            echo -e "Folding ${line}: Kinase-pep $update_start of $ending \n"

            cd "${set_dir}"
            
            round_=0

            sleep 2
            
            while (( "$(ls running_job*.job | wc -l)" > 3 ))
            do
                round_=$(( round_ + 1 ))
                if [[ "$round_" == 3 ]]
                then
                    printf "Waiting. "
                    round_=0
                fi
                sleep 10
            done
            
            firstBatch=$(( firstBatch - 1 ))
            update_start=$(( update_start + 1 ))
            
        elif (( "$firstBatch" < 1 && "$(ls running_job*.job | wc -l)" < 4 ))
        then
            # echo -e "First job launched\n"
            sleep 1
            if [[ -f "${parent_dir}/runAFmulti_gpu-v100s.sh" ]]
            then
                rm ${parent_dir}/runAFmulti_gpu-v100s.sh
            fi
            \cp -f ./runAFmulti_gpu-v100s.sh "${parent_dir}"
            cd "${parent_dir}"
            echo -e "Launching $line!"
            sleep 1

            sbatch runAFmulti_gpu-v100s.sh
            
            touch ../running_job_${line}.job

            design_count=$(( design_count + 1 ))
            echo -e "Folding ${line}: Kinase-pep $update_start of $ending \n"

            cd "${set_dir}"

            round_=0

            sleep 2

            while (( "$(ls running_job*.job | wc -l)" >= 4 ))
            do
                round_=$(( round_ + 1 ))
                if [[ "$round_" == 3 ]]
                then
                    printf "Waiting... "
                    round_=0
                fi
                sleep 10
            done
            update_start=$(( update_start + 1 ))
        fi
    fi
done < example_list_of_complexes.dat