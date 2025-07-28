#!/bin/bash

# This file is batch script used to run commands on the BioHPC cluster.
# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name mpnn_des

# Name of the SLURM partition that this job should run on.
# SBATCH -p GPUA100                                # partition (queue)
#SBATCH -p GPUv100s  
# SBATCH -p GPU4A100
# SBATCH -p 384GB                                # partition (queue)
# SBATCH -p 512GB
# Number of GPU cards
#SBATCH --gres=gpu:1
# Number of nodes required to run this job
#SBATCH -N 1

##SBATCH --ntasks-per-node 8

##SBATCH --cpus-per-task 32

# Memory (RAM) requirement/limit in MB.
#SBATCH --mem 380928                       # Memory Requirement (MB)
# SBATCH --mem 501760      
# SBATCH --mem 761856                       # Memory Requirement (MB)


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
module load cuda112/toolkit/11.2.0 cuda112/blas/11.2.0 cuda112/fft/11.2.0

export CUDA_VISIBLE_DEVICES=0,1

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
# The 1st residue in the chain corresponds to 1 and not PDB residues index for now.
fixed_positions="4" #fixing/not designing residue 4 in chain B

python ${MPNN_PATH}/helper_scripts/parse_multiple_chains.py --input_path=$folder_with_pdbs --output_path=$path_for_parsed_chains

python ${MPNN_PATH}/helper_scripts/assign_fixed_chains.py --input_path=$path_for_parsed_chains --output_path=$path_for_assigned_chains --chain_list "$chains_to_design"

python ${MPNN_PATH}/helper_scripts/make_fixed_positions_dict.py --input_path=$path_for_parsed_chains --output_path=$path_for_fixed_positions --chain_list "$chains_to_design" --position_list "$fixed_positions"

python ${MPNN_PATH}/protein_mpnn_run.py \
        --jsonl_path $path_for_parsed_chains \
        --chain_id_jsonl $path_for_assigned_chains \
        --fixed_positions_jsonl $path_for_fixed_positions \
        --out_folder $output_dir \
        --num_seq_per_target 480 \
        --sampling_temp "0.1" \
        --batch_size 32

echo -e "Completed...\n"
