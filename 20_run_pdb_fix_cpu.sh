#!/bin/bash

# This is a SLURM batch script to fix PDB files for AlphaFold2 initial guess
# The script is submitted to the cluster using the SLURM `sbatch` command.
# Lines starting with # are comments, and will not be run.
# Lines starting with #SBATCH specify options for the scheduler.
# Lines that do not start with # or #SBATCH are commands that will run.

# Name for the job that will be visible in the job queue and accounting tools.
#SBATCH --job-name fix_pdb_cpu

#SBATCH -p 512GB
#SBATCH -N 1

#SBATCH --mem 501760      

# Time limit for the job in the format Days-H:M:S
# A job that reaches its time limit will be cancelled.
# Specify an accurate time limit for efficient scheduling so your job runs promptly.
#SBATCH -t 6-23:45:00

# The standard output and errors from commands will be written to these files.
# %j in the filename will be replace with the job number when it is submitted.
#SBATCH -o job_%j.out
#SBATCH -e job_%j.err


echo -e " Preparing input PDBs (fixing chain ids and residue numbering)\n"

sleep 1

cp ./structs/*.pdb ./af2_init_guess_in/

pushd af2_init_guess_in
pdb_counter=0
total_pdb="$(ls *.pdb | wc -l)"

for pdb in *.pdb
do
    #use pymol python here
    python \
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
rm ../../../${running_job_}
sleep 3