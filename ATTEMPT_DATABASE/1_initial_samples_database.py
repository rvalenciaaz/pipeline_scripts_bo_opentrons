#!/usr/bin/env python
# coding: utf-8

import os
import sqlite3
import logging
import torch
import random
import numpy as np
import pandas as pd
import argparse
from botorch.utils.sampling import draw_sobol_samples
import pyDOE2  # For Latin Hypercube Sampling

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Argument parsing for experiment code and optional database path
parser = argparse.ArgumentParser(description="Initial design script")
parser.add_argument("--experiment_code", type=str, required=True, help="Code of the experiment to run")
parser.add_argument("--db_path", type=str, default="experiments.db", help="Path to the SQLite database (default: experiments.db)")
args = parser.parse_args()

# Connect to the database and fetch experiment details
def fetch_experiment_data(experiment_code, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch experiment details from the database
        cursor.execute("SELECT dim, samplesper, big, batches, method FROM experiments WHERE experiment_code = ?", (experiment_code,))
        experiment_data = cursor.fetchone()
        if experiment_data is None:
            raise ValueError(f"Experiment with code '{experiment_code}' not found in the database")

        dim, samplesper, big, batches, method = experiment_data

        # Fetch the component names (labels) associated with the experiment
        cursor.execute("""
            SELECT c.component_name
            FROM experiment_component_mappings ecm
            JOIN components c ON ecm.component_id = c.component_id
            WHERE ecm.experiment_code = ?
        """, (experiment_code,))
        components = [row[0] for row in cursor.fetchall()]

        if not components:
            raise ValueError(f"No components found for experiment code '{experiment_code}'")

        conn.close()

        return {
            "dim": dim,
            "samplesper": samplesper,
            "big": big,
            "batches": batches,
            "method": method,
            "components": components
        }

    except Exception as e:
        logging.error(f"Error fetching data from the database: {e}")
        raise

# Fetch experiment data from the database
experiment_code = args.experiment_code
db_path = args.db_path
logging.info(f"Fetching data for experiment code: {experiment_code}")
experiment_data = fetch_experiment_data(experiment_code, db_path)

# Initialize parameters from the experiment data
dim = experiment_data["dim"]
col_labels_list = experiment_data["components"]
init_samples = experiment_data["samplesper"]
is_big = experiment_data["big"]
method = experiment_data["method"]
iteration = 0  # Default iteration to 0

# Adjust samples for big experiment
if is_big:
    if experiment_data["batches"] is None:
        raise ValueError("--batches is required when --big is True")
    init_samples *= experiment_data["batches"]
    samples_per_batch=experiment_data["samplesper"]

# Create necessary directories
for directory in ["samples", "samples_runned", "raw_data", "opentrons_scripts",
                  "microplate_diagrams", "run_master_table", "ms_run_tables", 
                  "color_tables", "tube_stock", "growth_data"]:
    os.makedirs(directory, exist_ok=True)
logging.info("Necessary directories created or already exist.")

# Sampling
bounds = torch.stack([torch.zeros(dim), torch.ones(dim)])
if method == "sobol":
    logging.info("Using Sobol sampling method.")
    samples = draw_sobol_samples(bounds=bounds, n=init_samples, q=1).reshape(init_samples, dim)
else:  # LHS method
    logging.info("Using Latin Hypercube sampling method.")
    samples = torch.tensor(pyDOE2.lhs(n=dim, samples=init_samples))

# Check if number of labels matches the number of dimensions
if len(col_labels_list) != dim:
    raise ValueError(f"Number of components ({len(col_labels_list)}) does not match the number of dimensions ({dim}).")

# Save samples based on whether --big is activated or not
if is_big:
    logging.info("Big experiment mode activated.")
    # Save samples with the default space-fill filename for big experiment
    init_table = pd.DataFrame({"sample": [f"0_{i+1}" for i in range(init_samples)]})
    init_table[col_labels_list] = samples
    init_table.to_csv("samples/samples_space_fill.csv", index=False)

    # Randomize and assign batches
    samples_df = pd.read_csv("samples/samples_space_fill.csv")
    samples_df["batch"] = random.sample([str(i) for i in range(experiment_data["batches"])] * samples_per_batch, len(samples_df))

    # Save batch files based on batch number
    for bnum in samples_df["batch"].unique():
        batch_df = samples_df[samples_df["batch"] == bnum].reset_index(drop=True)
        batch_df["sample"] = [f"{bnum}_{i+1}" for i in batch_df.index]
        batch_df.drop(columns=["batch"], inplace=True)
        batch_df.to_csv(f"samples/{bnum}_samples.csv", index=False)
else:
    logging.info("Standard experiment mode (non-big) activated.")
    # Save samples for non-big experiment with iteration-based filename
    init_table = pd.DataFrame({"sample": [f"{iteration}_{i+1}" for i in range(init_samples)]})
    init_table[col_labels_list] = samples
    init_table.to_csv(f"samples/{iteration}_samples.csv", index=False)

logging.info("Sampling completed and saved successfully.")