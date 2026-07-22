"""
Process and download hPET and dPET data datasets.
Optimized for zero-leak local caching, automatic download resume, and safe extraction.
"""

import os
import sys
import time
import datetime as dt
import numpy as np
import requests
from netCDF4 import Dataset

def main(startyear=2002, endyear=2002, skip_existing=False):#, latmin=None, latmax=None, lonmin=None, lonmax=None, regionname=None, t_resolution=None, output_path=None, remove_globaldata=None):
    start = dt.datetime.now()
    
    #startyear = 2002
    #endyear = 2002
    
    latmin = -40.0
    latmax = 40.0
    lonmin = -26.0
    lonmax = 60.0
    
    regionname = 'AF'
    t_resolution = 'hourly'
    output_path = '/home/chc-andres/AF/datasets/climatology/hPET/raw/'
    remove_globaldata = False 
    
    if not os.path.exists(output_path):
        print(f"Directory {output_path} does not exist. Creating it now...")
        os.makedirs(output_path, exist_ok=True)
        print("Directory created successfully.")
    else:
        print(f"Output directory verified: {output_path}")

    os.environ['TMPDIR'] = output_path
    os.environ['TEMP'] = output_path
    os.environ['TMP'] = output_path
    print(f"System temporary environment variables bound to: {output_path}")

    check_input_variables(startyear, endyear, latmin, latmax, lonmin, lonmax, regionname, t_resolution, output_path, remove_globaldata)
    wrapper(startyear, endyear, latmin, latmax, lonmin, lonmax, regionname, t_resolution, output_path, remove_globaldata, skip_existing)
    
    end = dt.datetime.now()
    diff = end - start
    print('Runtime: %s' % diff)

def download_file_with_resume(url, absolute_local_path):
    """Downloads a file using requests, forcing streaming output directly to the absolute target directory location."""
    headers = {}
    part_path = absolute_local_path + ".part"
    
    if os.path.exists(part_path):
        temp_size = os.path.getsize(part_path)
        headers['Range'] = f'bytes={temp_size}-'
        mode = 'ab'
        print(f"Resuming partial download from byte index {temp_size} inside target storage folder...")
    else:
        temp_size = 0
        mode = 'wb'

    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            with requests.get(url, headers=headers, stream=True, timeout=30) as r:
                if r.status_code == 416: 
                    print("File appears already fully downloaded or server doesn't support the requested byte range.")
                    if os.path.exists(part_path):
                        os.rename(part_path, absolute_local_path)
                    return
                r.raise_for_status()
                
                total_size = int(r.headers.get('content-length', 0)) + temp_size
                downloaded = temp_size
                
                with open(part_path, mode) as f:
                    for chunk in r.iter_content(chunk_size=4096 * 1024): 
                        if chunk:
                            f.write(chunk)
                            f.flush() 
                            os.fsync(f.fileno()) 
                            downloaded += len(chunk)
                            done = int(50 * downloaded / total_size) if total_size > 0 else 0
                            sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded / (1024**3):.2f} / {total_size / (1024**3):.2f} GB")
                            sys.stdout.flush()
                print() 
                
                if os.path.exists(part_path):
                    os.rename(part_path, absolute_local_path)
                return 
                
        except (requests.exceptions.RequestException, ConnectionError) as e:
            print(f"\n[Warning] Network interrupted on attempt {attempt+1}/{max_retries}: {e}")
            time.sleep(retry_delay)
            if os.path.exists(part_path):
                temp_size = os.path.getsize(part_path)
                headers['Range'] = f'bytes={temp_size}-'
                mode = 'ab'
    
    raise IOError(f"Failed to download file after {max_retries} connection drops.")

def get_remote_file_size(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=30)
        response.raise_for_status()
        content_length = response.headers.get('content-length')
        if content_length is not None:
            return int(content_length)
    except requests.exceptions.RequestException:
        pass

    try:
        response = requests.get(url, stream=True, timeout=30)
        try:
            content_length = response.headers.get('content-length')
            return int(content_length) if content_length is not None else None
        finally:
            response.close()
    except requests.exceptions.RequestException:
        return None

def wrapper(startyear, endyear, latmin, latmax, lonmin, lonmax, regionname, t_resolution, output_path, remove_globaldata, skip_existing):
    if t_resolution == 'daily':
        #datapath = 'https://data.bris.ac.uk/webshare/Stochastic_storm_modelling/2d241f8f-e661-4380-b858-7459f5c7141a/hPET/'
        datapath = 'https://data.bris.ac.uk/datasets/qb8ujazzda0s2aykkv0oq0ctp/'
    elif t_resolution == 'hourly':
        #datapath = 'https://data.bris.ac.uk/webshare/Stochastic_storm_modelling/2d241f8f-e661-4380-b858-7459f5c7141a/hPET/'
        datapath = 'https://data.bris.ac.uk/datasets/qb8ujazzda0s2aykkv0oq0ctp/'
    else:
        raise ValueError("t_resolution is wrong please write 'daily' or 'hourly'")

    years = np.arange(startyear, endyear + 1)
    for y in range(0, len(years)):
        year = int(years[y])
        region_extract(datapath, year, latmin, latmax, lonmin, lonmax, regionname, t_resolution, output_path, remove_globaldata, skip_existing)
        print(f"Finished processing year: {year}")

def region_extract(datapath, year, latmin, latmax, lonmin, lonmax, regionname, t_resolution, output_path, remove_globaldata, skip_existing):
    if t_resolution == 'daily':
        fname = '_daily_pet.nc'
        tunits = 'days since ' + str(year) + '-01-01' 
    elif t_resolution == 'hourly':
        fname = '_hourly_pet.nc'
        tunits = 'hours since ' + str(year) + '-01-01 00:00:00'
    else:
        raise ValueError("t_resolution is wrong please write 'daily' or 'hourly'")

    specific_file = str(year) + fname
    url = f"{datapath}{specific_file}"
    global_file_path = os.path.abspath(os.path.join(output_path, specific_file))
    regional_file_path = os.path.abspath(os.path.join(output_path, f"{year}_{t_resolution}_pet_{regionname}.nc"))
    
    print(f"\n--- Processing Year: {year} ---")

    if os.path.exists(global_file_path):
        if skip_existing and os.path.exists(regional_file_path):
            print(f"Skipping year {year}: output already exists at {regional_file_path}")
            return None
        print(f"Using existing global file for extraction: {global_file_path}")
    else:
        if skip_existing and os.path.exists(regional_file_path):
            print(f"Skipping year {year}: output already exists at {regional_file_path}")
            return None

        print('Downloading from: ' + url)
        print('Saving Raw File Directly To: ' + global_file_path)
        download_file_with_resume(url, global_file_path)

    pet_hr = None
    try:
        print("Opening file to extract subset boundaries...")
        pet_hr = Dataset(global_file_path)
        lats = pet_hr.variables['latitude'][:]
        lons = pet_hr.variables['longitude'][:]

        latminind, lonminind = nearest_point(latmin, lonmin, lats, lons)
        latmaxind, lonmaxind = nearest_point(latmax, lonmax, lats, lons)

        reg_data = pet_hr.variables['pet'][:, latmaxind:latminind, lonminind:lonmaxind]
        newlats = lats[latmaxind:latminind]
        newlons = lons[lonminind:lonmaxind]

        pet_hr.close()
        pet_hr = None 

        if remove_globaldata:
            if os.path.exists(global_file_path):
                os.remove(global_file_path)
                print(f"Extraction successful. Global file removed: {global_file_path}")
        else:
            print(f"Extraction successful. Global file kept as requested: {global_file_path}")

        varname = 'pet'

        nc_write(reg_data, newlats, newlons, varname, tunits, regional_file_path)
        print(regional_file_path + ' completed!')

    except Exception as e:
        print(f"\n[ERROR] Extraction failed for year {year} due to: {e}")
        part_file = global_file_path + ".part"
        if os.path.exists(part_file):
            print(f"[SAFEGUARD] Incomplete download file preserved at: {part_file} for resume.")
        if os.path.exists(global_file_path):
            print(f"[SAFEGUARD] The global file was NOT deleted. It is saved at: {global_file_path}")
        raise 
        
    finally:
        if pet_hr is not None:
            try:
                pet_hr.close()
            except:
                pass

    return None

def nearest_point(lat_var, lon_var, lats, lons):
    if any(lons > 180.0) and (lon_var < 0.0):
        lon_var = lon_var + 360.0
    else:
        lon_var = lon_var
        
    lat = lats
    lon = lons
    if lat.ndim == 2:
        lat = lat[:, 0]
    if lon.ndim == 2:
        lon = lon[0, :]
        
    index_a = np.where(lat >= lat_var)[0][-1]
    index_b = np.where(lat <= lat_var)[0][-1]
    if abs(lat[index_a] - lat_var) >= abs(lat[index_b] - lat_var):
        index_lat = index_b
    else:
        index_lat = index_a
        
    index_a = np.where(lon >= lon_var)[0][0]
    index_b = np.where(lon <= lon_var)[0][0]
    if abs(lon[index_a] - lon_var) >= abs(lon[index_b] - lon_var):
        index_lon = index_b
    else:
        index_lon = index_a
        
    return index_lat, index_lon

def nc_write(data, lat, lon, varname, tunits, filename):
    ds = Dataset(filename, mode='w', format='NETCDF4_CLASSIC')
    ds.createDimension('time', None)
    ds.createDimension('latitude', len(lat))
    ds.createDimension('longitude', len(lon))
    
    time_var = ds.createVariable('time', np.float32, ('time',))
    lat_var = ds.createVariable('latitude', np.float32, ('latitude',))
    lon_var = ds.createVariable('longitude', np.float32, ('longitude',))
    
    if len(data.shape) == 3:
        pet_val = ds.createVariable(varname, 'f4', ('time','latitude','longitude'), zlib=True)
        time_var.units = tunits
        time_var.calendar = 'proleptic_gregorian'
        time_var[:] = np.arange(data.shape[0])
        lat_var[:] = lat
        lon_var[:] = lon
        pet_val[:,:,:] = data
    elif len(data.shape) == 2:
        pet_val = ds.createVariable(varname, 'i', ('latitude','longitude'), zlib=True)
        lat_var[:] = lat
        lon_var[:] = lon
        pet_val[:,:] = data
    else:
        ds.close()
        raise ValueError('The function can only write a 2D or 3D array data!')
        
    ds.close()
    return None

def check_input_variables(startyear, endyear, latmin, latmax, lonmin, lonmax, regionname, t_resolution, output_path, remove_globaldata):
    if (startyear < 1981) or (startyear > 2026):
        raise ValueError("startyear is out of range. It should be between 1981 and 2026")
    if (endyear < 1981) or (endyear > 2026):
        raise ValueError("endyear is out of range. It should be between 1981 and 2026")
    if (endyear < startyear):
        raise ValueError("endyear is less than startyear. endyear should be greater than or equal to start year.")
    if (latmin < -90.0) or (latmin > 90.0):
        raise ValueError("latmin is out of range. it should be -90.0 to 90.0")

##********************************************************************************##
if __name__ == '__main__':
    # input arguments from command line
    if len(sys.argv) not in (3, 4):
        print("Usage: python grid_download_hPET.py <startyear> <endyear> [--skip-existing]")
        sys.exit(1)
    startyear = int(sys.argv[1])
    endyear = int(sys.argv[2])
    skip_existing = len(sys.argv) == 4 and sys.argv[3] == '--skip-existing'

    main(startyear=startyear, endyear=endyear, skip_existing=skip_existing)
