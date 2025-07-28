#!/bin/bash

# This file is batch script used to run commands on the BioHPC cluster.
# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name fix_pdb_cpu

# Name of the SLURM partition that this job should run on.
# SBATCH -p GPUA100                                # partition (queue)
# SBATCH -p GPU4A100
# SBATCH --gres=gpu:4
# SBATCH -p GPU4v100
# SBATCH --gres=gpu:4
# SBATCH -p GPUv100s
#SBATCH -p 256GB
# SBATCH --gres=gpu:1
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
#SBATCH --mail-user Abeeb.Yekeen@UTSouthwestern.edu

# module load
# module load cuda118/toolkit/11.8.0 cuda118/blas/11.8.0 cuda118/fft/11.8.0


# Colabfold path
# export PATH="/work/RADONC/s226058/wspace/vrk1/pep_des/colabfold/localcolabfold/colabfold-conda/bin:$PATH"

echo -e " Preparing input PDBs (fixing chain ids and residue numbering)\n"

sleep 1

cp ./top5complex/*.pdb ./af2_init_guess_in/

pushd af2_init_guess_in
pdb_counter=0
total_pdb="$(ls *.pdb | wc -l)"

for pdb in *.pdb
do
    /cm/shared/apps/pymol/2.5/bin/python \
    "/work/RADONC/s226058/wspace/proDesign/kinase_pep_design/format_chain_id_resn_biopython_pymol.py" \
    -i ${pdb} -o ${pdb}
    
    ((pdb_counter++))
    if (( $pdb_counter % 50 == 0 ))
    then
        echo -e "Processed $pdb successfully: $pdb_counter of ${total_pdb}\n"
    fi
done

echo -e "Processed $pdb successfully: $pdb_counter of ${total_pdb}\n"

popd

running_job_="$(ls running_job_*.job)"
rm ../${running_job_}
sleep 3