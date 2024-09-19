import shutil
import os

# List of directories to remove
directories = ["samples", "samples_runned", "raw_data", "opentrons_scripts",
               "microplate_diagrams", "run_master_table", "ms_run_tables", 
               "color_tables", "tube_stock", "growth_data"]

# Remove each directory and its contents
for directory in directories:
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Removed directory: {directory}")
    else:
        print(f"Directory not found: {directory}")