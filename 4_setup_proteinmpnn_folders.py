import os
import argparse

parser = argparse.ArgumentParser(description='Create folders for launching ProteinMPNN.')
parser.add_argument('--file', type=str, required=True, help='Path to the list file containing folder names')

args = parser.parse_args()
file_path = args.file

try:
    with open(file_path, 'r') as file:
        for line in file:
            item = line.strip()
            if item:
                nested_path = os.path.join(item, 'AFcomplex', 'mpnn_des')
                os.makedirs(nested_path, exist_ok=True)
    print(f"Folder created successfully using {file_path}")
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    