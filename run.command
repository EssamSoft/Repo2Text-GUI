#!/bin/bash

# Get the directory where this script is physically located
# $0 represents the script path, dirname extracts the folder path
script_dir="$(cd "$(dirname "$0")" && pwd)"

# Change the current working directory to the script's location
# This is crucial so that main.py can find its own relative assets (if any)
cd "$script_dir"

# Now we can simply run main.py as we are in the correct folder
python3 "main.py"