# -*- coding: utf-8 -*-
import os
import sys
import xarray as xr
import requests
from requests.auth import HTTPBasicAuth

sys.path.append("Training/Datasets/")
import AQ_credentials as NN_credentials # comment this line if you are using NN_credentials.py for NOAA credentials
#import NN_credentials as NN_credentials # uncomment this line if you are using NN_credentials.py for NOAA credentials
# This should be a separate file containing your NOAA and IMERG credentials

# -----------------------------
# User settings
# -----------------------------
username = NN_credentials.USERNAME_NOAA
password = NN_credentials.PASSWORD_NOAA

out_dir = "/home/c1755103/dataset/modis/ndvi/"

#out_dir = "avhrr_ndvi_pakistan"
os.makedirs(out_dir, exist_ok=True)

# Bounding box for Pakistan
lat_min, lat_max = 23, 37
lon_min, lon_max = 60, 77.5

# -----------------------------
# Download + subset loop
# -----------------------------
base_url = "https://www.ncei.noaa.gov/data/avhrr-monthly-ndvi/access"

for year in range(1981, 2025):  # 1981�2024
    file_name = f"avhrr-monthly-ndvi_v5_{year}.nc"
    url = f"{base_url}/{year}/{file_name}"
    local_file = os.path.join(out_dir, file_name)

    # Step 1: Download yearly global file if not already present
    if not os.path.exists(local_file):
        print(f"Downloading {file_name}...")
        with requests.get(url, auth=HTTPBasicAuth(username, password), stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(local_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    # Step 2: Open with xarray and subset Pakistan
    print(f"Processing {file_name}...")
    ds = xr.open_dataset(local_file)

    # Subset by bounding box
    ds_pk = ds.sel(lat=slice(lat_max, lat_min), lon=slice(lon_min, lon_max))

    # Save subset file
    out_file = os.path.join(out_dir, f"NDVI_Pakistan_{year}.nc")
    ds_pk.to_netcdf(out_file)

    print(f"? Saved subset: {out_file}")
