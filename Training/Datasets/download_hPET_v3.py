import os
import numpy as np
from netCDF4 import Dataset
import wget
import datetime as dt
import xarray as xr

## ***** MAKE THE NECESSARY CHANGES TO THE FUNCTION main() ***********##
## ***** AND RUN THIS PYTHON SCRIPT TO DOWNLOAD hPET and dPET ********##
def main():
    start = dt.datetime.now()
    # example (please change these values to your specification)
    # input arguments
    startyear = 2025
    endyear = 2026
    latmin = -6.0#-2.0#
    latmax =  15.5#1.25#
    lonmin = 32.0#35.50
    lonmax = 52.10#38.30#
    regionname='HAD'
    t_resolution ='hourly'
    output_path = '/share/home/c1755103/dataset/ERA/'
    remove_globaldata = 1 # 0 for keep the global data, 1 remove the global data
    # run script
    # check variables
    check_input_variables(startyear,endyear,latmin,latmax,lonmin,lonmax,
        regionname,t_resolution,output_path,remove_globaldata)
    # download data
    wrapper(startyear,endyear,latmin,latmax,lonmin,lonmax,regionname,
        t_resolution,output_path,remove_globaldata)

    end = dt.datetime.now()
    diff= end-start
    print('Runtime: %s'%diff)


## ********** NO CHANGE ON THE CODE BELOW THIS **********************************************##
def wrapper(startyear,endyear,latmin,latmax,lonmin,lonmax,regionname,
    t_resolution,output_path,remove_globaldata):
    """
    This is a wrapper function to run for downloading hPET and dPET data.
    All the arguments need to be given at the end of the script before running
    the script.

    :param startyear: the begging year to start the data download (min = 1981, max = 2019)
    :param endyear: the last year of data to be  downloaded (min = 1981, max = 2019)
    :param latmin: the minimum latitude value of the region (float)
    :param latmax: the maximum latitude value of the region (float)
    :param lonmin: the minimum longitude value of the region (float)
    :param lonmax: the maximum longitude value of the region (float)
    :param regionname: name of the region (it could be any name the user wants) (string)
    :param t_resolution: the time resolution to be downloaded (daily or hourly)
    :param output_path:  the file path to store the downloaded data (string)
    :return:
    """

    if t_resolution == 'daily':
        #datapath = 'https://data.bris.ac.uk/webshare/Stochastic_storm_modelling/2d241f8f-e661-4380-b858-7459f5c7141a/hPET/'
        datapath = 'https://data.bris.ac.uk/datasets/qb8ujazzda0s2aykkv0oq0ctp/'
    elif t_resolution == 'hourly':
        #datapath = 'https://data.bris.ac.uk/webshare/Stochastic_storm_modelling/2d241f8f-e661-4380-b858-7459f5c7141a/hPET/'
        datapath = 'https://data.bris.ac.uk/datasets/qb8ujazzda0s2aykkv0oq0ctp/'
    else:
        raise ValueError("t_resolution is wrong please write 'daily' or 'hourly'")

    # set up the year array loop through each year to download the data
    years = np.arange(startyear,endyear+1)
    for y in range(0,len(years)):
        year=int(years[y])
        region_extract(datapath,year,latmin,latmax,lonmin,lonmax,regionname,t_resolution,output_path,remove_globaldata)
        print(year)


def region_extract(datapath,year,latmin,latmax,lonmin,lonmax,regionname,
    t_resolution,output_path,remove_globaldata):
    """
    This function extract the data from the global hPET and dPET file and write a new
    netCDF file with a file name <year>_<t_resolution>_pet_<regionname>.nc in the output_path
    provided.

    :param datapath: the file path where the hPET data is stored (url)
    :param year: the year for which data is going to be downloaded (integer)
    :param latmin: the minimum latitude value (float)
    :param latmax: the maximum latitude value (float)
    :param lonmin: the minimum longitude value (float)
    :param lonmax: the maximum longitude value (float)
    :param regionname: name of the region (it could be any name the user wants) (string)
    :param t_resolution: the time resolution to be downloaded (daily or hourly)
    :param output_path:  the file path to store the downloaded data (string)
    :param remove_globaldata:  switch for removing the global data after extracting the region (0= donot remove, 1= remove)
    :return: hPET or dPET data in a netCDF file
    """

    if t_resolution == 'daily':
        fname = '_daily_pet.nc'
        tunits='days since '+str(year)+'-01-01' # time unit for the new netcdf file
    elif t_resolution == 'hourly':
        fname = '_hourly_pet.nc'
        tunits='hours since '+str(year)+'-01-01 00:00:00'
    else:
        raise ValueError("t_resolution is wrong please write 'daily' or 'hourly'")

    # Download the data from the server
    url=datapath + str(year) + fname
    print('Downloading '+url) 
    file_dl = wget.download(url, out=output_path)
    
    
    # read the file to extract the regions
    pet_hr = Dataset(output_path + str(year) + fname)  #datapath + 
    lats = pet_hr.variables['latitude'][:]
    lons = pet_hr.variables['longitude'][:]
    
    # extract the min and max index
    latminind, lonminind = nearest_point(latmin, lonmin, lats, lons)
    latmaxind, lonmaxind = nearest_point(latmax, lonmax, lats, lons)
 
    # read the data pet
    reg_data=pet_hr.variables['pet'][:, latmaxind:latminind, lonminind:lonmaxind]  
    # read the new latitude and longitude
    newlats=lats[latmaxind:latminind]
    newlons=lons[lonminind:lonmaxind]

    if remove_globaldata == 1:
        # Remove the file to save space
        pet_hr.close()
        os.remove(output_path + str(year) + fname)
        print(output_path + str(year) + fname + ' File Removed!')
    else:
          pass
    
    # get a filename and variable name (here it is called pet)
    filename=output_path+str(year)+'_'+t_resolution+'_pet_'+regionname+'.nc'
    varname='pet'
    # write the new data on a netcdf file
    nc_write(reg_data, newlats, newlons, varname, tunits, filename)
    print(filename + ' completed!')

    
    # time zone offset
    if t_resolution == 'daily':
        # time zone offset not required
        pass            

    elif t_resolution == 'hourly':
        # Download the timezone data from the server
        datapath ='https://data.bris.ac.uk/webshare/Stochastic_storm_modelling/2d241f8f-e661-4380-b858-7459f5c7141a/hPET/'
        tz_fname = 'timezone_offset.nc'
        url = datapath + tz_fname
        #wget.bar_thermometer(current, total, width=80)
        print('Downloading ' + url) 
        #file_dl = wget.download(url, out=output_path)
        #tz_fname = "D:/ERA/HAD/" + tz_fname
        #data = xr.open_dataset(tz_fname)
        #pet=data['offset'].sel(latitude=slice(latmax,latmin), longitude=slice(lonmin,lonmax))
        #filename = output_path+'timezone_offset_'+regionname+'.nc'
        #pet.to_netcdf(path=filename, mode='w', format='NETCDF4_CLASSIC')
        #print(filename + ' completed!')
        #
        #if remove_globaldata == 1:
        #    # Remove the Global file to save space
        #    data.close()
        #    #os.remove(tz_fname)
        #    print(tz_fname + ' File Removed!')
        #else:
        #    pass
    else:
        raise ValueError("t_resolution is wrong please write 'daily' or 'hourly'")
    
    return None
    

def nearest_point(lat_var, lon_var, lats, lons):
    """
    This function identify the nearest grid location index for a specific lat-lon
    point.
    :param lat_var: the latitude
    :param lon_var: the longitude
    :param lats: all available latitude locations in the data
    :param lons: all available longitude locations in the data
    :return: the lat_index and lon_index
    """
    # this part is to handle if lons are givn 0-360 or -180-180
    if any(lons > 180.0) and (lon_var < 0.0):
        lon_var = lon_var + 360.0
    else:
        lon_var = lon_var
        
    lat = lats
    lon = lons

    if lat.ndim == 2:
        lat = lat[:, 0]
    else:
        pass
    if lon.ndim == 2:
        lon = lon[0, :]
    else:
        pass

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
    """
    this function write the PET on a netCDF file.

    :param: data: data to be written (time,lat,lon)
    :param: lat: latitude
    :param: lon: longitude
    :param: varname: name of the variable to be written (e.g. 'pet')
    :param: tunits: time units for the data (e.g. 'days since 1981-01-01')
    :param:filename: the file name to write the values with .nc extension

    :return:  produce a netCDF file in the same directory.
    """
    
    ds = Dataset(filename, mode='w', format='NETCDF4_CLASSIC')

    time = ds.createDimension('time', None)
    latitude = ds.createDimension('latitude', len(lat))
    longitude = ds.createDimension('longitude', len(lon))
   
    time = ds.createVariable('time', np.float32, ('time',))
    latitude = ds.createVariable('latitude', np.float32, ('latitude',))
    longitude = ds.createVariable('longitude', np.float32, ('longitude',))

    # check if the data is 2d or 3d
    if len(data.shape) == 3: # 3D array
        pet_val = ds.createVariable(varname, 'f4', ('time','latitude','longitude'), zlib=True)
        time.units = tunits  
        time.calendar = 'proleptic_gregorian'
        time[:] = np.arange(data.shape[0])
        latitude[:] = lat
        longitude [:] = lon
        pet_val[:,:,:] = data
    # this is only to write the time offsets
    elif len(data.shape) == 2: # 2D array
        pet_val = ds.createVariable(varname, 'i', ('latitude','longitude'), zlib=True)
        latitude[:] = lat
        longitude [:] = lon
        pet_val[:,:] = data
    else:
        raise ValueError('the function can only write a 2D or 3D array data!')

    ds.close()
    
    return None    


def check_input_variables(startyear,endyear,latmin,latmax,lonmin,lonmax,
    regionname,t_resolution,output_path,remove_globaldata):

    """
    This function check if the input variables are correct before proceeding to
    the download.
    """
    # check year range
    if (startyear < 1981) or (startyear > 2026):
        raise ValueError("startyear is out of range. It should be between 1981 and 2026")
    elif (endyear < 1981) or (endyear > 2026):
        raise ValueError("endyear is out of range. It should be between 1981 and 2026")
    else:
      pass

    # check startyear and endyear values 
    if (endyear < startyear):
        raise ValueError("endyear is less than startyear. endyear should be greather than or equal to start year.")
    else:
      pass

    # check latitude and longitude range
    if (latmin < -90.0) or (latmin > 90.0):
        raise ValueError("latmin is out of range. it should be 90.0 to -90.0")
    elif (latmax < -90.0) or (latmax > 90.0):
        raise ValueError("latmax is out of range. it should be 90.0 to -90.0")

    elif (lonmin < -180.0) or (lonmin > 180.0):
        raise ValueError("lonmin is out of range. it should be -180.0 to 180.0")
    elif (lonmax < -180.0) or (lonmax > 180.0):
        raise ValueError("lonmax is out of range. it should be -180.0 to 180.0")
    else:
      pass

    # check max min lon/lat 
    if (latmin > latmax):
        raise ValueError("latmin should be less than latmax. Check the input values!")

    elif (lonmin > lonmax):
        raise ValueError("lonmin should be less than lonmax. Check the input values!")
    else:
      pass

##********************************************************************************##
if __name__ == '__main__':
    main()

