import os
import argparse


parser = argparse.ArgumentParser(description='Create folders from a list of names in a file.')
parser.add_argument('--file', type=str, required=True, help='Path to the list file containing folder names')

args = parser.parse_args()
file_path = args.file

try:
    with open(file_path, 'r') as file:
        for line in file:
            folder_name = line.strip()
            if folder_name:
                os.makedirs(folder_name, exist_ok=True)
    print(f"Folders created from {file_path}")
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")