import os
import sys
import h5py
import requests
import numpy as np
import xarray as xr
from tqdm import tqdm
from datetime import datetime, timedelta


sys.path.append("Training/Datasets/")
import AQ_credentials as NN_credentials # contains your IMERG credentials, use your own credentials in a separate file named AQ_credentials.py
#import NN_credentials as NN_credentials # uncomment this line if you are using NN_credentials.py for NOAA credentials
# This should be a separate file containing your IMERG credentials
# It should define USERNAME_IMERG and PASSWORD_IMERG variables

def first_days_between(start_date, end_date):
    # Ensure start_date is the first day of its month
    if start_date.day != 1:
        start_date = datetime(start_date.year, start_date.month, 1)
        if start_date < date.today():
            pass  # No change needed here unless you want to shift to next month

    # Move to the first of the next month if start_date is before the given start
    if start_date < datetime(start_date.year, start_date.month, 1):
        start_date = datetime(start_date.year + (start_date.month // 12), 
                          ((start_date.month % 12) + 1), 1)

    # Generate list
    first_days = []
    current = datetime(start_date.year, start_date.month, 1)
    while current <= end_date:
        first_days.append(current)
        # Move to first of next month
        year = current.year + (current.month // 12)
        month = (current.month % 12) + 1
        current = datetime(year, month, 1)
    
    return first_days


# ==== CONFIG ====
#1. Set your IMERG credentials in AQ_credentials.py
USERNAME = NN_credentials.USERNAME_IMERG
PASSWORD = NN_credentials.PASSWORD_IMERG

# 2. Set bounding box for study site
# Bounding box
lat_min = -6.95
lat_max = 15.55
lon_min = 28.05
lon_max = 53.15
# extend = [lon_nin, lat_min, lon_max, lat_max]
#bounds=[35.0, -4.10, 53.15, 13.55] # HAD

# 3. Select the period of interest
# Time range (1 month)
start_date = datetime(2025, 10, 1)
end_date   = datetime(2027, 1, 1)

# 4. Select the IMERG product type
# Choose: 'Early', 'Late', or 'Final'
PRODUCT_TYPE = 'Late' 

# 5. Set output directory
output_dir = "/share/home/c1755103/dataset/IMERG/"
#output_dir = "/user/work/km19051/dataset/IMERG/"


# DO NOT MODIFY BELOW THIS LINE UNLESS YOU KNOW WHAT YOU ARE DOING =========
os.makedirs(output_dir, exist_ok=True)

local_path = os.path.join(output_dir,"raw")
os.makedirs(local_path, exist_ok=True)

print('Raw data will be stored in: ', local_path)
print('Monthly data will be stored in: ', output_dir)

# DO NOT MODIFY FROM HERE
# IMERG V07 30-min grid definition
lat = np.arange(-89.95, 90, 0.1)  # 1800 points
lon = np.arange(-179.95, 180.0, 0.1)    # 3600 points

# Find nearest grid cell indices for bbox corners
lat_min_idx = int(np.argmin(np.abs(lat - lat_min)))
lat_max_idx = int(np.argmin(np.abs(lat - lat_max)))
lon_min_idx = int(np.argmin(np.abs(lon - lon_min)))
lon_max_idx = int(np.argmin(np.abs(lon - lon_max)))


# Map product names to directory names
product_map = {
    'Early': 'GPM_3IMERGHHE.07',
    'Late':  'GPM_3IMERGHHL.07',
    'Final': 'GPM_3IMERGHH.07'
}

product_dir = product_map.get(PRODUCT_TYPE)
base_url = f"https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/{product_dir}"

# HAD
#https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.07/2025/089/3B-HHR.MS.MRG.3IMERG.20250330-S000000-E002959.0000.V07B.HDF5.nc4?
#precipitation[0:0][2150:2331][858:1035],time,lon[2150:2331],lat[858:1035]

#https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.07/
#2023/001/
#3B-HHR.MS.MRG.3IMERG.
#20230101-S000000-E002959.0000.V07B.HDF5.nc4?precipitation[0:0]
#[2079:2320][829:1054],time,
#lon[2079:2320],lat[829:1054]
#url_aggregation = "?precipitation[0:0][2079:2320][829:1054],time,lon[2079:2320],lat[829:1054]"
url_aggregation = f"?precipitation[0:0][{lon_min_idx}:{lon_max_idx}][{lat_min_idx}:{lat_max_idx}],time,lon[{lon_min_idx}:{lon_max_idx}],lat[{lat_min_idx}:{lat_max_idx}]"

#https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.07/2023/001/3B-HHR.MS.MRG.3IMERG.20230101-S000000-E002959.0000.V07B.HDF5.nc4?precipitation[0:0][2079:2320][829:1054],time,lon[2079:2320],lat[829:1054]
#https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.07/2023/001/3B-HHR.MS.MRG.3IMERG.20230101-S003000-E005959.0030.V07B.HDF5.nc4?precipitation[0:0][2079:2320][829:1054],time,lon[2079:2320],lat[829:1054]
#https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGHH.07/2023/001/3B-HHR.MS.MRG.3IMERG.20230101-S010000-E012959.0060.V07B.HDF5.nc4?precipitation[0:0][2079:2320][829:1054],time,lon[2079:2320],lat[829:1054]

# Adjust filename pattern based on run type
# Filenames for Early/Late use 'E' or 'L' instead of 'MRG'/'V07B' variations in some cases.
# Ensure you verify the exact naming convention in your specific directory.
# Example:
# 	Final: 3B-HHR.MS.MRG.3IMERGE.20230101-S000000-E002959.0000.V07B.HDF5.nc4
#	Late: 3B-HHR-L.MS.MRG.3IMERG.20251228-S000000-E002959.0000.V07B.HDF5
#	Early: 3B-HHR-E.MS.MRG.3IMERG.20251228-S000000-E002959.0000.V07B.HDF5
run_char = '-E' if PRODUCT_TYPE == 'Early' else ('-L' if PRODUCT_TYPE == 'Late' else '')

session = requests.Session()
session.auth = (USERNAME, PASSWORD)

dates_list = first_days_between(start_date, end_date)

for i, istart_date in enumerate(dates_list[:-1]):

	# Time range (1 month)
	iend_date = dates_list[i+1]
	
	precip_data = []
	time_data = []
	lat_slice = None
	lon_slice = None
	
	delta_time = 0
	current = istart_date
	while current <= iend_date:
		yyyy = current.strftime("%Y")
		mm = current.strftime("%m")
		dd = current.strftime("%d")
		hh = current.strftime("%H")
		mi = current.strftime("%M")
		doy = current.strftime('%j')
	
		start_str = current.strftime("%Y%m%d-S%H%M00")
		end_str = current + timedelta(minutes=29)
		end_str   = end_str.strftime("E%H%M59")
		filename  = f"3B-HHR{run_char}.MS.MRG.3IMERG.{start_str}-{end_str}.{delta_time:04}.V07B.HDF5.nc4"
		
		#print(filename)
		#url = f"{base_url}/{yyyy}/{mm}/{dd}/{filename}"
		url = f"{base_url}/{yyyy}/{doy}/{filename}{url_aggregation}"
		#print(url)
		local_path = os.path.join(output_dir,"raw", filename)
		#print(local_path)
		os.makedirs(os.path.dirname(local_path), exist_ok=True)
	
		try:
			if not os.path.exists(local_path):
				r = session.get(url, stream=True)
				if r.status_code == 200:
					with open(local_path, "wb") as f:
						for chunk in r.iter_content(chunk_size=8192):
							f.write(chunk)
				else:
					print(f"❌ {filename} ({r.status_code})")
					current += timedelta(minutes=30)
					continue
	
			# Read file and subset
			precip = xr.open_dataset(local_path)

			#	# Select subset indices only once
			if lat_slice is None or lon_slice is None:
				lat_slice = precip['lat']
				lon_slice = precip['lon']
			#	precip = f["Grid/precipitationCal"][lat_slice, lon_slice]
	
			#precip_data.append(precip)
			precip_data.append((precip['precipitation'][0].values*0.5).T)
			time_data.append(current)
	
		except Exception as e:
			print(f"⚠️ Error reading {filename}: {e}")
	
		current += timedelta(minutes=30)
		delta_time += 30
		if delta_time > 1410:
			delta_time = 0
		
	# === Save as NetCDF ===
	if precip_data:
		data = np.array(precip_data)
		times = np.array(time_data)
		#print(data.shape)
		da = xr.DataArray(
			data,
			coords={"time": times, "lat": lat_slice, "lon": lon_slice},
			dims=["time", "lat", "lon"],
			#name="pre"
		)
		ds = xr.Dataset({"pre": da})
	
		out_month = istart_date.strftime("%Y-%m")
		
		final_path = os.path.join(output_dir, istart_date.strftime("%Y"))
		os.makedirs(final_path, exist_ok=True)
		#/IMERG/YYYY/IMERG_YYYY-MM.nc
		output_file = os.path.join(final_path, f"IMERG_{out_month}.nc")
		ds.to_netcdf(output_file)
		print(f"✅ Saved monthly subset: {output_file}")
	else:
	    print("⚠️ No data downloaded or matched bounding box.")
