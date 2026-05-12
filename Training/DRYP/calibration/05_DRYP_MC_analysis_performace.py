# ====================== Libraries =====================
import os
import sys
import numpy as np
import time
import pandas as pd
import datetime
from datetime import timedelta
import index_goodness_fit as gen
from scipy import stats


# ====================== Helpers =====================
def get_date_range(fname, timefield='Date'):
    """Return min and max datetime in a file."""
    df = pd.read_csv(fname)
    df[timefield] = pd.to_datetime(df[timefield], dayfirst=True, errors='coerce')
    df = df.dropna(subset=[timefield])
    return df[timefield].min(), df[timefield].max()


def get_common_date_range(file_timefield_pairs, min_start="2012-01-01"):
    """Find common overlapping period across multiple files."""
    starts, ends = [], []
    for f, tfield in file_timefield_pairs:
        if os.path.exists(f):
            try:
                dmin, dmax = get_date_range(f, timefield=tfield)
                starts.append(dmin)
                ends.append(dmax)
            except Exception as e:
                print(f"?? Could not read {f} ({tfield}): {e}")

    if not starts or not ends:
        return None, None

    # enforce restriction: start >= min_start
    min_start = pd.to_datetime(min_start)
    start = max(max(starts), min_start)
    end = min(ends)

    if start >= end:  # no overlap
        return None, None
    return start, end


def aggregate_slice_csv(fname, agg_step='ME', mean=True, cumsum=False,
                        date_start=None, date_end=None,
                        timefield='Date', renamefield=True):
	"""Read, slice, and aggregate a CSV file consistently."""
	df = pd.read_csv(fname)
	df[timefield] = pd.to_datetime(df[timefield], format='mixed')#dayfirst=True, errors='coerce')
	df = df.dropna(subset=[timefield])

	if date_start is not None and date_end is not None:
		df = df[df[timefield].between(date_start, date_end)]

	df.index = pd.DatetimeIndex(df[timefield])
	df = df.drop([timefield], axis=1)

	if mean:
		df = df.resample(agg_step).mean(numeric_only=True)
	else:
		df = df.resample(agg_step).sum(numeric_only=True)

	if cumsum:
		df = df.cumsum()

	df = df.reset_index()
	if renamefield is True:
		try:
			df.rename(columns={timefield: 'Date'})
		except:
			pass
	return df


def slope_ratio(obs, sim):
    ind = np.where(np.isnan(obs) == False)[0]
    x = np.arange(len(ind))
    return np.polyfit(x, obs[ind], 1)[0] / np.polyfit(x, sim[ind], 1)[0]

def merge_dataframes(df1, df2):
	# Make sure 'Date' is an index
	df1 = df1.set_index('Date')
	df2 = df2.set_index('Date')

	# Concatenate the dataframes
	merged_df = pd.concat([df1, df2], axis=1, join='inner')
	return merged_df

# ====================== Basin Data Class =====================
class basin_data():
    def __init__(self, ibasin):
        if ibasin == "Tana":
            self.fdis = ["/user/work/km19051/basin_data/streamflow/KE_Garissa_4G01.csv"]
            self.ftht = "/user/work/km19051/basin_data/HAD_Tana_ESA.csv"
            self.faet = "/user/work/km19051/basin_data/HAD_Tana_GLEAM.csv"
            self.ftws = "/user/work/km19051/basin_data/HAD_Tana_GRACE.csv"
            self.fdiss = "/user/work/km19051/HAD_basin/output/Tana_IMa_simNN_p_dis.csv"
            self.favgs = "/user/work/km19051/HAD_basin/output/Tana_IMa_simNN_avg.csv"
            self.favgr = "/user/work/km19051/HAD_basin/output/Tana_IMa_simNN_RZ_avg.csv"
            self.IFIELD = ['flow_m3_s']
            self.nameTime = ['Date']
            self.dis_var = ["dis_0"]

        elif ibasin == "Juba":
            self.fdis = [
                "/user/work/km19051/basin_data/streamflow/river-juba-at-luuq_flow.csv",
                "/user/work/km19051/basin_data/streamflow/river-juba-at-bardheere_flow.csv",
            ]
            self.ftht = "/user/work/km19051/basin_data/HAD_Juba_ESA.csv"
            self.faet = "/user/work/km19051/basin_data/HAD_Juba_GLEAM.csv"
            self.ftws = "/user/work/km19051/basin_data/HAD_Juba_GRACE.csv"
            self.fdiss = "/user/work/km19051/HAD_basin/output/JU_HAD_IMERGcv_input_sim85_lks_NN_p_dis.csv"
            self.favgs = "/user/work/km19051/HAD_basin/output/JU_HAD_IMERGcv_input_sim85_lks_NN_avg.csv"
            self.favgr = "/user/work/km19051/HAD_basin/output/JU_HAD_IMERGcv_input_sim85_lks_NN_avgrp.csv"
            self.IFIELD = ['flow(m3/s)', 'flow(m3/s)']
            self.nameTime = ['Date', "Date"]
            self.dis_var = ["dis_5", "dis_3"]

        elif ibasin == "Shabelle":
            self.fdis = [
                "/user/work/km19051/basin_data/streamflow/shabelle-at-belet_flow.csv",
                "/user/work/km19051/basin_data/streamflow/shabelle-at-bulo-b_flow.csv",
            ]
            self.ftht = "/user/work/km19051/basin_data/HAD_Shabelle_ESA.csv"
            self.faet = "/user/work/km19051/basin_data/HAD_Shabelle_GLEAM.csv"
            self.ftws = "/user/work/km19051/basin_data/HAD_Shabelle_GRACE.csv"
            self.fdiss = "/user/work/km19051/HAD_basin/output/Shabelle_IM_simNN_p_dis.csv"
            self.favgs = "/user/work/km19051/HAD_basin/output/Shabelle_IM_simNN_avg.csv"
            self.favgr = "/user/work/km19051/HAD_basin/output/Shabelle_IM_simNN_RZ_avg.csv"
            self.IFIELD = ['flow(m3/s)', 'flow(m3/s)']
            self.nameTime = ['Date', 'Date']
            self.dis_var = ["dis_1", "dis_0"]

        elif ibasin == "Kenya":
            self.fdis = ["/user/work/km19051/basin_data/streamflow/A0_Archers_Post.csv"]
            self.ftht = "/user/work/km19051/basin_data/HAD_Kenya_ESA.csv"
            self.faet = "/user/work/km19051/basin_data/HAD_Kenya_GLEAM.csv"
            self.ftws = "/user/work/km19051/basin_data/HAD_Kenya_GRACE.csv"
            self.fdiss = "/user/work/km19051/HAD_basin/output/Kenya_IMb_simNN_p_dis.csv"
            self.favgs = "/user/work/km19051/HAD_basin/output/Kenya_IMb_simNN_avg.csv"
            self.favgr = "/user/work/km19051/HAD_basin/output/Kenya_IMb_simNN_RZ_avg.csv"
            self.IFIELD = ['Discharge']
            self.nameTime = ['Date']
            self.dis_var = ["dis_0"]


# ====================== Main Loop =====================
basin = ["Tana", 'Juba', 'Shabelle', 'Kenya']
basin = ['Juba',]

for ibasin in basin:
	cth = basin_data(ibasin)
	fout = "/user/work/km19051/HAD_basin/postpp/csv/"
	fname_out = fout + ibasin + "_MCa_indices.csv"

	# --- find common overlapping period ---
	file_timefield_pairs = [
		(cth.fdis[-1], cth.nameTime[-1]),
		(cth.faet, 'Date'),
		(cth.ftht, 'Date'),
		(cth.ftws, 'Date'),
		(cth.fdiss.replace("NN", "0"), 'Date'),
		(cth.favgs.replace("NN", "0"), 'Date'),
		(cth.favgr.replace("NN", "0"), 'Date'),
	]
	date_start, date_end = get_common_date_range(file_timefield_pairs)#, min_start="2000-12-31")

	if date_start is None or date_end is None:
		print(f"?? Skipping {ibasin}: no valid overlapping period found")
		continue

	print(f"{ibasin}: common period {date_start} ? {date_end}")
	date_start, date_end = "2012-01-01", "2024-12-31"
	# --- read obs data consistently ---
	#dis = aggregate_slice_csv(cth.fdis[-1], timefield=cth.nameTime[-1],
	#						date_start=date_start, date_end=date_end)[['Date', cth.IFIELD[-1]]]#.values
	aet = aggregate_slice_csv(cth.faet, date_start=date_start, date_end=date_end)[['Date', "aet"]]#.values
	tht = aggregate_slice_csv(cth.ftht, date_start=date_start, date_end=date_end)[['Date', "tht"]]#.values
	tws = aggregate_slice_csv(cth.ftws, date_start=date_start, date_end=date_end)[['Date', "twsc"]]#.values

	variables = {"Q_mean": True, "Q_KGE": True, "Q_NSE": True,
				#"Q_logKGE": True, "Q_logNSE": True,
				"tht_r": True,
				"aet_r": True, "aet_KGE": True,
				"tws_r": True, "tws_KGE": True, "tws_SR": True}
				
	
	#print(aggregate_slice_csv(cth.fdis[-1], timefield=cth.nameTime[-1],
	#						date_start=date_start, date_end=date_end).head(-10))
	
	label_dis_all = []
	for j, idis_var in enumerate(cth.dis_var):
		label_dis = ["Q_mean", "Q_KGE", "Q_NSE"]		
		#label_dis_name = [ilabel_dis+str(j) 
		for ilabel_dis in label_dis:
			label_dis_all.append(ilabel_dis+str(j))
		
	#print(label_dis_all)
	label_dis_all = label_dis_all + ["tht_r", "aet_r", "aet_KGE",
				"tws_r", "tws_KGE", "tws_SR"]
				
	dis_units = 1/30.5/86400
	dfindices = pd.DataFrame()
	var_s = ["pre", "inf", "aet", "rch", "tls"]
	var_r = ["ssz"]

	for isim in range(100):
		ifdis = cth.fdiss.replace("NN", str(isim))
		ifaet = cth.favgs.replace("NN", str(isim))
		iftws = cth.favgs.replace("NN", str(isim))
		iftht = cth.favgs.replace("NN", str(isim))
		ifavr = cth.favgr.replace("NN", str(isim))
		
		#if os.path.exists(ifdis) and os.path.exists(ifavr) and os.path.exists(ifaet):
		try:
			indices = [isim]

			# add water balance (s variables)
			for ivar in var_s:
				indices.append(np.mean(
					aggregate_slice_csv(ifaet, mean=False, date_start=date_start, date_end=date_end)[ivar+"_0"].values))

			# add water balance (r variables)
			for ivar in var_r:
				indices.append(np.mean(
					aggregate_slice_csv(ifavr, mean=True, date_start=date_start, date_end=date_end)[ivar+"_0"].values))

			for idis, ifdis_obs, idis_obs, idtime_obs in zip(cth.dis_var, cth.fdis, cth.IFIELD, cth.nameTime):
				#read observation
				#print(ifdis_obs)
				dis = aggregate_slice_csv(
						ifdis_obs, date_start=date_start, date_end=date_end, timefield=idtime_obs)#[['Date', idis_obs]]
				dis = dis.rename(columns={idtime_obs: 'Date'})
				dis = dis[['Date', idis_obs]]
				#print(dis)
				# read simulations and merge with observation
				merge_Q = merge_dataframes(dis, aggregate_slice_csv(
						ifdis, date_start=date_start, date_end=date_end)[['Date', idis]])
			
				# discharge mean
				if variables['Q_mean']:
					indices.append(np.mean(
						aggregate_slice_csv(
							ifdis, date_start=date_start, date_end=date_end)[idis].values * dis_units))
	
				# KGE	
				if variables['Q_KGE']:
					indices.append(gen.KGE(merge_Q[idis_obs].values, merge_Q[idis].values*dis_units))
	
				# NSE
				if variables['Q_NSE']:
					indices.append(gen.NSE(merge_Q[idis_obs].values, merge_Q[idis].values*dis_units))

				## log-KGE
				#if variables['Q_logKGE']:
				#	indices.append(gen.KGE(np.log10(dis),
				#		np.log10(aggregate_slice_csv(ifdis, date_start=date_start, date_end=date_end)[cth.dis_var[-1]].values * dis_units)))
				#
				## log-NSE
				#if variables['Q_logNSE']:
				#	indices.append(gen.NSE(np.log10(dis),
				#		np.log10(aggregate_slice_csv(ifdis, date_start=date_start, date_end=date_end)[cth.dis_var[-1]].values * dis_units)))

			# correlations
			merge_tht = merge_dataframes(tht, aggregate_slice_csv(iftht, date_start=date_start, date_end=date_end)[['Date', 'tht_0']])
			#print(merge_tht)
			if variables['tht_r']:
				indices.append(gen.pearsonr(merge_tht['tht'].values, merge_tht['tht_0'].values)[0])

			merge_aet = merge_dataframes(aet, aggregate_slice_csv(ifaet, date_start=date_start, date_end=date_end)[['Date', 'aet_0']])

			if variables['aet_r']:
				indices.append(gen.pearsonr(merge_aet['aet'].values, merge_aet['aet_0'].values)[0])

			if variables['aet_KGE']:
				indices.append(gen.KGE(merge_aet['aet'].values, merge_aet['aet_0'].values))
			
			merge_tws = merge_dataframes(tws, aggregate_slice_csv(iftws, cumsum=True, date_start=date_start, date_end=date_end)[['Date', 'twsc_0']])
			
			if variables['tws_r']:
				indices.append(gen.pearsonr(merge_tws['twsc'].values, merge_tws['twsc_0'].values)[0])

			if variables['tws_KGE']:
				indices.append(gen.KGE(merge_tws['twsc'].values*10.0, merge_tws['twsc_0'].values))

			if variables['tws_SR']:
				indices.append(slope_ratio(merge_tws['twsc'].values*10.0, merge_tws['twsc_0'].values))

			# save
			print(indices)
			#columnames = list(variables.keys())
			#df = pd.DataFrame(data=[indices], columns=['Sim']+label_dis_all+var_s+var_r+columnames)
			df = pd.DataFrame(data=[indices], columns=['Sim']+var_s+var_r+label_dis_all)
			dfindices = pd.concat([dfindices, df], ignore_index=True)
		#else:
		except:
			print('Simulation does not exist: ' , str(isim))

	# save dataset
	dfindices.to_csv(fname_out, index=False)
