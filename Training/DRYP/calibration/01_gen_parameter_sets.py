"""
this file creates input files for scaling
analysis, at walnut gulch catchement
"""


import os
import pandas as pd
import numpy as np

GLOBAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
GLOBAL_PATH = "/home/chc-andres/AF/datasets/calibration/csv/"
# Number of samples to generate (you can change this)
n_samples = 10 

# Read ranges of parameter file for model simulations
fname = GLOBAL_PATH + "AF_parameter_range_file.csv"
##fname = "C:/Users/km19051/OneDrive - Cardiff University/PhD/WS/LandLab/HAD/WS/input_model/HAD_parameter_range_file.csv"

# check if the file exists
if not os.path.exists(fname):
	# create a new file with the specified ranges
	df = pd.DataFrame({
		"Grid": ["1km", "1km"],
		"tstep": [1, 1],
		"model": ["AF", "AF"],
		"type": ["min", "max"],
		"uz_kdroot": [1.0, 1.5],
		"uz_kkast": [0.1, 0.5],
		"riv_kksat": [0.2, 0.6],
		"sz_kksat": [0.3, 0.7],
		"sz_ksy": [0.5, 1.3],
	})
	df.to_csv(fname, index=False)
	print(f"File {fname} not found. A new file has been created with default ranges. Please check and modify the ranges as needed.")
else:
	print(f"Found the file {fname}. Proceeding with parameter generation.")
	# Read CSV file
	df = pd.read_csv(fname)

# Drop non-numeric / fixed columns
fixed_cols = ["Grid", "tstep", "model", "type"]
param_cols = [c for c in df.columns if c not in fixed_cols]

# get list of model to generate parameter sets
label_model = df["model"].unique()

# loop through each model and generate parameter sets
for ilabel_model in label_model:
	
	# Read CSV file
	#df = pd.read_csv(fname)
	
	# path output
	path_output = fname.split('.')[0] + '_' + 'sets.csv'

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
