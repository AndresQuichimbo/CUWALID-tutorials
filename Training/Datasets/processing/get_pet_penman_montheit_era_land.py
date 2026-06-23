import glob
import os
import numpy as np
import xarray as xr

# this script calculates hourly Penman-Monteith PET from ERA5-Land data
# and saves the results to netCDF files. The FAO-56 Penman-Monteith equation
# is used for the calculation.
# It has been designed to process multiple monthly ERA5-Land files in a batch manner.
# AI has been used to optimize the code for efficiency and clarity.

def calculate_hourly_pet(file_path):
    """Calculates hourly Penman-Monteith PET from an ERA5-Land netCDF file."""
    print(f"Processing: {os.path.basename(file_path)}")

    # 1. Load dataset
    ds = xr.open_dataset(file_path)

    # check if time dimension is named "time" or "valid_time"
    if "valid_time" in ds.dims:
        ds = ds.rename({"valid_time": "time"})

    # 2. Extract and convert raw meteorological variables
    t2m = ds["t2m"] - 273.15  # Convert Kelvin to Celsius
    d2m = ds["d2m"] - 273.15  # Convert Kelvin to Celsius
    u10 = ds["u10"]  # 10m u-component of wind
    v10 = ds["v10"]  # 10m v-component of wind
    sp = ds["sp"] / 1000.0  # Convert Pa to kPa
    ssr = ds["ssr"]  # Joules/m2
    strd = ds["str"]  # Joules/m2

    # 3. Wind Speed Conversion (10m to 2m using FAO-56 wind profile relationship)
    u10_speed = np.sqrt(u10**2 + v10**2)
    u2 = u10_speed * (4.87 / np.log(67.8 * 10 - 5.42))

    # 4. Vapor Pressure Calculations (kPa)
    e0 = 0.6108 * np.exp((17.27 * t2m) / (t2m + 237.3))  # Saturation
    ea = 0.6108 * np.exp((17.27 * d2m) / (d2m + 237.3))  # Actual
    vpd = e0 - ea
    vpd = xr.where(vpd < 0, 0, vpd)  # Enforce physical limit

    # 5. Psychrometric constant (gamma) and Slope of vapor pressure curve (Delta)
    gamma = 0.000665 * sp
    delta = (4098 * e0) / ((t2m + 237.3) ** 2)

    # 6. Net Radiation (Rn) Calculation (Joules/m2 to MJ/m2/hour)
    #ssr_hourly = ssr.diff(dim="time", label="upper") / 1_000_000.0
    #str_hourly = strd.diff(dim="time", label="upper") / 1_000_000.0
    #rn = ssr_hourly + str_hourly

    # Isolate the specific hourly accumulation
    # .diff applies the subtraction: Value(t) - Value(t-1)
    # .where sets unphysical negative values (if any) to 0
    ssr_hourly = ssr.diff(dim='time', label='upper').where(lambda x: x >= 0, 0)
    str_hourly = strd.diff(dim='time', label='upper').where(lambda x: x <= 0, 0)

    # Convert from J/m^2 to W/m^2 by dividing by 3600 seconds
    ssr_hourly = ssr_hourly / 1_000_000.0
    str_hourly = str_hourly / 1_000_000.0

    # Optional: Add the first hour back (00:00 UTC), as .diff drops the first time step
    # At 00:00 UTC, the raw value corresponds to the 23:00 to 00:00 accumulation
    ds_00 = ssr.isel(time=0) / 1_000_000.0
    ssr_hourly = xr.concat([ds_00, ssr_hourly], dim='time')
    ds_00 = strd.isel(time=0) / 1_000_000.0
    str_hourly = xr.concat([ds_00, str_hourly], dim='time')

    rn = ssr_hourly + str_hourly

    ## 7. Coordinate Alignment
    ## The .diff() dropped the first hour. .reindex_like() instantly subsets
    ## all other variables to match the exact hourly timeline of rn.
    #t2m = t2m.reindex_like(ssr_hourly)
    #u2 = u2.reindex_like(ssr_hourly)
    #vpd = vpd.reindex_like(ssr_hourly)
    #delta = delta.reindex_like(ssr_hourly)
    #gamma = gamma.reindex_like(ssr_hourly)

    # 8. Soil Heat Flux (G) Estimation for Hourly steps
    g = xr.where(rn >= 0, 0.1 * rn, 0.5 * rn)

    # 9. Penman-Monteith Equation (FAO-56 Hourly Formulation)
    term1 = 0.408 * delta * (rn - g)
    term2 = gamma * (37 / (t2m + 273.3)) * u2 * vpd
    denominator = delta + gamma * (1 + 0.34 * u2)

    pet = (term1 + term2) / denominator
    pet = xr.where(pet < 0, 0, pet)  # Set negative evapotranspiration to 0

    # 10. Format output dataset
    pet_ds = pet.to_dataset(name="pet")
    pet_ds["pet"].attrs = {
        "units": "mm/hour",
        "long_name": "Penman-Monteith Potential Evapotranspiration",
    }

    return pet_ds


# --- Batch Processing Execution ---
input_dir = "/share/home/c1755103/dataset/ERA_temp/"
output_dir = "/share/home/c1755103/dataset/ERA/"
os.makedirs(output_dir, exist_ok=True)

# Find all matching monthly files
file_pattern = os.path.join(input_dir, "HAD_meteo_*_*_pm.nc")
file_list = sorted(glob.glob(file_pattern))

for file_path in file_list:
    try:
        # Calculate PET
        output_ds = calculate_hourly_pet(file_path)

        # Generate output filename (e.g., HAD_pet_2026_02.nc)
        base_name = os.path.basename(file_path)
        output_name = base_name.replace("_pm.nc", ".nc")
        output_name = output_name.replace("meteo", "pet")
        output_path = os.path.join(output_dir, output_name)

        # Save to netCDF
        output_ds.to_netcdf(output_path)
        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

