# Load necessary libraries
library(data.table)
library(pmp)
library(tidyr)
library(dplyr)
library(GenomicRanges)

library(S4Vectors)
library(SummarizedExperiment)
#library(pmp)
library(ggplot2)
library(reshape2)
library(gridExtra)
# Load your metabolomic data
# Replace 'path_to_your_data.csv' with the path to your data file

setwd("~/GIT_FOLDER/surfactin_bayesian_optimisation/TEST/SOBOL_BIG/7F_48_WELL_COMPLETE_FILLING_M9_LIPOQQQ")

iteration <- "0"
data <- fread(paste("baseline_corrected/","all_baseline_correction.csv",sep=""))

original_order <- fread(paste("ms_run_tables/","all_ms_list.csv",sep=""))

order_filtered <- original_order[!grepl("Blank|Solvent", original_order$`File Name`), ]

matrix_df <- pivot_wider(data, names_from = compound, values_from = integral)

df_filtered <- matrix_df[!grepl("Blank|Solvent", matrix_df$file), ]


# 1. Add a New Column for Numerical Order


# Reorder the columns based on this order

df_filtered <- as.data.frame(df_filtered)

# Set the first column as row names
row.names(df_filtered) <- df_filtered[[1]]

# Optionally, remove the first column from the dataframe
df_filtered <- df_filtered[-1]

# Remove columns
#df_filtered <- df_filtered %>% select(-c(Cyanocobalamin, Extra2, Propionate, Isovalerate, Thiamine, Choline,`Pantothenic acid`))


#df_filtered[df_filtered==0]<-1
#zero_positions <- which(df_filtered == 0, arr.ind = TRUE)


df_filtered<-t(df_filtered)

desired_order <- order_filtered$`File Name`

# Reorder columns in target DataFrame
target_df<- df_filtered[, desired_order]

sample_order <- c(1:ncol(target_df))

batch <- rep("0", length(colnames(target_df)))
class <- ifelse(grepl("QC", colnames(target_df)), 
                "QC", 
                sapply(strsplit(colnames(target_df), "_"), `[`, 2))


new_df<-SummarizedExperiment(assays=list(counts=target_df))

#assays(new_df)$counts

corrected_data <- QCRSC(df=new_df, order=sample_order, batch=batch, 
                        classes=class, spar=0, minQC=4)

plots <- sbc_plot (df=new_df, corrected_df=corrected_data, classes=class, 
                   batch=batch, output="temp.pdf", indexes=seq(1,58))

data_normalised <- pqn_normalisation(df=corrected_data,classes=class, qc_label="QC")


write.csv(data_normalised, paste("batch_correction/",iteration,"_batch_corrected.csv",sep=""))

df <- MTBLS79[ , MTBLS79$Batch==1]
df2<- pqn_normalisation(df=df,
                  classes=df$Class, qc_label='QC')


