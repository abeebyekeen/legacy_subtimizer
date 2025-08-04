#!/bin/bash

# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name AF-multi_fold

# Name of the SLURM partition that this job should run on.
#SBATCH -p GPUv100s
# Number of GPU cards
#SBATCH --gres=gpu:1
# Number of nodes required to run this job
#SBATCH -N 1

# Memory (RAM) requirement/limit in MB.
#SBATCH --mem 380928                       # Memory Requirement (MB)

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
export PATH="/work/RADONC/s226058/wspace/vrk1/pep_des/colabfold/localcolabfold/colabfold-conda/bin:$PATH"

export CUDA_VISIBLE_DEVICES=0,1

echo "Launched colabfold"

# mkdir AFcomplex AFcomplex/top5complex

total_des="$(ls -d *_sample* | wc -l)"
current_des=0

for des in *_sample*
do
    pushd "${des}"

    if [[ -f *"_sample"*"_pae.png" ]] && [[ -f *"_sample"*"_plddt.png" ]] && \
    [[ -f *"_sample"*"_coverage.png" ]] && [[ -f *"_sample"*".done.txt" ]]
    then
        printf "Done. "
        continue
    fi

    seed=$((1000 + RANDOM %8999))
    fasta=$(ls *.fasta)
    fasta_base=$(basename ${fasta} ".fasta")

    colabfold_batch --num-recycle 2 --num-models 2 --random-seed "${seed}" \
    --model-type auto --templates ${fasta} .

    current_des=$(( current_des + 1 ))
    echo -e "\n Folding of ${des} completed: $current_des of $total_des"
    echo -e "\n Copying the top prediction...\n"

    cp ${fasta_base}_unrelaxed_rank_001_*.pdb ../../structs

    popd

done

v100running_job_="$(ls v100running_job_*.job)"
rm ../../../../${v100running_job_}

echo -e "All designs for the current set completed\n"
sleep 1