#!/bin/bash

# Check if the input file is provided as an argument
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file> <output_file>"
    exit 1
fi

input_file=$1
output_file=$2

# Extract the first two rows (headers or metadata)
head -n 2 "$input_file" > "$output_file"

# Sort the rest of the file based on the second column (numerically, for negative numbers)
tail -n +3 "$input_file" | sort -k 2,2 -n >> "$output_file"

echo "Sorting complete. Output saved to $output_file"
