#!/bin/bash
# This script is designed to run AlphaFold-Multimer (AF-Multimer) on a SLURM-based cluster.
# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name AF-multi

# Name of the SLURM partition that this job should run on.
#SBATCH -p GPUv100s                               
# Number of GPU cards
#SBATCH --gres=gpu:1
# Number of nodes required to run this job
#SBATCH -N 1

##SBATCH --ntasks-per-node 8

##SBATCH --cpus-per-task 32

# Memory (RAM) requirement/limit in MB.
#SBATCH --mem 380928                       # Memory Requirement (MB)

# Time limit for the job in the format Days-H:M:S
# A job that reaches its time limit will be cancelled.
# Specify an accurate time limit for efficient scheduling so your job runs promptly.
#SBATCH -t 3-23:45:00

# The standard output and errors from commands will be written to these files.
# %j in the filename will be replace with the job number when it is submitted.
#SBATCH -o job_%j.out
#SBATCH -e job_%j.err

# load the appropriate cuda module if using SLURM
module load cuda118/toolkit/11.8.0 cuda118/blas/11.8.0 cuda118/fft/11.8.0

# Colabfold path
export PATH="/PathTo/colabfold/localcolabfold/colabfold-conda/bin:$PATH"

export CUDA_VISIBLE_DEVICES=0,1

echo "Launched colabfold"
sleep 1

round=5

mkdir AFcomplex AFcomplex/top5complex

while [[ "$round" != 0 ]]
do

    mkdir AFcomplex/round_${round}
    seed=$((1000 + RANDOM %8999))
    fasta=$(ls *.fasta)
    fasta_base=$(basename ${fasta} ".fasta")

    colabfold_batch --num-recycle 10 --num-models 5 --random-seed "${seed}" --model-type auto --templates --amber --num-relax 3 --use-gpu-relax ${fasta} AFcomplex/round_${round}

    echo -e "\n Round $(( 6 - round)) completed...\n"
    sleep 1
    echo -e "\n Copying the top prediction for this round...\n"

    cp AFcomplex/round_${round}/${fasta_base}_relaxed_rank_001_*.pdb AFcomplex/top5complex

    round=$(( round - 1 ))
    
done

current_dir="$(pwd)"
current_line=$(basename "${current_dir}")
rm ../running_job_${current_line}.job || echo ""

echo -e "Predictions completed...\n"
