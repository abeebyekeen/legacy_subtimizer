#!/bin/bash

# This file is batch script used to run commands on the BioHPC cluster.
# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name AF-multi_fold

# Name of the SLURM partition that this job should run on.
# SBATCH -p GPUA100                                # partition (queue)
# SBATCH -p GPU4A100
# SBATCH --gres=gpu:4
# SBATCH -p GPU4v100
# SBATCH --gres=gpu:4
# SBATCH -p GPUv100s
#SBATCH -p GPUp100
#SBATCH --gres=gpu:2
# SBATCH -p 384GB                               
# SBATCH -p 512GB
# Number of GPU cards
# SBATCH --gres=gpu:4
# Number of nodes required to run this job
#SBATCH -N 1

##SBATCH --ntasks-per-node 8

##SBATCH --cpus-per-task 32

# Memory (RAM) requirement/limit in MB.
# SBATCH --mem 380928                       
# SBATCH --mem 501760      
# SBATCH --mem 761856                       
#SBATCH --mem 252928

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
module load cuda118/toolkit/11.8.0 cuda118/blas/11.8.0 cuda118/fft/11.8.0

# Colabfold path
export PATH="/PathTo/colabfold/localcolabfold/colabfold-conda/bin:$PATH"

# total_des="$(ls -d *_sample* | wc -l)"
line_num=0
starting=1
ending=4
current_des=0
max_parallel_jobs=2
declare -A gpu_jobs=()  # Associative array to track GPU and job PID

# find an available GPU
find_available_gpu() {
    for gpu in $(seq 0 $((max_parallel_jobs - 1))); do
        if [[ -z ${gpu_jobs[$gpu]} ]]; then
            echo $gpu
            return
        fi
    done
}

# launch colabfold
launch_task() {
    local des="$1"
    local gpu_id=$(find_available_gpu)
    pushd "${des}"
    round=5

    mkdir AFcomplex AFcomplex/top5complex

    while [[ "$round" != 0 ]]
    do
        mkdir AFcomplex/round_${round}
        local seed=$((1000 + RANDOM %8999))
        local fasta=$(ls *.fasta)

        CUDA_VISIBLE_DEVICES=$gpu_id colabfold_batch --num-recycle 10 --num-models 5 --random-seed "${seed}" \
        --model-type auto --templates --amber --num-relax 3 --use-gpu-relax ${fasta} AFcomplex/round_${round} &

        # Save the PID of the background job with the GPU ID
        gpu_jobs[$gpu_id]=$!
        ((current_des++))

        echo -e "Launching ${des}-- round $(( 6 - round))..."
        round=$(( round - 1 ))
        popd
    done
}

# check for completed jobs
check_completed_jobs() {
    if ((rounds_ == 2))
    then
        printf "Waiting...\n"
        rounds_=0
    fi

    for gpu in "${!gpu_jobs[@]}"
    do
        local pid=${gpu_jobs[$gpu]}
        if ! kill -0 $pid 2>/dev/null; then
            # Job is finished, remove its PID and free up the GPU
            echo -e "One Job finished: $current_des of $ending..."
            unset gpu_jobs[$gpu]
        fi
    done
}

while IFS= read -r des
do
    line_num=$(( line_num + 1 ))
    if (( "$line_num" < "$starting" ))
        then 
            printf "Skipping ${line_num} - ${des}... "
            continue
    elif (( "$line_num" > "$ending" ))
        then break                
    elif (( "$line_num" >= "$starting" && "$line_num" <= "$ending" ))
        then
        rounds_=0
        while [ ${#gpu_jobs[@]} -ge $max_parallel_jobs ]
        do
            check_completed_jobs
            ((rounds_++))
            sleep 30
        done        
        # Launch colabfold in the background
        launch_task "${des}"
    fi

done < example_list_of_complexes.dat

wait
echo -e " Colabfold p100 jobs completed" ; sleep 1
echo -e " Copying the top predictions...\n" ; sleep 1

while IFS= read -r des
do
    pushd "${des}"
    fasta=$(ls *.fasta)
    fasta_base=$(basename "${fasta}" ".fasta")

    cd AFcomplex

    for desround in round_*
    do     
        \cp -f ${desround}/${fasta_base}_relaxed_rank_001_*.pdb top5complex
    done

    cd ..
    popd 
done < example_list_of_complexes.dat

echo -e "All designs for the current set completed\n"
sleep 1