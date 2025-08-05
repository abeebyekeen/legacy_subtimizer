#!/bin/bash

set -e

flexpepdock="$ROSETTA/source/bin/FlexPepDocking.default.linuxgccrelease"

if [ -z "$ROSETTA" ] || [ ! -d "$ROSETTA/database" ]; then
  echo "Error: ROSETTA env variable is not set or \$ROSETTA/database does not exist."
  exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <input_pdb_file>"
  echo "Example: $0 alk_axltd_3868.pdb"
  exit 1
fi

INPUT_PDB="$1"

if [ ! -f "$INPUT_PDB" ]; then
  echo "Error: Input file '$INPUT_PDB' not found."
  exit 1
fi

# get basename of input pdb
BASE_NAME="${INPUT_PDB%.*}"

# expected intermediate output from prepack
INTERMEDIATE_PREPACK_PDB="${BASE_NAME}_0001.pdb"

# Renamed prepacked file
PREPACKED_PDB="${BASE_NAME}_ppk.pdb"

# Directory names
SCORE_ONLY_DIR="score_only"
PEPREFINE_DIR="peprefine"

echo "--- Starting FlexPepDock workflow for $INPUT_PDB ---"
echo "Intermediate prepack output will be: $INTERMEDIATE_PREPACK_PDB"
echo "Renamed prepack file will be: $PREPACKED_PDB"
echo "Output directories will be: $SCORE_ONLY_DIR and $PEPREFINE_DIR"
echo ""

echo "Running flexpepdock prepack..."

"$flexpepdock" -database "$ROSETTA/database" -s "$INPUT_PDB" -flexpep_prepack -ex1 -ex2aro -scorefile ppk.score.sc |& tee ppk.log

# Check if intermediate prepack was successful
if [ ! -f "$INTERMEDIATE_PREPACK_PDB" ]; then
    echo "Error: Expected prepack output '$INTERMEDIATE_PREPACK_PDB' not found after prepack step."
    exit 1
fi

echo "Renaming $INTERMEDIATE_PREPACK_PDB to $PREPACKED_PDB..."
mv "$INTERMEDIATE_PREPACK_PDB" "$PREPACKED_PDB"
sleep 1

echo "Creating directories: $SCORE_ONLY_DIR and $PEPREFINE_DIR..."
mkdir "$SCORE_ONLY_DIR" "$PEPREFINE_DIR"

#run flexpepdock score_only
cd "$SCORE_ONLY_DIR"
echo "Running flexpepdock score_only..."

"$flexpepdock" -database "$ROSETTA/database" -s "../$PREPACKED_PDB" -scorefile score.only.sc -flexpep_score_only -ex1 -ex2aro -use_input_sc |& tee score.only.log

#run refinement
cd "../$PEPREFINE_DIR"
echo "Running flexpepdock pep_refine..."
"$flexpepdock" -database "$ROSETTA/database" -s "../$PREPACKED_PDB" -scorefile refine.score.sc -pep_refine -ex1 -ex2aro -use_input_sc -nstruct 250 |& tee refine.score.log

cd .. # go back from peprefine to the initial directory

echo "--- FlexPepDock completed successfully for $INPUT_PDB ---"