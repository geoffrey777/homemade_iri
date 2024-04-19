# IMPORTING DATA FILE

from netCDF4 import Dataset
import os
import re
import numpy as np

units = {
    "sshg" : "m",
    "longitude" : "°",
    "latitude" : "°",
    "sst" : "°C",
    "level" : "m",
    "month" : "",
    "year" : ""
}

months_letters = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]  

days = lambda year : [31, 28 + year % 4 == 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

data = {
    "chlor_a" : {
        "YEAR" : lambda year : "AQUA_MODIS." + year + "0101_"+ year + "1231.L3m.YR.CHL.chlor_a.4km.nc",
        "MONTH" : lambda year, month : year + "/AQUA_MODIS." + year + month + "01_" + month + days(year)[month-1] + ".L3m.MO.CHL.chlor_a.4km.nc"
    },
    "dzdt" : {
        "YEAR" : lambda year : "dzdt." + year + ".nc"
    },
    "n_an" : {
        "CLIMATOLOGY" : "woa23_all_n00_01.nc"
    },
    "p_an" : {
        "CLIMATOLOGY" : "woa23_all_p00_01.nc"
    },
    "i_an" : {
        "CLIMATOLOGY" : "woa23_all_i00_01.nc"
    },
    "sshg" : {
        "YEAR" : lambda year : "sshg." + year + ".nc"
    },
    "ucur" : {
        "YEAR" : lambda year : "ucru." + year + ".nc"
    },
    "vcur" : {
        "YEAR" : lambda year : "vcur." + year + ".nc"
    },
    "sst" : {
        "YEAR" : lambda year : "AQUA_MODIS." + year + "0101_" + year + "1231.L3m.YR.SST.sst.4km.nc"
    }
}

vars = {
    "CHLOROPHYLL" : "chlor_a",
    "SST" : "sst",
    "SSHG" : "sshg",
    "NITRATE" : "n_an",
    "PHOSPHATE" : "p_an"
}

def get_bigger_than(data, number):
    minimum = np.full(data.shape, number)
    return data * (data > minimum)

def get_lower_than(data, number):
    maximum = np.full(data.shape, number)
    return data * (data < maximum)

def get_between(data, min_value, max_value):
    # DATA CLEANING
    data = get_bigger_than(data, min_value)
    data = get_lower_than(data, max_value)
    return data

def extract_index(data_nc, borders, is_360):
    # pour la latitude on retourne un i_min et un i_max l'utilisateur
    # pourra avoir [i_min, i_max]
    # mais pour la longitude plus subtil car :
    # 1. deux écritures [-180,180] ou [0,360] c'est is_360
    # 2. si l'user veut une coupe longitudinale allant de -5 à 5 il passe par
    # le méridien, la solution : on renvoie une liste des indices du genre 
    # [...,359,360,1,2,...]
    N, W, S, E = borders
    j_north = np.argmin(abs(data_nc['lat'][:]-N))
    j_south = np.argmin(abs(data_nc['lat'][:]-S))

    if is_360:
        W = W % 360
        E = E % 360

    j_west = np.argmin(abs(data_nc['lon'][:]-W))
    j_east = np.argmin(abs(data_nc['lon'][:]-E))

    if j_west < j_east:
        # Tudo ben
        latitude_js = np.arange(j_west, j_east+1, 1)
        return j_north, j_south, latitude_js
    else:
        n = data_nc['lon'].shape[0]
        latitude_js = np.arange(j_west, j_east+n, 1) % n
        return j_north, j_south, latitude_js

#temp_nc = Dataset(src, "r")
data = {}
axis = {}

os.chdir("DATA")
folders = os.listdir()

# def get_coordinates():
#     # COORDINATES -> INDICES
#     is_360 = temp_nc['lon'][-1] > 181
#     j_north, j_south, longitude_js = extract_index(temp_nc, borders, is_360)
#     p_latitude = len(temp_nc["lat"][j_south:j_north])
#     longitude = np.asarray(temp_nc["lon"][longitude_js])
#     p_longitude = len(longitude_js)

str_to_int = lambda list : [int(l) for l in list]
months = np.arange(1, 13, 1)

for folder in folders:
    os.chdir(folder)
    timelines = os.listdir()
    if "MONTH" in timelines:
        os.chdir("MONTH")
        years = os.listdir()
        nb_of_years = len(years)

        temp_nc = Dataset(years[0] + "/" + os.listdir(years[0])[0], "r")

        p_latitude, p_longitude = temp_nc[vars[folder]][:].shape
    
        #is_360 = temp_nc['lon'][-1] > 181
        # data[folder] = np.zeros((nb_of_years, 12, p_latitude, p_longitude))
        
        data[folder] = []

        for j_y, year in zip(range(nb_of_years), years):
            
            for j_m, month in zip(range(12), os.listdir(year)):

                temp_nc = Dataset(year + "/" + month, 'r')
                # print(temp_nc[vars[folder]][:])
                data[folder].append(temp_nc[vars[folder]][:])

        data[folder] = np.asarray(data[folder])
        # print(data[folder])
        years = str_to_int(years)
        years.sort()

        axis[folder] = {"year" : years}
        
        axis[folder][year]["month"] = months

    elif "YEAR" in timelines:
        os.chdir("YEAR")
        files = os.listdir()
        nb_of_years = len(files)
        years = [re.findall(r"(200\d|199\d)", file)[0] for file in files]
        years.sort()
        temp_nc = Dataset(files[0], 'r')
        
        shape = (nb_of_years,) + temp_nc[var[folder]][:].shape

        data[folder] = np.zeros(shape)

        axis[folder] = {"year" : years}

        if 12 in shape:
            axis[folder]["month"] = months
    

    axis["latitude"] = temp_nc["lat"]
    axis["longitude"] = temp_nc["lon"]

# AXIS : {LABELS : VALUES}
axis = lambda temp_nc : {
    "year" : np.arange(2002, 2022, 1),
    "month" : np.arange(1, 13, 1),
    "latitude" : np.asarray(temp_nc["lat"][j_south:j_north]),
    "longitude" : np.asarray(temp_nc["lon"][longitude_js])
}

# DATA : (years, months, p_latitude, p_longitude)
data = np.zeros((20,12,p_latitude,p_longitude))
temp_nc = np.asarray(temp_nc[var][:,j_south:j_north, longitude_js])
data[0] = get_between(temp_nc, -10, 10)

for i,y in zip(range(1,20),range(2003,2022)):
    temp_nc = Dataset("DATA/SSHG/ANNUAL/sshg." + str(y) + ".nc", "r")
    # NDARRRAY
    temp_nd = np.asarray(temp_nc[var][...,j_south:j_north, longitude_js])
    # CLEANING
    temp_clean = get_between(temp_nd, -10, 10)
    # SAVING
    data[i] = temp_clean[::-1]