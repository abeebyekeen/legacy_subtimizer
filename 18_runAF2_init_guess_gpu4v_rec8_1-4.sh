#!/bin/bash

# This is a SLURM batch script to run multiple instances of AlphaFold2 with an initial guess
# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name AF2ini_guess

#SBATCH -p GPU4v100
# Number of GPU cards
#SBATCH --gres=gpu:4
# Number of nodes required to run this job
#SBATCH -N 1

#SBATCH --mem 371552

# Time limit for the job in the format Days-H:M:S
# A job that reaches its time limit will be cancelled.
# Specify an accurate time limit for efficient scheduling so your job runs promptly.
#SBATCH -t 6-23:45:00

# The standard output and errors from commands will be written to these files.
# %j in the filename will be replace with the job number when it is submitted.
#SBATCH -o job_%j.out
#SBATCH -e job_%j.err


# Activate environment

# conda activate af2_des
# sleep 3

# module load
module load cuda121/toolkit/12.1.0

line_num=0
starting=1
update_start="$starting"
current_des="$starting"
ending=4
# firstFour=1
max_parallel_jobs=4
declare -A gpu_jobs=()  # Associative array to track GPU and job PID

# Function to find an available GPU
find_available_gpu() {
    for gpu in $(seq 0 $((max_parallel_jobs - 1))); do
        if [[ -z ${gpu_jobs[$gpu]} ]]; then
            echo $gpu
            return
        fi
    done
}

# Function to launch job
launch_task() {
    local des="$1"
    local gpu_id=$(find_available_gpu)
    # pushd "${des}"

    CUDA_VISIBLE_DEVICES=$gpu_id \
    /work/RADONC/s226058/wspace/vrk1/pep_des/dl_binder_design/af2_initial_guess/predict.py \
    -pdbdir ../af2_init_guess_in -outpdbdir ../af2_init_guess_out.rec8 \
    -scorefilename af2score.dat -recycle 8 &

    # Save the PID of the background job with the GPU ID
    gpu_jobs[$gpu_id]=$!
    
    echo -e "Launched ${des}: Kinase-pep $update_start of $ending...\n"
    sleep 2
}


# Function to check for completed jobs
check_completed_jobs() {
    if (( rounds_ == 8 ))
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
            ((current_des++))
            unset gpu_jobs[$gpu]
        fi
    done
}

# Start run
while IFS= read -r line
do
    line_num=$(( line_num + 1 ))
    if [[ "$line" == "#"*"tid"* ]] && (( "$line_num" < "$starting" )) ; then
        echo -e " Skipping $line -- excluded...\n"
        sleep 1 ; continue
    fi
    if [[ "$line" == "#"*"tid"* ]] && (( "$line_num" >= "$starting" )) ; then
        ((current_des++))
        (( update_start++))
        echo -e " Skipping $line -- excluded...\n"
        sleep 1 ; continue
    fi
    if (( "$line_num" < "$starting" )) ; then
        printf "Skipping ${line_num} - ${line}... "
        continue
    elif (( "$line_num" > "$ending" )) ; then break
    elif (( "$line_num" >= "$starting" && "$line_num" <= "$ending" )) ; then
        home_direct="$(pwd)"
        set_dir="/work/RADONC/s226058/wspace/proDesign/kinase_pep_design/YST_fixed_dark_fam/confident_AFMcomplexes"
        cd "${set_dir}"
        parent_dir="${set_dir}/${line}/AFcomplex/mpnn_out_clust_fold"
        
        if [[ -d "${parent_dir}/af2_init_guess.rec8" ]] ; then
            rm -r ${parent_dir}/af2_init_guess.rec8
            mkdir ${parent_dir}/af2_init_guess.rec8
        elif [[ ! -d "${parent_dir}/af2_init_guess" ]] ; then
            mkdir ${parent_dir}/af2_init_guess.rec8
        fi

        cd "${parent_dir}/af2_init_guess.rec8"
        # touch running_job_${line}.job
        echo -e "Launching $line!\n"
        sleep 1

        if [[ -d "${parent_dir}/af2_init_guess_out.rec8" ]] ; then
            rm -r "${parent_dir}/af2_init_guess_out.rec8"
            mkdir "${parent_dir}/af2_init_guess_out.rec8"
        elif [[ ! -d "${parent_dir}/af2_init_guess_out" ]] ; then
            mkdir "${parent_dir}/af2_init_guess_out.rec8"
        fi

        rounds_=0
        # Wait if maximum number of parallel jobs are running
        while [ ${#gpu_jobs[@]} -ge $max_parallel_jobs ]; do
            check_completed_jobs
            ((rounds_++))
            sleep 15
        done

        # Launch colabfold in the background
        launch_task "${line}"
        cd "${home_direct}"

        update_start=$(( update_start + 1 ))
    fi

done < ../list_of_complexes_dark_confident.dat

wait

echo -e "All jobs completed...\n"
sleep 1