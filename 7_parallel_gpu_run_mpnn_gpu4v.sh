#!/bin/bash

# This script is designed to run multiple instances of the ProteinMPNN in parallel on a GPU cluster using SLURM.
# It reads a list of complexes from a file, launches MPNN for each complex,
# and manages the GPU resources to ensure that a maximum number of jobs run in parallel.
# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name mpnn_des_parallel

# Name of the SLURM partition that this job should run on.
#SBATCH -p GPU4v100
#SBATCH --gres=gpu:4
# Number of nodes required to run this job
#SBATCH -N 1

# Memory (RAM) requirement/limit in MB.
#SBATCH --mem 371552

# Time limit for the job in the format Days-H:M:S
# A job that reaches its time limit will be cancelled.
# Specify an accurate time limit for efficient scheduling so your job runs promptly.
#SBATCH -t 6-23:45:00

# The standard output and errors from commands will be written to these files.
# %j in the filename will be replace with the job number when it is submitted.
#SBATCH -o job_%j.out
#SBATCH -e job_%j.err

# Send an email when the job status changes, to the specfied address.
#SBATCH --mail-type FAIL
#SBATCH --mail-user Your.Email@Email.Address.com


# load the appropriate cuda module if using SLURM
module load cuda121/toolkit/12.1.0

line_num=0
starting=1
current_des="$starting"
ending=4 # the ending number to the last complex to process


max_parallel_jobs=4
declare -A gpu_jobs=()  # array to track GPU and job PID

# find available GPU
find_available_gpu() {
    for gpu in $(seq 0 $((max_parallel_jobs - 1))); do
        if [[ -z ${gpu_jobs[$gpu]} ]]; then
            echo $gpu
            return
        fi
    done
}

# launch mpnn
launch_task() {
    local des="$1"
    local gpu_id=$(find_available_gpu)
    # pushd "${des}"
    folder_with_pdbs="../top5complex/"

    output_dir="../mpnn_out"
    if [ ! -d $output_dir ]
    then
        mkdir -p $output_dir
    fi

    path_for_parsed_chains=$output_dir"/parsed_pdbs.jsonl"
    path_for_assigned_chains=$output_dir"/assigned_pdbs.jsonl"
    path_for_fixed_positions=$output_dir"/fixed_pdbs.jsonl"
    chains_to_design="B"
    fixed_positions=$(grep 'fixed_positions=' fixed_positions.dat | sed 's/fixed_positions=//g' | tr -d '"')

    python ${MPNN_PATH}/helper_scripts/parse_multiple_chains.py --input_path=$folder_with_pdbs --output_path=$path_for_parsed_chains

    python ${MPNN_PATH}/helper_scripts/assign_fixed_chains.py --input_path=$path_for_parsed_chains --output_path=$path_for_assigned_chains --chain_list "$chains_to_design"

    python ${MPNN_PATH}/helper_scripts/make_fixed_positions_dict.py --input_path=$path_for_parsed_chains --output_path=$path_for_fixed_positions --chain_list "$chains_to_design" --position_list "$fixed_positions"

    CUDA_VISIBLE_DEVICES=$gpu_id \
    python ${MPNN_PATH}/protein_mpnn_run.py \
            --jsonl_path $path_for_parsed_chains \
            --chain_id_jsonl $path_for_assigned_chains \
            --fixed_positions_jsonl $path_for_fixed_positions \
            --out_folder $output_dir \
            --num_seq_per_target 480 \
            --sampling_temp "0.1" \
            --batch_size 32 &

    # save PID of the bg job with the GPU ID
    gpu_jobs[$gpu_id]=$!
    ((current_des++))

    echo -e "Launched ${des}: ${current_des} of ${ending}...\n"
    sleep 1
}


# Function to check for completed jobs
check_completed_jobs() {
    if (( rounds_ == 6 ))
    then
        printf "Waiting...\n"
        rounds_=0
    fi

    for gpu in "${!gpu_jobs[@]}"
    do
        local pid=${gpu_jobs[$gpu]}
        if ! kill -0 $pid 2>/dev/null; then
            # Job is finished, remove its PID and free up the GPU
            echo -e "One job finished: $current_des of $ending..."
            unset gpu_jobs[$gpu]
        fi
    done
}

# start run
while IFS= read -r line
do
    line_num=$(( line_num + 1 ))
    if [[ "$line" == "#"*"tid"* ]] ; then
        ((current_des++))
        # (( update_start++))
        echo -e " Skipping $line -- excluded...\n"
        sleep 1
        continue
    fi    
    if (( "$line_num" < "$starting" )) ; then
        printf "Skipping ${line_num} - ${line}... "
        continue
    elif (( "$line_num" > "$ending" )) ; then break
    elif (( "$line_num" >= "$starting" )) ; then
        home_direct="$(pwd)"
        design_dir="${line}/AFcomplex/mpnn_des"
        pushd "${design_dir}"

        echo -e "Launching $line!\n"
        sleep 1

        rounds_=0
        # Wait if maximum number of parallel jobs are running
        while [ ${#gpu_jobs[@]} -ge $max_parallel_jobs ]; do
            check_completed_jobs
            ((rounds_++))
            sleep 10
        done

        # Launch mpnnn in the background
        launch_task "${line}"
        # while [[ ! -d "mpnn_out/seqs" ]]
        # do sleep 20
        # done

        # echo -e "Output sequence directory created\n"
        # sleep 1

        popd "${home_direct}"
 
        # while (( "$(ls mpnn_out/seqs/*.fa | wc -l)" < 4 ))
        # do sleep 20
        # done
        
    fi
done < example_list_of_complexes.dat

wait

echo -e "All jobs completed...\n"
sleep 1