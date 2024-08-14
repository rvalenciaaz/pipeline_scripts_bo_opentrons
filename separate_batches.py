#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import seaborn as sns
import random
import os 

new_path = "samples/0_samples_space_fill.csv"
os.rename(old_path, new_path) if os.path.exists(old_path := "samples/0_samples.csv") else print("File not found or already renamed")

random.seed(1245)

samples=pd.read_csv("samples/0_samples_space_fill.csv")

batchnumber=6
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


