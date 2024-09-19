#!/usr/bin/env python
# coding: utf-8

import os
import torch
import random
import numpy as np
import pandas as pd
import argparse
from scipy.stats import qmc  # For Sobol and LHS sampling

# Argument parsing
parser = argparse.ArgumentParser(description="Initial design script")
parser.add_argument("--dim", type=int, required=True, default=2, help="Number of dimensions")
parser.add_argument("--iter", type=int, help="Iteration number (not required if --big is activated)")
parser.add_argument("--labels", type=str, required=True, default="1", help="Column labels file")
parser.add_argument("--samplesper", required=True, type=int, default=7, help="Samples per iteration")
parser.add_argument("--big", action="store_true", help="Flag for large experiment")
parser.add_argument("--batches", type=int, help="Number of batches (required if --big is present)")
parser.add_argument("--method", type=str, required=True, choices=["sobol", "lhs"], help="Sampling method: 'sobol' or 'lhs'")
args = parser.parse_args()

# Handle 'batches' requirement if 'big' is present
if args.big and args.batches is None:
    parser.error("--batches is required when --big is specified")

# Initialize parameters
dim = args.dim
col_labels = args.labels
init_samples = args.samplesper
iteration = args.iter if not args.big else 0  # Default iteration to 0 when --big is activated

# Adjust samples for big experiment
if args.big:
    init_samples *= args.batches

# Create necessary directories
for directory in ["samples", "samples_runned", "raw_data", "opentrons_scripts",
                  "microplate_diagrams", "run_master_table", "ms_run_tables", 
                  "color_tables", "tube_stock", "growth_data"]:
    os.makedirs(directory, exist_ok=True)

# Sampling using scipy for both sobol and lhs
if args.method == "sobol":
    # Sobol sampling using scipy
    sobol_sampler = qmc.Sobol(d=dim, scramble=True)
    samples = sobol_sampler.random(n=init_samples)
else:  # LHS method
    # LHS sampling using scipy
    lhs_sampler = qmc.LatinHypercube(d=dim)
    samples = lhs_sampler.random(n=init_samples)

# Convert samples to DataFrame
labels_df = pd.read_csv(col_labels)
col_labels_list = labels_df["Component"].to_list()

if len(col_labels_list) != dim:
    raise ValueError(f"Number of components in {col_labels} ({len(col_labels_list)}) does not match the number of dimensions (--dim {dim}).")

# Save samples based on whether --big is activated or not
if args.big:
    # Save samples with the default space-fill filename for big experiment
    init_table = pd.DataFrame({"sample": [f"0_{i+1}" for i in range(init_samples)]})
    init_table[col_labels_list] = samples
    init_table.to_csv("samples/samples_space_fill.csv", index=False)

    # Randomize and assign batches
    samples_df = pd.read_csv("samples/samples_space_fill.csv")
    samples_df["batch"] = random.sample([str(i) for i in range(args.batches)] * 7, len(samples_df))

    # Save batch files based on batch number
    for bnum in samples_df["batch"].unique():
        batch_df = samples_df[samples_df["batch"] == bnum].reset_index(drop=True)
        batch_df["sample"] = [f"{bnum}_{i+1}" for i in batch_df.index]
        batch_df.drop(columns=["batch"], inplace=True)
        batch_df.to_csv(f"samples/{bnum}_samples.csv", index=False)

else:
    # Save samples for non-big experiment with iteration-based filename
    init_table = pd.DataFrame({"sample": [f"{iteration}_{i+1}" for i in range(init_samples)]})
    init_table[col_labels_list] = samples
    init_table.to_csv(f"samples/{iteration}_samples.csv", index=False)
