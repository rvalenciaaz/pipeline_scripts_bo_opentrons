#!/usr/bin/env python
# coding: utf-8

import os
import torch
import random
import numpy as np
import pandas as pd
import argparse
from botorch.models import SingleTaskGP, HeteroskedasticSingleTaskGP
from botorch.fit import fit_gpytorch_mll
from botorch.acquisition import UpperConfidenceBound,qUpperConfidenceBound
from botorch.optim import optimize_acqf
from botorch.utils.sampling import draw_sobol_samples
from gpytorch.mlls import ExactMarginalLogLikelihood
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.preprocessing import MinMaxScaler

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
dtype = torch.float64

seed = 1245

random.seed(seed)
torch.manual_seed(seed)
torch.backends.cudnn.deterministic = True
if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
np.random.seed(seed)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Initial design script v1.0")
parser.add_argument("--dim", type=int, default=2, help="Number of dimensions")
parser.add_argument("--iter", type=int, default=0, help="Iteration number")
parser.add_argument("--labels", type=str, default=1, help="Column labels")
parser.add_argument("--samplesper", type=int, default=7, help="Samples per iteration")
parser.add_argument("--big", action="store_true", help="Flag for large experiment")
parser.add_argument("--batches", type=int, default=1, help="Number of batches")

args = parser.parse_args()

dim = args.dim
iteration = args.iter
col_labels = args.labels
samples_per_iteration = args.samplesper
init_samples = samples_per_iteration

if args.big:
    batches = args.batches
    init_samples *= batches


directories = ["samples", "samples_runned", "raw_data", "opentrons_scripts",
               "microplate_diagrams", "run_master_table", "ms_run_tables", "color_tables","tube_stock","growth_data"]

for directory in directories:
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        print(f"The directory '{directory}' already exists.")

bounds = torch.stack([torch.zeros(dim,dtype=dtype, device=device), torch.ones(dim,dtype=dtype, device=device)])

sampler = draw_sobol_samples(bounds=bounds, n=init_samples, q=1).reshape(init_samples,dim)

labels=[str(iteration)+"_"+str(i+1) for i in range(init_samples)]

init_table = pd.DataFrame({"sample":labels})

labels_df=pd.read_csv(col_labels)
col_labels=labels_df["Component"].to_list()
init_table[col_labels]=sampler.cpu().numpy()

init_table.to_csv("samples/"+str(iteration)+"_samples.csv",index=False)

if args.big:

    new_path = "samples/0_samples_space_fill.csv"
    os.rename(old_path, new_path) if os.path.exists(old_path := "samples/0_samples.csv") else print("File not found or already renamed")

    samples=pd.read_csv("samples/0_samples_space_fill.csv")

    batchnumber=batches
    # Create a list with 7 copies of each number
    numbers = [str(i) for i in range(batchnumber)] * 7

    # Shuffle the list randomly
    random.shuffle(numbers)

    samples["batch"]=numbers

    for bnum in pd.unique(samples["batch"]):
        df=samples.loc[samples["batch"]==bnum].reset_index(drop=True).reset_index()
        df["sample"]=df.apply(lambda x: x["batch"]+"_"+str(x["index"]+1),axis=1)
        df2=df.drop(["index","batch"],axis=1)
        df2.to_csv("samples/"+str(bnum)+"_samples.csv", index=False)