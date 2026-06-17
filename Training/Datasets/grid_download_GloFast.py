import cdsapi
import os
c = cdsapi.Client()

process = 7

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
#area = [-1.48, 37.08, -1.52, 37.12] #Kenya_lake -1.494148, 37.098323, lat, lon
#area = [37.2, 60.3, 23.2, 78.0] # Pakistan
#area = [32, 75.5, 33, 76.5] # Pakistan
area = [37.2, 66.0, 23.2, 82.6] # indus basin

			
if process == 7:
	for i in range(1983, 2025):

		month = ['01','02','03',
				'04',
				'05',
				'06',
				'07',
				'08','09',
				'10','11','12'
				]
		
		for imonth in month:
            # set filename
			filename = '/home/c1755103/dataset/glofast/PK_discharge_'+str(i)+'_'+str(imonth)+'.nc'
			
			if os.path.exists(filename):
				print("File already exist ", filename)
			else:
				dataset = "cems-glofas-historical"
				
				request = {
                        "system_version": ["version_4_0"],
                        "hydrological_model": ["lisflood"],
                        "product_type": ["consolidated"],
                        "variable": [
                            "river_discharge_in_the_last_24_hours",
                        #    "runoff_water_equivalent"
                        ],
						'data_format':'netcdf',
						'area': area,
						#'variable':[
						#	"runoff_water_equivalent"],
						'hyear': [str(i)],
						'hmonth': [imonth],
						'hday':[
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
							]
						}
				
				c.retrieve(dataset, request, filename)#.download()
				#print(c.retrieve)
				print(filename, "  File downloaded")
