# IMPORTING DATA FILE

from netCDF4 import Dataset
import os
import re
import numpy as np
import matplotlib.pyplot as plt

units = {
    "sshg" : "m",
    "longitude" : "°",
    "latitude" : "°",
    "sst" : "°C",
    "level" : "m",
    "month" : "",
    "year" : "",
    "p_an" : "\\mu mol.kg^{-1}",
    "n_an" : "\\mu mol.kg^{-1}",
    "i_an" : "\\mu mol.kg^{-1}",
    "depth" : "m",
    "chlor_a" : "mg.m^{-3}",
    "dzdt" : "m.s^{-1}",
    "ucur" : "m.s^{-1}",
    "vcur" : "m.s^{-1}",
    "pottmp" : "K",
    "uflx" : "N.m^{-2}",
    "vflx" : "N.m^{—2}"
}

months_letters = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]  

days = lambda year : [31, 28 + year % 4 == 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

vars = {
    "CHLOROPHYLL" : "chlor_a",
    "SST" : "sst",
    "SSHG" : "sshg",
    "NITRATE" : "n_an",
    "PHOSPHATE" : "p_an",
    "SILICATE" : "i_an",
    "DZDT" : "dzdt",
    "UCUR" : "ucur",
    "VCUR" : "vcur",
    "POTTEMP" : "pottmp",
    "UFLX" : "uflx",
    "VFLX" : "vflx"
}

intervals = {
    "CHLOROPHYLL" : (-1000.,1000.),
    "SST" : (-1000.,1000.),
    "SSHG" : (-10.,10.),
    "NITRATE" : (-100.,100.),
    "PHOSPHATE" : (-100.,100.),
    "SILICATE" : (-100.,100.),
    "DZDT" : (-1.,1.),
    "UCUR" : (-10.,10.),
    "VCUR" : (-10.,10.),
    "UFLX" : (-100.,100.),
    "VFLX" : (-100.,100.),
    "POTTEMP" : (-500.,500.)
}

colors = {
    "CHLOROPHYLL" : "green",
    "SST" : "navy",
    "POTTEMP" : "navy",
    "SSHG" : "gray",
    "NITRATE" : "orange",
    "PHOSPHATE" : "violet",
    "SILICATE" : "yellow",
    "DZDT" : "brown",
    "UCUR" : "coral",
    "VCUR" : "coral",
    "UFLX" : "chocolate",
    "VFLX" : "chocolate"
}


def get_between(arr, min_value, max_value):
    # DATA CLEANING
    minimum = np.full(arr.shape, min_value)
    maximum = np.full(arr.shape, max_value)
    arr[arr > maximum] = np.nan
    arr[arr < minimum] = np.nan
    return arr

axis = {}
axis_length = {}
nc_files = {}
coordinates = {}
months = np.arange(1, 13, 1)
inverted = {}


def generate_coordinates(borders, variable, temp_nc):

    N, W, S, E = list(borders.values())

    # LATITUDES
    j_south = np.argmin(abs(temp_nc['lat'][:]-S))
    j_north = np.argmin(abs(temp_nc['lat'][:]-N))
    
    if j_south > j_north:

        # LATITUDES ARE FROM N TO S
        inverted[variable] = True
        j_south, j_north = j_north, j_south
        latitudes = np.asarray(temp_nc["lat"][j_south:j_north])[::-1]
    
    else:
        latitudes = np.asarray(temp_nc["lat"][j_south:j_north])

    axis[variable]["latitude"] = latitudes
    axis_length[variable]["latitude"] = len(latitudes)

    # LONGITUDES
    is_360 = temp_nc['lon'][-1] > 181

    if is_360:

        W = W % 360
        E = E % 360

    j_west = np.argmin(abs(temp_nc['lon'][:]-W))
    j_east = np.argmin(abs(temp_nc['lon'][:]-E))

    if j_west < j_east:

        longitude_js = np.arange(j_west, j_east+1, 1)
    
    else:

        n = temp_nc['lon'].shape[0]
        longitude_js = np.arange(j_west, j_east+n, 1) % n

    longitudes = np.asarray(temp_nc["lon"][longitude_js])

    if is_360:

        longitudes[longitudes > 180] = ( longitudes[longitudes > 180] - 360. )

        if longitudes[1] < 0:
            longitudes[0] = - longitudes[0]
        

    axis[variable]["longitude"] = longitudes
    axis_length[variable]["longitude"] = len(longitudes)

    coordinates[variable] =  (j_south, j_north, longitude_js)


def load_file(borders, timeline, months_args, variable):

    print(variable)

    os.chdir("DATA")
    variables = os.listdir()
    
    if variable in variables:

        os.chdir(variable)
        folders = os.listdir()
        

        if "MONTH" in folders and len(months_args) > 0:

            timeline.sort()
            timeline = np.asarray(timeline)
            
            os.chdir("MONTH")

            years_folders = np.asarray(os.listdir())
            
            years_folders = years_folders[years_folders != ".DS_Store"]
            years = years_folders.astype(int)
            
            args = np.in1d(years, timeline)
            years_folders = years_folders[args]
            years = years[args]

            nc_files[variable] = {}

            for year in years_folders:

                os.chdir(year)

                months_files = np.sort(np.asarray(os.listdir()))
                months_files = months_files[months_files != ".DS_Store"]
                months_files = months_files[months_args]
                
                nc_files[variable][int(year)] = {}

                for i, month in zip(range(1,13), months_files):
                    
                    nc_files[variable][int(year)][i] = Dataset(month, 'r') 
    
                os.chdir("..")
            
            temp_nc = nc_files[variable][int(year)][1]

            axis[variable] = {"year" : years}
            axis_length[variable] = {"year" : len(years)}

            axis[variable]["month"] = months_args+1
            axis_length[variable]["month"] = len(months_args)

        elif "YEAR" in folders:

            timeline.sort()
            timeline = np.asarray(timeline)

            os.chdir("YEAR")
            files = np.asarray(os.listdir())
        
            years = np.asarray([int(re.findall(r"(202\d|201\d|200\d|199\d|198\d)", file)[0]) for file in files])

            years_arg = np.argsort(years)
            years = np.sort(years)

            files = files[years_arg]

            args = np.in1d(years, timeline)

            years = years[args]
            files = files[args]

            nc_files[variable] = {}
            
            for year, file in zip(years, files):
                nc_files[variable][int(year)] = Dataset(str(file), 'r')
                
            axis[variable] = {"year" : years}
            axis_length[variable] = {"year" : len(timeline)}
            
            temp_nc = nc_files[variable][int(year)]
            
            shape = temp_nc[vars[variable]][:].shape

            if 12 in shape:
                axis[variable]["month"] = months
                axis_length[variable]["month"] = 12
            
            if 40 in shape:
                axis[variable]["level"] = np.asarray(temp_nc["level"][:])
                axis_length[variable]["level"] = 40

        elif "DEPTH" in folders:
            # FILE WITH LEVEL DATA
            os.chdir("DEPTH")
            files = os.listdir()

            temp_nc = Dataset(files.pop(0))

            nc_files[variable] = temp_nc
            
            depths = np.asarray(temp_nc["depth"][:])
            axis[variable] = {"depth" : depths}
            axis_length[variable] = {"depth" : len(depths)}

        else:
            raise Exception("No data for " + variable)
        
        generate_coordinates(borders, variable, temp_nc)

        os.chdir("..")
        os.chdir("..")
    
    else:
        raise Exception("Missing data for " + variable)
    
    os.chdir("..")