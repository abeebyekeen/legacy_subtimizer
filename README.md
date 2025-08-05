## Subtimizer: A Computational Workflow for Structure-Guided Design of Potent and Selective Kinase Peptide Substrates

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/abeebyekeen/subtimizer?style=flat-square)](https://github.com/abeebyekeen/subtimizer/releases)
[![DOI](https://zenodo.org/badge/doi/10.1101/2025.07.04.663216.svg?style=svg)](http://dx.doi.org/10.1101/2025.07.04.663216)

### Contents

0. [Contents](#contents)
1. [Prerequisites/Requirements](#prerequisites)
2. [Clone Subtimizer](#clone-subtimizer)
3. [Set Up Environments](#set-up-environments)
4. [Usage](#usage)
5. [Updating the Code](#6-updating-the-code)
6. [Citation](#7-citation)

---

### Prerequisites

1. [Install Anaconda or Miniconda](https://www.anaconda.com/products/distribution) or [Mamba](https://mamba.readthedocs.io)
2. [Install ColabFold](https://github.com/YoshitakaMo/localcolabfold)
3. [Install ProteinMPNN](https://github.com/dauparas/ProteinMPNN)
4. [Get the af2_initial_guess code](https://github.com/nrbennet/dl_binder_design)

---

### Clone Subtimizer

```bash
git clone https://github.com/abeebyekeen/subtimizer.git
cd subtimizer
```

---

### Set up environments

```bash
conda env create -f af2_des_env.yaml
conda env create -f mpnn_des_env.yaml
```

---

### Usage

#### Step 1: Prepare list of complexes
```bash
echo -e "AKT1_2akt1tide\nALK_axltide\nEGFRm_1csktide\nSGK1_1akt1tide" > example_list_of_complexes.dat
```

#### Step 2: Set up folder structure
```bash
python 0_setup_KinasePep_folders.py --file example_list_of_complexes.dat
```

#### Step 3: Run AF-Multimer

##### Option A: Batch jobs with SLURM
```bash
bash 1_batch-run_AFmulti_gpu_v100s.sh
```
> In the `1_batch-run_AFmulti_gpu.sh` script, the following are the variables you may want to change:
>* starting = which complex in the list to start processing from.
>* ending = which complex in the list to end at.

> The script above calls and launches (sbatch) the job script `2_runAFmulti_gpu_v100s.sh`.

> In the `2_runAFmulti_gpu_v100s.sh` script, you can set the number of AF-Multimer rounds to run by changing the `rounds` variable.

##### Option B: Parallel jobs (with multiple GPUs)
```bash
sbatch 3_runAFmulti_parallel_gpu-pid_p100.sh
```
> Edit `max_parallel_jobs` based on available GPUs

#### Step 4: Set up directory for ProteinMPNN
```bash
python 4_setup_proteinmpnn_folders.py --file example_list_of_complexes.dat
```

Copy `6_run-mpnn.sh` into the mpnn_des folder.
Edit `6_run-mpnn.sh`:
- `chains_to_design` (the chain(s) to design)
- `fixed_positions` (residues to fix in the chain)

#### Step 5: Run ProteinMPNN
Change to mpnn_des environment
```bash
conda activate mpnn_des
```

While in the working directory, run:
```bash
bash 5_batch-run_mpnn.sh
# or
bash 7_parallel_gpu_run_mpnn_gpu4v.sh
```

#### Step 6: Combine designed sequences and plot sequence logos
```bash
bash 8_combine_fasta_and_plot_logo.sh
```

#### Step 7: Extract and plot sequence recovery information
```bash
python 9_extract_seq_recov.py
python 10_stripplot_seqrec_csvOUT_opt.py
```

#### Step 8: Cluster designed sequences with CD-Hit
```bash
bash 11_batch-run_cdhit.sh
# (calls 12_run-cdhit.sh)
```

#### Step 9: Summarize clusters
```bash
bash 13_get_cluster_summary.sh
```

#### Step 10: Prepare kinase-peptide (designed) for folding
```bash
python 14_prepare_kinase-pep_for_AFm-fold.py
```

#### Step 11: Fold designed sequences with AF-Multimer

>Note: The version of proteinMPNN used in this work does not generate pdbs. Hence the need for post-design folding. 

>However, with the [newer version (and LigandMPNN)](https://github.com/dauparas/LigandMPNN) which generates structures of designed sequences, this step may not be necessary.

Change to af2_des environment

```bash
conda activate af2_des
```

##### Option A: Batch SLURM
```bash
bash 15_batch-run_AFmulti_fold_gpu_v100s.sh
# (calls 16_runAFm_fold_gpu_v100s.sh)
```

##### Option B: Parallel jobs
```bash
sbatch 17_batch-run_AFmulti_gpu-pid_4v100.sh
# (calls 18_runAFm_fold_gpu_4v100.sh)
```

#### Step 12: Prepare PDBs for af2_init_guess

>Note: af2_init guess has two requirements for the input pdb
    * the binder (substrate) has to be the first chain
    * no overlapping residue numbers between chains 

```bash
bash 19_batch-run_pdb_fix_cpu.sh
# (20_calls run_pdb_fix_cpu.sh)
```

#### Step 13: Set up `af2_init_guess` folder
```bash
mkdir af2_init_guess && cd af2_init_guess
cp ../21_runAF2_init_guess_gpu4v_rec8.sh .
cp ../22_plot_swarm_pae-inter_CSVout_with_oriSub.py .
```

> Update the path to `dl_binder_design/af2_initial_guess/predict.py` in `21_runAF2_init_guess_gpu4v_rec8.sh`

#### Step 14: Run af2_init_guess
```bash
sbatch 21_runAF2_init_guess_gpu4v_rec8.sh
```

#### Step 15: Extract and merge results
```bash
cd ../
python extract_merge_af2_init_guess_with_folding_data_rec8.py
python add_ptm-iptm_column_to_merged_data_rec8.py
```



#### Step 16: Compare with original (parent) peptides

```bash
bash setup_original_subs_folder.sh
cd original_subs/
bash batch-run_pdb_fix_cpu_orig.sh
mkdir af2_init_guess && cd af2_init_guess
cp ../runAF2_init_guess_gpu4v_rec8_originalSub.sh .
sbatch runAF2_init_guess_gpu4v_rec8_originalSub.sh
```

Then:
```bash
cd ../
python extract_merge_af2_init_guess_with_folding_data_rec8_oriSub.py
python add_ptm-iptm_column_to_merged_data_rec8_oriSub.py
```



#### Step 17: Merge all data
```bash
python merge_test_subs_data_with_orig_subs.py
python extract_add_pepSEQ_to_outcsv.py
```



#### Step 18: Generate final plots
```bash
cd af2_init_guess
python plot_swarm_pae-inter_CSVout_with_oriSub_fixOrdi_portrait_set_full.py
```

---

## 📁 File Structure

```
subtimizer/
├── *.py                # Helper scripts
├── *.sh                # SLURM scripts
├── af2_des_env.yaml
├── mpnn_des_env.yaml
├── instructions.ins
├── README.md
└── LICENSE
```

---

## 📄 Citation

If you use Subtimizer in your work, please cite:

> **Yekeen, A. A. et al.** AI-driven design of potent and selective kinase peptide substrates using Subtimizer. *bioRxiv* (2025).  
> [https://doi.org/10.1101/2025.07.04.663216](https://doi.org/10.1101/2025.07.04.663216)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
