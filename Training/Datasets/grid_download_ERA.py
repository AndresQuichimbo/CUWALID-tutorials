#-110.21/31.780/-109.87/31.66
import cdsapi
import os

# before running this script, make sure you have installed the cdsapi
# package and configured your CDS API key in the .cdsapirc file.
# check the documentation for more information:
# https://cds.climate.copernicus.eu/how-to-api

# create a client instance
c = cdsapi.Client()
# this will use the default URL and key from your .cdsapirc file,
# but you can also specify them explicitly:
c = cdsapi.Client(url="https://cds.climate.copernicus.eu/api")

#years_data = [2012,2013,2014]

process = 7
#format [ulat, llon, llat, rlon]
lat_min = -6.95
lat_max = 15.55
lon_min = 28.05
lon_max = 53.15

# locations
#format [ulat, llon, llat, rlon]
#area = 15.5, 32.0/-5.65/52.0',# Mark lat 52.81, lon -2.57
#area = 53.0, -2.75/52.75/-2.5',# Mark lat 52.81, lon -2.57
#area = 51.5, -3.2/51.3/-3.1',# cardiff 51.5/-3.2/51.3/-3.1
#area = 53.1, -4.2/53.0/-4.1',# snowdonia 51.5/-3.2/51.3/-3.1
#area = 51.5, -3.2/51.3/-3.1',# cardiff 51.5/-3.2/51.3/-3.1
#area = -1.0, 35/-2/36',# San River
#area = 2.00, 36/-1/38',# Ewaso
#area = [37.04, 27.28, 36.96, 27.34] # Kos
#area = [32, 70, 30, 72] # pakistan - zoom in
#area = [37.2, 60.3, 23.2, 78.0] # Pakistan
#area = [32, 75.5, 33, 76.5] # Pakistan

area = [lat_max, lon_min, lat_min, lon_max] # Defined by lat_min, lat_max, lon_min, lon_max
			
if process == 7:
	for i in range(2026, 2027):

		month = ['01','02','03',
				'04',
				'05',
				'06',
				'07',
				'08','09',
				'10','11','12'
				]
		
		for imonth in month:
		
			#filename = 'D:/ERA/HAD/pre/HAD_pre_'+str(i)+'_'+str(imonth)+'_h.nc'
			#filename = '/home/c1755103/dataset/era/PK_cloud_'+str(i)+'_'+str(imonth)+'_hp.nc'
			#filename = '/home/c1755103/dataset/era/PK_meteo_'+str(i)+'_'+str(imonth)+'_pm.nc'
			filename = '/share/home/c1755103/dataset/ERA_temp/HAD_meteo_'+str(i)+'_'+str(imonth)+'_pm.nc'
			
			if os.path.exists(filename):
				print("File already exist ", filename)
			else:
				#'reanalysis-era5-land',
				dataset = "reanalysis-era5-land"
				#dataset = 'reanalysis-era5-single-levels'
	
				request = {
						"download_format": "unarchived",
						#'product_type': 'reanalysis', # for single levels
						'data_format':'netcdf',
						'area': area,
						'variable':[
							'10m_u_component_of_wind',
							'10m_v_component_of_wind',
							'2m_dewpoint_temperature',
							'2m_temperature',
							'surface_net_solar_radiation',
							'surface_net_thermal_radiation',
							'surface_pressure',
							#'total_precipitation'
							#'total_cloud_cover'
							#from single levels reanalysis
							],
						'year': [str(i)],
						'month': [imonth],
						'day':[
							'01','02','03',
							'04','05','06',
							'07','08','09',
							'10','11',
							'12',
							'13','14','15',
							'16','17','18',
							'19','20','21',
							'22','23','24',
							'25','26','27',
							'28','29','30',
							'31'
							],
						'time':[
							'00:00','01:00','02:00',
							'03:00','04:00','05:00',
							'06:00','07:00','08:00',
							'09:00','10:00','11:00',
							'12:00','13:00','14:00',
							'15:00','16:00','17:00',
							'18:00','19:00','20:00',
							'21:00','22:00','23:00'
							]
						}
				
				c.retrieve(dataset, request, filename)#.download()
				#print(c.retrieve)
				print(filename, "  File downloaded")