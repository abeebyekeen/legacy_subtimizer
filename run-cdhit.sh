#!/bin/bash

# This file is batch script used to run commands on the BioHPC cluster.
# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name run-cdhit

# Name of the SLURM partition that this job should run on.
# SBATCH -p GPUA100                                # partition (queue)
# SBATCH -p GPU4A100
# SBATCH -p 384GB                                # partition (queue)
# SBATCH -p 512GB
# SBATCH -p 256GBv1
# SBATCH -p GPU
#SBATCH -p GPUp4
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
# SBATCH --mem 252928
# SBATCH --mem 254976

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
#SBATCH --mail-user Abeeb.Yekeen@UTSouthwestern.edu

# module load
# module load cuda11/blas/11.1.0 cuda11/fft/11.1.0 cuda11/toolkit/11.1.0
# module load cuda112/toolkit/11.2.0 cuda112/blas/11.2.0 cuda112/fft/11.2.0

# export CUDA_VISIBLE_DEVICES=0,1

# input_fas="/work/RADONC/s226058/wspace/proDesign/kinase_pep_design/YST_fixed/AKT1_1akt1tide/AFcomplex/mpnn_out/seqs/all_design.fa"

# out_clusters="/work/RADONC/s226058/wspace/proDesign/kinase_pep_design/YST_fixed/AKT1_1akt1tide/AFcomplex/mpnn_out_clust/all_design_clustered.fa"

# log_file="/work/RADONC/s226058/wspace/proDesign/kinase_pep_design/YST_fixed/AKT1_1akt1tide/AFcomplex/mpnn_out_clust/log.log"

module load cd-hit/4.6.4

cd-hit -i all_design.fa -o all_design_clustered.fa -c 1.0 -M 32000 -T 0 -l 5 > log.log