#!/bin/bash

# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name AF-multi_fold

#SBATCH -p GPU4v100
#SBATCH --gres=gpu:4
# Number of nodes required to run this job
#SBATCH -N 1

# Memory (RAM) requirement/limit in MB.
#SBATCH --mem 380928                       

# Time limit for the job in the format Days-H:M:S
# A job that reaches its time limit will be cancelled.
# Specify an accurate time limit for efficient scheduling so your job runs promptly.
#SBATCH -t 6-23:45:00

# The standard output and errors from commands will be written to these files.
# %j in the filename will be replace with the job number when it is submitted.
#SBATCH -o job_%j.out
#SBATCH -e job_%j.err

# module load
module load cuda118/toolkit/11.8.0 cuda118/blas/11.8.0 cuda118/fft/11.8.0

# Colabfold path
export PATH="/path_to/colabfold/localcolabfold/colabfold-conda/bin:$PATH"

total_des="$(ls -d *_sample* | wc -l)"
current_des=0
max_parallel_jobs=4
declare -A gpu_jobs=()  # array to track GPU and job PID

# Function to find an available GPU
find_available_gpu() {
    for gpu in $(seq 0 $((max_parallel_jobs - 1))); do
        if [[ -z ${gpu_jobs[$gpu]} ]]; then
            echo $gpu
            return
        fi
    done
}

# Function to launch colabfold
launch_task() {
    local des="$1"
    local gpu_id=$(find_available_gpu)
    pushd "${des}"
   
    if [[ -f "${des}.done.txt" ]]
    then
        echo -e "${des} is done, skipping..."
        ((current_des++))
        popd
        continue
    fi

    local seed=$((1000 + RANDOM % 8999))
    local fasta=$(ls *.fasta)

    CUDA_VISIBLE_DEVICES=$gpu_id colabfold_batch --num-recycle 2 --num-models 2 --random-seed "${seed}" \
    --model-type auto --templates ${fasta} . &

    # save PID of the background job with the GPU ID
    gpu_jobs[$gpu_id]=$!
    ((current_des++))

    echo -e "Launching ${des}..."
    popd
}

# Function to check for completed jobs
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
            echo -e "One Job finished: $current_des of $total_des..."
            unset gpu_jobs[$gpu]
        fi
    done
}

for des in *_sample*
do

    rounds_=0
    # Wait if maximum number of parallel jobs are running
    while [ ${#gpu_jobs[@]} -ge $max_parallel_jobs ]; do
        check_completed_jobs
        ((rounds_++))
        sleep 30
    done

    # Launch colabfold in the background
    launch_task "${des}"
done

wait
echo -e " Colabfold jobs completed" ; sleep 1
echo -e " Copying the top predictions...\n" ; sleep 1

for des in *_sample*
do
    pushd "${des}"

    if [[ -f "${des}.done.txt" ]]
    then
        fasta=$(ls *.fasta)
        fasta_base=$(basename "${fasta}" ".fasta")
        \cp -f ${fasta_base}_unrelaxed_rank_001_*.pdb ../../structs
    fi

    popd 
done

gpu4v100running_job="$(ls gpu4v100running_job*.job)"
rm ../../../../${gpu4v100running_job} || echo ""

echo -e "All designs for the current set completed\n"
sleep 1