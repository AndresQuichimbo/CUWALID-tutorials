import os
import json
import numpy as np
import calendar
import pandas as pd

def write_JSON_dryp_files(json_template, model_name, path_pre, path_pet, destination,
						   start_date="2024 03 01", end_date="2024 05 31", new_setting_file=None,
						   path_Qo=None, path_uz_theta=None, path_sz_wte=None, path_rp_theta=None,
						   path_pnd_Vo=None, path_outputs=None):
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
	

	# create new settings file
	if new_setting_file is not None:

		# Get input file as dictionary
		settings_file_path = json_template["OUTPUT"]["path_setting"]
		with open(settings_file_path, 'r') as file:
			settings_file_template = json.load(file)
		# Change settings file location
		json_template["OUTPUT"]["path_setting"] = new_setting_file
		
		## Change variables in settings file
		#json_template["dryp_settings"]["SIMULATION_PERIOD"]["start_date"] = start_date
		#json_template["dryp_settings"]["SIMULATION_PERIOD"]["end_date"] = end_date
		if start_date is not None:
			settings_file_template["SIMULATION_PERIOD"]["start_date"] = start_date
		if end_date is not None:
			settings_file_template["SIMULATION_PERIOD"]["end_date"] = end_date


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


def gen_inital_end_simulation_dates(year, month, day, dtyear=1, dtmonth=0, dtday=0):
	"""This function gets the initial and end date of a specified period
	"""
	date_ini = str(year+dtyear) + ' ' + str(month+dtmonth) + ' ' + str(day+dtday)
	date_end = str(year+dtyear+1) + ' ' + str(month+dtmonth) + ' ' + str(day+dtday)
	
	name = str(year)
	name_end = str(year+dtyear)
	
	return date_ini, date_end, name, name_end

def gen_pipeline_dryp_files(path_json_template, path_outputs=None, model_name=None, start_year=2000, end_year=2026):
	
	# Get input file as dictionary
	with open(path_json_template, 'r') as file:
		json_template = json.load(file)
	if path_outputs is None:
		path_outputs = json_template["OUTPUT"]["path_output"]
	
	# get path, filename and model name
	path, file = os.path.split(path_json_template)
	
	# identify filename of paramter file
	if model_name is None:
		model_name = file.split('.')[0]
	#else:
	#	mname = model_name
	
	# avoid updating forcing dataset
	path_pre, path_pet = None, None	
	
	# iterate over the simulatio period
	for i, iyear in enumerate(range(start_year, end_year)):
		mname = model_name + "_" + str(iyear)
		path_new_input = path + "/" + mname + ".json"
		path_new_settings = path + "/"  + mname + "_settings.json"
		# get name of initial conditions
		# skip if the initial year
		if i != 0:
			mname0 = model_name + "_" + str(iyear-1)
			path_Qo = path_outputs + '/'+ mname0 +'_avg_Q_ini.asc'
			path_uz_theta = path_outputs + '/'+ mname0 +'_avg_tht_ini.asc'
			path_sz_wte = path_outputs + '/'+ mname0 +'_avg_wte_ini.asc'
			path_rp_theta = path_outputs + '/'+ mname0 + '_avg_tht_rp_ini.asc'
			path_pnd_Vo = path_outputs + '/' + mname0 + '_avg_V_pnd_ini.asc'
		else:
			path_Qo=None
			path_uz_theta=None
			path_sz_wte=None
			path_rp_theta=None
			path_pnd_Vo=None
		
		# get simulation period
		if i == 0:
			date_ini, date_end = None, None
		else:
			date_ini, date_end, name, name_end = gen_inital_end_simulation_dates(iyear-1, 1, 1)
		#print(#json_template,
		#		mname, #path_pre,# path_pet,
		#					path_new_input,
		#				   #start_date, end_date,
		#				   path_new_settings,
		#				   path_Qo,
		#				   path_uz_theta,
		#				   path_sz_wte,
		#				   path_rp_theta,
		#				   path_pnd_Vo
		#				   )
		
		
		write_JSON_dryp_files(json_template, mname, path_pre, path_pet, path_new_input,
						   start_date=date_ini, end_date=date_end, new_setting_file=path_new_settings,
						   path_Qo=path_Qo,
						   path_uz_theta=path_uz_theta,
						   path_sz_wte=path_sz_wte,
						   path_rp_theta=path_rp_theta,
						   path_pnd_Vo=path_pnd_Vo
						   )

# ========================================================
# LOOP FOR CREATING MULTIPLE IMPOT FILES FOR RUNNING IN HPC
# write here the name of the initial file, which will be used to create the subsequent files for the simulation
fname = [
#"/user/work/km19051/HAD/HAD_IMERG_input_sim_"+str(i)+".json" for i in range(31, 43) 
"/home/c1755103/HAD/HAD_IMERGcv_input_sim85_lks.json" 
]

# WARNINGS
# The initial file should specify the initial conditions at the beginning of
# the simulation of the entire period, therefore, the name of initial model
# must be according to the name required to the next simulation.
# Subsequent period must consider the initial conditions from the previous period.

# write here the path where the output files will be saved, if None it will be
# the same as specified in the initial file
path_outputs = "/home/c1755103/HAD/HAD_output"

for ifname_input in fname:
	gen_pipeline_dryp_files(ifname_input, path_outputs)