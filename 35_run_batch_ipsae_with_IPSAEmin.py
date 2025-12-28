#!/usr/bin/env python3

import os
import sys
import glob
import pandas as pd
import subprocess
import argparse
import re
from concurrent.futures import ProcessPoolExecutor, as_completed

# --- CONFIGURATION ---
PAE_CUTOFF = "15"
DIST_CUTOFF = "15"
MAX_WORKERS = 8  # Adjust based on your CPU cores
# ---------------------

def get_kinase_peptide_name(csv_filename):
    """Extracts kinase_peptide from filename."""
    base = os.path.basename(csv_filename)
    if "_merged_scores" in base:
        return base.split("_merged_scores")[0]
    return base.split("_")[0]  # Fallback

def find_files_standard(home_path, kinase_peptide, structure_id):
    """Finds PAE and PDB files for the standard case."""
    base_dir = os.path.join(home_path, kinase_peptide, "AFcomplex", "mpnn_out_clust_fold", "seqs", structure_id)
    
    if not os.path.isdir(base_dir):
        return None, None, f"Dir not found: {base_dir}"

    pae_pattern = os.path.join(base_dir, f"{structure_id}_scores_rank_001_alphafold2_multimer_v3_model_*.json")
    pdb_pattern = os.path.join(base_dir, f"{structure_id}_*_rank_001_alphafold2_multimer_v3_model_*.pdb")

    pae_files = glob.glob(pae_pattern)
    pdb_files = glob.glob(pdb_pattern)

    if not pae_files:
        return None, None, f"No PAE file found in {base_dir} matching pattern"
    if not pdb_files:
        return None, None, f"No PDB file found in {base_dir} matching pattern"
    
    return pae_files[0], pdb_files[0], None

def find_files_special(home_path, kinase_peptide, fold_value):
    """
    Finds PAE and PDB files for the special case by searching round_1 to round_5.
    Handles mismatch where PDB is named 'relaxed' but JSON is named 'scores'.
    Prioritizes 'relaxed' PDBs if multiple versions exist.
    """
    debug_search_paths = []

    for x in range(1, 6):
        round_dir = os.path.join(home_path, kinase_peptide, "AFcomplex", f"round_{x}")
        if not os.path.isdir(round_dir):
            continue
            
        debug_search_paths.append(round_dir)

        # 1. Find PDB (Prioritize 'relaxed' over 'unrelaxed')
        # We look for any PDB containing the fold_value (e.g. "rank_001...model_5...")
        pdb_pattern = os.path.join(round_dir, f"*{fold_value}*.pdb")
        pdb_candidates = glob.glob(pdb_pattern)
        
        final_pdb = None
        if pdb_candidates:
            # If we have multiple (relaxed and unrelaxed), pick relaxed
            relaxed = [f for f in pdb_candidates if "_relaxed_" in f]
            if relaxed:
                final_pdb = relaxed[0]
            else:
                final_pdb = pdb_candidates[0]

        # 2. Find PAE/JSON (Usually named 'scores' or just contains the ID)
        pae_pattern = os.path.join(round_dir, f"*{fold_value}*.json")
        pae_candidates = glob.glob(pae_pattern)
        
        final_pae = None
        if pae_candidates:
            # Just take the first matching JSON (usually only one matches the specific rank/seed)
            final_pae = pae_candidates[0]

        # 3. Return if both found
        if final_pdb and final_pae:
            print(f"  -> Found in round_{x}:")
            print(f"     PAE: {os.path.basename(final_pae)}")
            print(f"     PDB: {os.path.basename(final_pdb)}")
            return final_pae, final_pdb, None
            
    return None, None, f"Files for '{fold_value}' not found in rounds 1-5"

def run_ipsae_task(task_info):
    """Runs ipsae.py for a single task."""
    index, pae_file, struct_file = task_info
    
    cmd = ["python3", "ipsae.py", pae_file, struct_file, PAE_CUTOFF, DIST_CUTOFF]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return index, "SUCCESS", struct_file
        else:
            return index, "ERROR", result.stderr
    except Exception as e:
        return index, "EXCEPTION", str(e)

def parse_ipsae_output(pdb_path):
    """
    Parses the generated txt file.
    - Finds the 'max' row for the main metrics.
    - Finds the minimum 'ipSAE' value across all rows (asym and max).
    """
    p_str = str(int(PAE_CUTOFF)).zfill(2)
    d_str = str(int(DIST_CUTOFF)).zfill(2)
    
    txt_path = pdb_path.replace(".pdb", "") + f"_{p_str}_{d_str}.txt"
    
    if not os.path.exists(txt_path):
        return None
    
    try:
        results = {}
        ipSAE_values = []  # List to store all ipSAE values found
        
        with open(txt_path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.split()
            if not parts: continue
            
            # Identify row type and collect ipSAE values
            if "max" in parts:
                try:
                    type_idx = parts.index("max")
                    
                    # Store the 'max' row metrics
                    results['ipSAE']       = float(parts[type_idx + 1])
                    results['ipSAE_d0chn'] = float(parts[type_idx + 2])
                    results['ipSAE_d0dom'] = float(parts[type_idx + 3])
                    results['ipTM_af']     = float(parts[type_idx + 4])
                    results['ipTM_d0chn']  = float(parts[type_idx + 5])
                    
                    # Also track this value for min calculation
                    ipSAE_values.append(float(parts[type_idx + 1]))
                except (ValueError, IndexError):
                    continue
            
            elif "asym" in parts:
                try:
                    type_idx = parts.index("asym")
                    # Track this value for min calculation
                    ipSAE_values.append(float(parts[type_idx + 1]))
                except (ValueError, IndexError):
                    continue

        # Calculate min if we found any values
        if ipSAE_values:
            results['ipSAE_min'] = min(ipSAE_values)
        
        # Only return if we successfully parsed the 'max' row
        if 'ipSAE' in results:
            return results
        else:
            return None

    except Exception as e:
        print(f"Error parsing {txt_path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Batch run ipsae.py based on CSV input.")
    parser.add_argument("csv_file", help="Path to input CSV file")
    parser.add_argument("home_path", help="HOME_path directory")
    args = parser.parse_args()

    csv_path = args.csv_file
    home_path = args.home_path
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
        
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    kinase_peptide = get_kinase_peptide_name(csv_path)
    print(f"Derived kinase_peptide name: {kinase_peptide}")
    
    tasks = []
    
    # 1. Prepare Tasks
    print("Locating files for each entry...")
    for idx, row in df.iterrows():
        struct_id = str(row['id'])
        
        is_special = bool(re.match(r"^\d+_seed_\d+_af2pred$", struct_id))
        
        pae_file = None
        pdb_file = None
        error_msg = None
        
        if is_special:
            fold_val = str(row['fold'])
            print(f"Row {idx}: Detected special case ({struct_id}). Searching round_1..5 for {fold_val}...")
            pae_file, pdb_file, error_msg = find_files_special(home_path, kinase_peptide, fold_val)
        else:
            pae_file, pdb_file, error_msg = find_files_standard(home_path, kinase_peptide, struct_id)
            
        if pae_file and pdb_file:
            tasks.append((idx, pae_file, pdb_file))
        else:
            print(f"Row {idx} ({struct_id}): Skipping. {error_msg}")

    print(f"\nStarting processing of {len(tasks)} valid tasks with {MAX_WORKERS} workers...")
    
    # 2. Run Tasks in Parallel
    results = {} 
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_task = {executor.submit(run_ipsae_task, t): t for t in tasks}
        
        for future in as_completed(future_to_task):
            idx, status, msg = future.result()
            if status == "SUCCESS":
                results[idx] = msg 
            else:
                print(f"Row {idx}: Execution Failed - {msg}")

    # 3. Post-Process and Update CSV
    print("\nParsing outputs and updating DataFrame...")
    
    # Initialize new columns including ipSAE_min
    new_columns = ['ipSAE', 'ipSAE_d0chn', 'ipSAE_d0dom', 'ipTM_af', 'ipTM_d0chn', 'ipSAE_min']
    for col in new_columns:
        if col not in df.columns:
            df[col] = None

    update_count = 0
    for idx, pdb_path in results.items():
        data_dict = parse_ipsae_output(pdb_path)
        if data_dict is not None:
            for col in new_columns:
                # Use .get() to avoid errors if a key is missing (though it shouldn't be)
                val = data_dict.get(col)
                if val is not None:
                    df.at[idx, col] = val
            update_count += 1
        else:
            print(f"Row {idx}: Output file parsing failed or 'max' type not found.")

    # 4. Save Output
    output_csv = csv_path.replace(".csv", f"_with_ipSAEmin_{PAE_CUTOFF}_{DIST_CUTOFF}.csv")
    df.to_csv(output_csv, index=False)
    print(f"\nProcessing complete.")
    print(f"Updated {update_count} entries.")
    print(f"Saved results to: {output_csv}")

if __name__ == "__main__":
    main()