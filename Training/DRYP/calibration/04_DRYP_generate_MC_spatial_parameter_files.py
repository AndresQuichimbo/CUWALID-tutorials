import json
import numpy as np
import calendar
import pandas as pd
from shutil import copyfile
import fileinput
import sys
import os

def write_JSON_dryp_files(json_template, destination, model_name=None, path_pre=None, path_pet=None,
						   start_date=None, end_date=None, new_setting_file=None,
						   path_Qo=None, path_uz_theta=None, path_sz_wte=None, path_rp_theta=None,
						   path_pnd_Vo=None, path_outputs=None, parameter_factors=None,
						   spatial_factors=None):
	""" This function create the simulation and setting file for running DRYP. New
	files are created  based on files provided as original files, this function
	changes the model name, precipitation and potential evapotranspiration
	paths.
	WARNING: if no new filename is provided it will replace the original file
	
	Parameters:
	-----------
	json_template : string
			model input, as a dictionary
	model_name : string
			model name for the new file
	path_pre : string
			precipitation dataset name, including path
	path_pet : string
			potential evapotranspiration dataset name, including path
	start_date : string
			date in the following format "YYYY-MM-DD" (e.g. 2002-01-01)
	end_date : string
			date in the following format "YYYY-MM-DD" (e.g. 2002-03-01)
	new_setting_file : bool
			If True it create the setting dryp file
	destination : string
			destination path for the new dryp input file
	path_Qo : string
			initial channel storage dataset name, including path
	path_uz_theta : string
			initial unsaturated zone moisture content dataset name, including path
	path_sz_wte : string
			initial saturated zone water table elevation dataset name, including path
	path_rp_theta : string
			initial riparian zone moisture content dataset name, including path
	path_pnd_Vo : string
			initial ponds volume of water dataset name, including path
	path_outputs : string
			outputs folder path
	parameter_factors : dict
			dictionary containing the parameter factors to be updated in the settings file
	spatial_factors : dict
			dictionary containing the spatial factors to be updated in the input file
	Returns:
	--------
	None
	"""

	# Change necesarry variables in template
	if model_name is not None:
		json_template["model_name"] = model_name
	if path_pre is not None:
		json_template["METEO"]["path_pre"] = path_pre
	if path_pet is not None:
		json_template["METEO"]["path_pet"] = path_pet
	if path_Qo is not None:
		json_template["TERRAIN"]["path_Qo"] = path_Qo
	if path_uz_theta is not None:
		json_template["UNSATURATED"]["path_uz_theta"] = path_uz_theta
	if path_sz_wte is not None:
		json_template["SATURATED"]["path_sz_wte"] = path_sz_wte
	if path_rp_theta is not None:
		json_template["RIPARIAN"]["path_rp_theta"] = path_rp_theta
	if path_pnd_Vo is not None:
		json_template["WATER_BODIES"]["path_pnd_Vo"] = path_pnd_Vo
	if path_outputs is not None:
		json_template["OUTPUT"]["path_output"] = path_outputs
	if spatial_factors is not None:
		for ikey in spatial_factors.keys():
			json_template["CALIBRATION"][ikey] = spatial_factors[ikey]

	# create a new settings file only if the new setting file does not exist
	if new_setting_file is not None:

		# Get input file as dictionary
		settings_file_path = json_template["OUTPUT"]["path_setting"]
		with open(settings_file_path, 'r') as file:
			settings_file_template = json.load(file)
		# Change settings file location
		json_template["OUTPUT"]["path_setting"] = new_setting_file
		
		## Change variables in the settings file
		#json_template["dryp_settings"]["SIMULATION_PERIOD"]["start_date"] = start_date
		#json_template["dryp_settings"]["SIMULATION_PERIOD"]["end_date"] = end_date
		if start_date is not None:
			settings_file_template["SIMULATION_PERIOD"]["start_date"] = start_date
		if end_date is not None:
			settings_file_template["SIMULATION_PERIOD"]["end_date"] = end_date

		# Update parameter factors only if provided
		if parameter_factors is not None:
			for ikey in parameter_factors.keys():
				settings_file_template["GLOBAL_FACTORS"][ikey] = parameter_factors[ikey]
	
	# Save the `dryp` part to the destination file
	#dryp_data = json_template["dryp"]
	with open(destination, "w") as dest_file:
		#json.dump(dryp_data, dest_file, indent=4)
		json.dump(json_template, dest_file, indent=4)

	# Save the `dryp_settings` part to the new settings file
	if new_setting_file is not None:
		#dryp_settings_data = settings_file_template["dryp_settings"]
		#dryp_settings_data = json_template["dryp_settings"]
		with open(new_setting_file, "w") as settings_file:
			#json.dump(dryp_settings_data, settings_file, indent=4)
			json.dump(settings_file_template, settings_file, indent=4)

def save_df_row_values(df, row_selector=0, filepath="row_values.txt", sep=" "):
    """
    Save only the values of one row from a DataFrame to a text file.

    Parameters
    ----------
    df : pandas.DataFrame
        Source dataframe.
    row_selector : int or label
        If int -> uses df.iloc[row_selector]. Otherwise uses df.loc[row_selector].
    filepath : str
        Output text file path.
    sep : str
        Separator to place between values in the file.
    """
    # select row by iloc if integer, else by label with loc
    if isinstance(row_selector, (int,)):
        row = df.iloc[row_selector]
    else:
        row = df.loc[row_selector]

    values = row.values
    # write plain values (no header/index), joined by sep
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(sep.join(map(str, values)))


# Example usages:
# If a DataFrame named `df` already exists in the notebook:
# save_df_row_values(df, 0, "row0.txt", sep=",")
#
# Or for a row with label "station_1":
# save_df_row_values(df, "station_1", "station_1_values.txt", sep="\t")

def gen_array_input_files(fname_input, fname_parameter_sets, model_name, nmax=100, spatial_factors=None, path_cal_set=None):
	""" This function generate multiple input files for running DRYP in an array
	environment. It creates multiple input files and setting files based on a
	template input file and a set of parameter values provided in a csv file.
	Parameters:
	-----------
	fname_input : string
			template input file path
	fname_parameter_sets : string
			csv file containing the parameter sets
	model_name : string
			base model name for the new files
	nmax : int
			number of input files to be created
	spatial_factors : dict
			dictionary containing the spatial factors to be updated in the input file
			if None, the parameter sets are used to update the global factors in the
			settings file
	path_cal_set : string
			path to the folder containing the calibration set files. If provided,
			the parameter sets file is ignored and the spatial factors are used.
	Returns:
	--------
	None
	"""
    # open input file
	with open(fname_input, 'r') as file:
		input_template = json.load(file)
    
	# read parameter sets
	parameter = pd.read_csv(fname_parameter_sets)
	
	setting_file = input_template["OUTPUT"]["path_setting"] 
	#Create a copy of inputfile
	fname_root = fname_input.split('.')[0]
	#fname_ext = fname_input.split('.')[1]
	
	fname_root_settings = setting_file.split('.')[0]
	for npar in range(0, nmax):
		# new input file name
		newfname_input = fname_root + '_' + str(npar) + '.json'
		imodel_name = model_name + "_" + str(npar)
		
		# new setting file
		new_setting_file = fname_root_settings + '_' + str(npar) + '.json'

		if spatial_factors is not None:
			# generate calibration set files
			ifname_set = os.path.join(path_cal_set,f"row_{npar}.txt")
			save_df_row_values(parameter, npar, ifname_set, sep=",")
			calibration_set = {}
			for ikey in spatial_factors.keys():
				calibration_set[ikey] = ifname_set
			# do not create new setting file
			new_setting_file = None
			parameter_factors = None
		else:
			calibration_set = None
			parameter_factors = dict(parameter.loc[npar])
		
		# replace all new values in dataset
		print(imodel_name)
		write_JSON_dryp_files(input_template, newfname_input, 
						new_setting_file=new_setting_file,
						model_name=imodel_name,
						parameter_factors= parameter_factors,
						spatial_factors=calibration_set,
						)
						
### ==================================================================
# Code start here
### ==================================================================
# Input parameters dictionary, comment the ones not used
icalibration_set = {
    #"path_cal_of_zone": None,
    #"path_cal_of_set": None,
    #"path_cal_uz_zone": None,
    "path_cal_uz_set": None,
    #"path_cal_sz_zone": None,
    #"path_cal_sz_set": None,
    #"path_cal_rp_zone": None,
    #"path_cal_rp_set": None,
    #"path_cal_st_zone": None,
    #"path_cal_st_set": None
}

# ========================================================
# LOOP FOR CREATING MULTIPLE IMPORT FILES FOR RUNNING IN HPC
fname = [
#basin_path +'model/HAD_IMERGcv_input_sim85.json',
#regional_path +'model/HAD_IMERGcv_input_sim85.json',
"/user/work/km19051/HAD_basin/Juba/JU_HAD_IMERGcv_input_sim85_lks_sim.json"
]

path_spatial_paramters = "/user/work/km19051/HAD_basin/calibration/HAD_spatial_parameter_range_file_JU.csv"

# it will not change the parameters in the settings file
#fname_parameter_sets = training_general_path + "/basin/dataset/csv/test_parameter_set.csv"
fname_parameter_sets = None

# location of parameter sets fo each simulation
#path_cal_set = regional_path + "/model/calibration_sets/"
path_cal_set = "/user/work/km19051/HAD_basin/calibration/calibration_sets/"

for ifname in fname:
	gen_array_input_files(ifname, path_spatial_paramters, "JU_HAD_IMERGcv_input_sim85", nmax=100,
					   spatial_factors=icalibration_set, path_cal_set=path_cal_set)