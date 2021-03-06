# Run the nested cross-validation for KBMF

source("nested_cross_val_kbmf.R")
K <- 10
R_values <- c(6,8,10)

Px <- 3
Nx <- 622
Pz <- 3
Nz <- 138

# Load in the drug sensitivity values
folder_drug_sensitivity <- '/Users/thomasbrouwer/Documents/Projects/libraries/BNMTF/data_drug_sensitivity/gdsc/'
name_drug_sensitivity <- 'ic50_excl_empty_filtered_cell_lines_drugs.txt'
Y <- as.matrix(read.table(paste(folder_drug_sensitivity,name_drug_sensitivity,sep=''),
				header=TRUE,
				sep=',',
				colClasses=c(rep("NULL",3), rep("numeric",138))))

# Load in the kernels - X = cancer cell lines, Z = drugs
folder_kernels <- '/Users/thomasbrouwer/Documents/Projects/libraries/BNMTF/data_drug_sensitivity/gdsc/kernels/'

kernel_copy_variation <- as.matrix(read.table(paste(folder_kernels,'copy_variation.txt',sep=''),header=TRUE,sep='\t'))
kernel_gene_expression <- as.matrix(read.table(paste(folder_kernels,'gene_expression.txt',sep=''),header=TRUE,sep='\t'))
kernel_mutation <- as.matrix(read.table(paste(folder_kernels,'mutation.txt',sep=''),header=TRUE,sep='\t'))

kernel_1d2d <- as.matrix(read.table(paste(folder_kernels,'1d2d_descriptors.txt',sep=''),header=TRUE,sep=','))
kernel_fingerprints<- as.matrix(read.table(paste(folder_kernels,'PubChem_fingerprints.txt',sep=''),header=TRUE,sep=','))
kernel_targets <- as.matrix(read.table(paste(folder_kernels,'targets.txt',sep=''),header=TRUE,sep=','))

Kx <- array(0, c(Nx, Nx, Px))
Kx[,, 1] <- kernel_copy_variation
Kx[,, 2] <- kernel_gene_expression
Kx[,, 3] <- kernel_mutation

Kz <- array(0, c(Nz, Nz, Pz))
Kz[,, 1] <- kernel_1d2d
Kz[,, 2] <- kernel_fingerprints
Kz[,, 3] <- kernel_targets

# Run the cross-validation
kbmf_nested_cross_validation(Kx, Kz, Y, R_values, K)

# R_values <- c(7,8,9)
# MSE: 2.1906, 2.1993, 2.2380, 2.2522, 2.3098
# R^2: 0.8108, 0.8109, 0.8073, 0.8120, 0.8021
# Rp:  0.9005, 0.9005, 0.8986, 0.9011, 0.8958
# Average performances: MSE=2.2380, R^2=0.8086, Rp=0.8993
