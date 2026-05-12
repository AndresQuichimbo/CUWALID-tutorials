"""
this file creates input files for scaling
analysis, at walnut gulch catchement
"""


import os
import pandas as pd
import numpy as np

# Number of samples to generate (you can change this)
n_samples = 100  

# Read ranges of parameter file for model simulations
fname = "/user/work/km19051/HAD_basin/calibration/HAD_parameter_range_file.csv"
#fname = "C:/Users/km19051/OneDrive - Cardiff University/PhD/WS/LandLab/HAD/WS/input_model/HAD_parameter_range_file.csv"

# Read CSV file

# Read CSV file
df = pd.read_csv(fname)

# Drop non-numeric / fixed columns
fixed_cols = ["Grid", "tstep", "model", "type"]
param_cols = [c for c in df.columns if c not in fixed_cols]

# list of model to generate parameter sets
label_model = ["JU",]

for ilabel_model in label_model:
	
	# Read CSV file
	df = pd.read_csv(fname)
	
	# path output
	path_output = fname.split('.')[0] + '_' + ilabel_model + '_2.csv'

	## input file
	#df = df.groupby(['model'])#.reset_index()
	
	#print(df)
	# Get min/max values for each parameter column
	param_ranges = {}
	for col in param_cols:
		param_ranges[col] = (df[df["type"] == "min"][col].values[0],
							df[df["type"] == "max"][col].values[0])
	
	# Generate uniformly distributed samples
	generated = pd.DataFrame({
		col: np.random.uniform(low, high, n_samples)
		for col, (low, high) in param_ranges.items()
	})
	
	## Add fixed values (same for all rows)
	#generated.insert(0, "Grid", df["Grid"].iloc[0])
	#generated.insert(1, "tstep", df["tstep"].iloc[0])
	#generated.insert(2, "model", df["model"].iloc[0])
	
	# Save to CSV
	generated.to_csv(path_output, index=False)
	
	print("Generated parameter file saved as:", path_output)
	#print(generated)
