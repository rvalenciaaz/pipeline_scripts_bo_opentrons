#!/usr/bin/env python
# coding: utf-8

import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import string
from functools import reduce
import matplotlib.patches as mpatches

# Set up argument parser
parser = argparse.ArgumentParser(description="Process the inputs for the script.")
parser.add_argument('--dim', type=int, default=2, help='Dimension argument.')
parser.add_argument('--iteration', type=int, default=0, help='Iteration number.')
parser.add_argument('--voltube', type=int, default=2000, help='Volume of tube in microliters.')
parser.add_argument('--maxwell', type=int, default=800, help='Max well volume.')
parser.add_argument('--maxvol', type=int, default=80, help='Max volume.')
parser.add_argument('--stock', type=str, help='Filename for stock dataframe.')
parser.add_argument('--medium', type=str, help='Filename for medium dataframe.')
parser.add_argument('--space', type=str, help='Filename for space dataframe.')

# Parse arguments
args = parser.parse_args()

dim = args.dim
iteration = args.iteration
voly = args.voltube
maxwell = args.maxwell
maxvol = args.maxvol

# Load DataFrames from filenames provided as arguments
if args.stock:
    stock = pd.read_csv(args.stock)
else:
    raise ValueError("A filename for the stock dataframe must be provided.")

if args.medium:
    medium = pd.read_csv(args.medium)
else:
    raise ValueError("A filename for the medium dataframe must be provided.")

if args.space:
    labels = pd.read_csv(args.space,index_col=0)
else:
    raise ValueError("A filename for the labels dataframe must be provided.")

dic1=dict(zip(stock["compound"],stock["max_concentration_mM"]))
dic2=dict(zip(medium["compound"],medium[args.medium.split("_")[0]+"_concentration_mM"]))
compi=labels.index.tolist()

samples=pd.read_csv("samples/"+str(iteration)+"_samples.csv")

#adding standard concentration for fixed compounds
#nen=list(set(compi)-set(samples.columns[1:]))
nen=compi[dim:]
dictio1={i:dic1[i] for i in nen}
dictio2={i:dic2[i] for i in nen}

for k in nen:
    samples[k]=dictio2[k]/dictio1[k]

cor=[(dic2[k]/dic1[k]) for k in list(samples.columns) if (k!="sample")]

standard1=[str(iteration)+"_CTRL"]+cor
standard2=[str(iteration)+"_REF"]+cor

stdf=pd.DataFrame(columns=samples.columns)

stdf.loc[0]=standard1
stdf.loc[1]=standard2

samples=pd.concat([samples,stdf]).reset_index(drop=True)

for j in samples.columns[1:]:
    samples["Vol_"+j]=round(((samples[j]*labels.loc[j][1])*maxwell/maxvol)*voly/labels.loc[j][2],1)
    samples["Water_"+j]=round(voly-samples["Vol_"+j],1)


newcol=["sample"]+[z for z in list(samples.columns) if (("Vol" in z) or ("Water" in z))]

newdf=samples[newcol].copy()

newdf.to_csv("tube_stock/"+str(iteration)+"_tube_stock.csv", index=False)
newdf.to_excel("tube_stock/"+str(iteration)+"_tube_stock.xlsx", index=False)