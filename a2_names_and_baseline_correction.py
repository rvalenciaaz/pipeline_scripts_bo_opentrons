#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from scipy.integrate import trapezoid
from functools import reduce
from pybaselines import Baseline
import matplotlib.pyplot as plt
import seaborn as sns

# Load the mass spectrometry data
iteration="5"
hypertable = pd.read_csv("hypertables/"+iteration+"_hypertable.csv")


# Load compound names from the MS method
compound_table = pd.read_csv("SRM Table_lipo_new.csv")
compound_table_sorted = compound_table.sort_values(["Polarity", "Precursor (m/z)"])

# Separate compounds based on polarity
positive_compounds = compound_table_sorted[compound_table_sorted["Polarity"] == "Positive"]
negative_compounds = compound_table_sorted[compound_table_sorted["Polarity"] == "Negative"]

# Create lists of unique compounds for each polarity
positive_compound_list = list(pd.unique(positive_compounds["Compound"]))
negative_compound_list = list(pd.unique(negative_compounds["Compound"]))
all_compounds_list = positive_compound_list + negative_compound_list

# Verify if the number of unique precursors/fragments matches with unique compounds
unique_precursors = pd.unique(hypertable["scan_type"])
print(len(unique_precursors))
print(len(all_compounds_list))

print(unique_precursors)
# Create a dictionary to map scan types to compound names
scan_type_to_compound = dict(zip(unique_precursors, all_compounds_list))

# Replace scan types in the hypertable with compound names
hypertable["scan_type"] = hypertable["scan_type"].apply(lambda x: scan_type_to_compound.get(x, "file"))

# Load lists of compounds with quality assessments
#bad_quality_compounds = pd.read_csv("bad_quality.txt", header=None)[0].to_list()
uncorrected_compounds = pd.read_csv("uncorrected_2.txt", header=None)[0].to_list()
#compounds_to_correct = pd.read_csv("to_correct.txt", header=None)[0].to_list()

# Filter out bad quality compounds
#quality_hypertable = hypertable[~hypertable["scan_type"].isin(bad_quality_compounds)]
quality_hypertable=hypertable
# Separate compounds into two groups: uncorrected and to be corrected
uncorrected_data = quality_hypertable[quality_hypertable["scan_type"].isin(uncorrected_compounds)].copy()
#corrected_data = quality_hypertable[quality_hypertable["scan_type"].isin(compounds_to_correct)].copy()

savefilt=[]
# Analyze uncorrected compounds
for compound in pd.unique(uncorrected_data["scan_type"]):
    compound_data = uncorrected_data[uncorrected_data['scan_type'] == compound]
    integral = compound_data.groupby("file").apply(lambda x: trapezoid(x["tic"], x=x["rt"])).reset_index()
    integral.columns = ["file", "integral"]
    integral["compound"] = compound
    min_area, max_area = integral["integral"].min(), integral["integral"].max()
    integral["file"]=integral["file"].str.strip(".raw")
    print(min_area, max_area, compound)
    savefilt.append(integral)
    
    plt.figure(figsize=(16, 12))
    
    sns.lineplot(data=compound_data, x='rt', y='tic', hue='file')
    
    plt.title(f"Intensity vs RT for {compound}", fontsize=24)
    plt.gca().legend().remove()

    plt.xlabel("Retention Time (s)",fontsize=20)
    plt.ylabel("Intensity (counts)",fontsize=20)

    plt.xticks(fontsize=20)  # Adjust the font size as needed
    plt.yticks(fontsize=20)  
    plt.savefig("baseline_corrected/"+compound+"_file_U_plot_iteration_"+iteration+".png",dpi=600,bbox_inches="tight")
    plt.savefig("baseline_corrected/"+compound+"_file_U_plot_iteration_"+iteration+"_transparent.png",dpi=600,transparent=True,bbox_inches="tight") #+iteration+
    plt.close()
'''
# Analyze and correct compounds
for compound in pd.unique(corrected_data["scan_type"]):
    compound_data = corrected_data[corrected_data['scan_type'] == compound]
    corrected_frames = []

    for file_name in pd.unique(compound_data["file"]):
        file_data = compound_data[compound_data["file"] == file_name].copy()
        baseline_fitter = Baseline(x_data=file_data["rt"])
        baseline = baseline_fitter.asls(file_data["tic"])[0] #lam=1e9, p=0.01
        file_data["tic"] -= baseline
        corrected_frames.append(file_data)

    corrected_compound_data = reduce(lambda x,y:pd.concat([x,y]), corrected_frames)
    integral = corrected_compound_data.groupby("file").apply(lambda x: trapezoid(x["tic"], x=x["rt"])).reset_index()
    integral.columns = ["file", "integral"]
    integral["compound"] = compound
    min_area, max_area = integral["integral"].min(), integral["integral"].max()
    print(min_area, max_area, compound)
    integral["file"]=integral["file"].str.strip(".raw")
    savefilt.append(integral)
'''
#savefilt contains peak area (area under the curve) data for each compound and each file
condensed=reduce(lambda x,y:pd.concat([x,y]),savefilt)
condensed=condensed.sort_values("file")
condensed_file_list=pd.unique(condensed["file"])

condensed.to_csv("baseline_corrected/"+iteration+"_baseline_corrected.csv", index=False)