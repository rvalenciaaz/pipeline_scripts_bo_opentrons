#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Process the inputs for the script.")

parser.add_argument('--iteration', type=int, help='Iteration')
parser.add_argument('--rackdata', type=str, help='Filename for rack and component dataframe.')
parser.add_argument('--bigdata', type=str, help='Filename for reservoir and component dataframe.')

# Parse arguments
args = parser.parse_args()


iteration = args.iteration
rackcode = pd.read_csv(args.rackdata,index_col=0,dtype=str)
bigcode=pd.read_csv(args.bigdata,index_col=0,dtype=str)

compnumber=len(pd.unique(rackcode.index))
#changing rate to 0.7

#iteration=0
#dim=7

df=pd.read_csv("tube_stock/"+str(iteration)+"_tube_stock.csv")

#coords for first rows in the tube rack
re1=["A1","A2","A3","A4","A5","A6","B1","B2","B3"]
#coords for last rows in the tube rack
re2=["C1","C2","C3","C4","C5","C6","D1","D2","D3"]

#number of tubes racks to use
racknumber=int(np.ceil(compnumber/2))
bignumber=int(np.ceil(compnumber/4))
#code for rack position, (rack_number, rack_row_position)
#rackcode={"Glucose":("1","1"),"NH4Cl":("1","2"),"MgSO4":("2","1"),"KH2PO4":("2","2"),
#        "Na2HPO4":("3","1"),"CaCl2":("3","2"),"NaCl": ("4","1")}
#bigcode={"Glucose":("A3","1"),"NH4Cl":("A4","1"),"MgSO4":("B3","1"),"KH2PO4":("B4","1"),
#        "Na2HPO4":("A3","2"),"CaCl2":("A4","2"),"NaCl": ("B3","2")}

with open("opentrons_scripts/"+str(iteration)+"_stock_opentrons.py","w") as f:
    #write basics
    f.write("from opentrons import protocol_api\nmetadata = {'apiLevel': '2.13'}\ndef run(protocol: protocol_api.ProtocolContext):\n")
    #write tips
    f.write("\ttiprack_1 = protocol.load_labware('opentrons_96_tiprack_1000ul',10)\n\ttiprack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 11)\n")
    #write tube racks
    for rn in range(1, racknumber+1):
        f.write("\treservoir_"+str(rn)+"= protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',"+str(rn)+")\n")
    
    #write falcon tubes
    f.write("\tbig1=protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical',6)\n\tbig2=protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical',9)\n")
    #write pipettes
    f.write("\tp1000 = protocol.load_instrument('p1000_single', 'right', tip_racks=[tiprack_1])\n\tp300 = protocol.load_instrument('p300_single', 'left', tip_racks=[tiprack_2])\n")
    #columns in tube stock df
    for i in pd.unique(df.columns[1:]):
        df2=df[["sample",i]].copy().reset_index(drop=True)
        #write comment about compound
        f.write("\t#"+i+"\n")
        #pick tips
        if (df2[i] <= 300).all():
            f.write("\tp300.pick_up_tip()\n")
        elif (df2[i] > 300).all():
            f.write("\tp1000.pick_up_tip()\n") 
        else:
            f.write("\tp300.pick_up_tip()\n")
            f.write("\tp1000.pick_up_tip()\n")
        #check if it's the compound of water
        cati=i.split("_")
        #rack and falcon tubes coords
        rackdata=rackcode.loc[cati[1]]
        bigdata=bigcode.loc[cati[1]]
        if rackdata[1]=="1":
            linea=re1
        else:
            linea=re2
        resi=bigdata[1]
        #if the column is a compound
        if cati[0]=="Vol":
            for iq,j in df2.iterrows():
                if ((j[i]<=300) & (j[i]!=0)):
                    f.write("\tp300.aspirate("+str(j[i])+",big"+resi+"['"+bigdata[0]+"'],rate=0.7)\n")
                    f.write("\tp300.dispense("+str(j[i])+",reservoir_"+rackdata[0]+"['"+linea[iq]+"'],rate=0.7)\n")
                if ((j[i]>300) & (j[i]<=1000)):
                    f.write("\tp1000.aspirate("+str(j[i])+",big"+resi+"['"+bigdata[0]+"'],rate=0.7)\n")
                    f.write("\tp1000.dispense("+str(j[i])+",reservoir_"+rackdata[0]+"['"+linea[iq]+"'],rate=0.7)\n")
                if ((j[i]>1000)):
                    newfor="{:.2f}".format(j[i]/2)
                    f.write("\tp1000.aspirate("+newfor+",big"+resi+"['"+bigdata[0]+"'],rate=0.7)\n")
                    f.write("\tp1000.dispense("+newfor+",reservoir_"+rackdata[0]+"['"+linea[iq]+"'],rate=0.7)\n")
                    f.write("\tp1000.aspirate("+newfor+",big"+resi+"['"+bigdata[0]+"'],rate=0.7)\n")
                    f.write("\tp1000.dispense("+newfor+",reservoir_"+rackdata[0]+"['"+linea[iq]+"'],rate=0.7)\n")
        #if the column is water
        else:
            for iq,j in df2.iterrows():
                if ((j[i]<=300) & (j[i]!=0)):
                    f.write("\tp300.aspirate("+str(j[i])+",big2['B4'],rate=0.7)\n")
                    f.write("\tp300.dispense("+str(j[i])+",reservoir_"+rackdata[0]+"['"+linea[iq]+"'],rate=0.7)\n")
                if ((j[i]>300) & (j[i]<=1000)):
                    f.write("\tp1000.aspirate("+str(j[i])+",big2['B4'],rate=0.7)\n")
                    f.write("\tp1000.dispense("+str(j[i])+",reservoir_"+rackdata[0]+"['"+linea[iq]+"'],rate=0.7)\n")
                if ((j[i]>1000)):
                    newfor="{:.2f}".format(j[i]/2)
                    f.write("\tp1000.aspirate("+newfor+",big2['B4'],rate=0.7)\n")
                    f.write("\tp1000.dispense("+newfor+",reservoir_"+rackdata[0]+"['"+linea[iq]+"'],rate=0.7)\n")
                    f.write("\tp1000.aspirate("+newfor+",big2['B4'],rate=0.7)\n")
                    f.write("\tp1000.dispense("+newfor+",reservoir_"+rackdata[0]+"['"+linea[iq]+"'],rate=0.7)\n")
        #drop tips
        if (df2[i] <= 300).all():
            f.write("\tp300.drop_tip()\n")
        elif (df2[i] >= 1000).all():
            f.write("\tp1000.drop_tip()\n")
        elif all(300 < x <= 2000 for x in df2[i]):
            f.write("\tp1000.drop_tip()\n")  
        else:
            f.write("\tp300.drop_tip()\n")
            f.write("\tp1000.drop_tip()\n")




