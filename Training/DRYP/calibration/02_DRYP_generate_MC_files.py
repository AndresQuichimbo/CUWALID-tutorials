import os
import json
import numpy as np
import pandas as pd

def write_JSON_dryp_files(json_template, destination, model_name=None, path_pre=None, path_pet=None,
						   start_date=None, end_date=None, new_setting_file=None,
						   path_Qo=None, path_uz_theta=None, path_sz_wte=None, path_rp_theta=None,
						   path_pnd_Vo=None, path_outputs=None, parameter_factors=None):
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

def gen_array_input_files(fname_input, fname_parameter_sets, model_name, nmax=100):
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
		
		# replace all new values in dataset
		print(imodel_name)
		write_JSON_dryp_files(input_template, newfname_input, 
						new_setting_file=new_setting_file,
						model_name=imodel_name,
						parameter_factors=dict(parameter.loc[npar]))

	
# =======================================================================
# LOOP FOR CREATING MULTIPLE IMPORT FILES FOR RUNNING IN HPC


fname = [
#basin_path +'model/HAD_IMERGcv_input_sim85.json',
#regional_path +'model/HAD_IMERGcv_input_sim85.json',
"/user/work/km19051/HAD_basin/Juba/JU_HAD_IMERGcv_input_sim85_lks.json"
]

#fname_parameter_sets = training_general_path + "/basin/dataset/csv/test_parameter_set.csv"
fname_parameter_sets = "/user/work/km19051/HAD_basin/calibration/HAD_parameter_range_file_JU.csv"

for ifname in fname:
	gen_array_input_files(ifname, fname_parameter_sets,
		"JU_HAD_IMERGcv_input_sim85_lks",
		nmax=100)
	