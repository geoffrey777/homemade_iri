# coding=utf-8

from matplotlib import pyplot as plt

import numpy as np

from data import *
import warnings

def translate(label, pluriel = False):
    if label == "year":
        if pluriel:
            return "années"
        return "année"
    if label == "month":
        return "mois"

def length_dict(dict):
    length_dict = {}
    for key, value in dict.items():
        length_dict[key] = len(value)
    return length_dict

def list_to_str(list):
    return [str(l) for l in list]

def dict_to_str(dict):
    str = "_"
    for key, value in dict.items():
        value = list(value)
        value.sort()
        value = list_to_str(value)
        str += key + "_(" + "_".join(value) + ")"
    return str

def get_labels_resolution(length, dimension):

    resolution_min = 1. #inch
    length_max = dimension / resolution_min
    step = int( length / length_max )
    if step == 0:
        # TOO MUCH SPACE
        step = 1
    return step

def check_and_round(arr):
    if type(arr[0]) == np.float32:
        return np.round(arr, 2)
    return arr

class Draw():

    def __init__(self):

        self.data = {}
        self.axis = {}
        self.axis_length = {}

    def get_data(self, variable, X_labels, Y_labels, **kwargs):
        
        try:
            self.data[variable]
            # DATA ALREADY EXIST BUT:

            # - YEAR(S) COULD BE MISSING
            if "year" in list(self.axis[variable].keys()):
        
                # COORDINATES
                j_south, j_north, j_longitudes = coordinates[variable]

                for year in kwargs["year"]:
    
                    if not year in self.axis[variable]["year"]:

                        temp_nd = np.asarray(nc_files[variable][year][vars[variable]][..., j_south:j_north, j_longitudes])

                        # INVERT IF NEEDED
                        if inverted[variable]:
                            # temp_nd = invert(self.axis[variable], temp_nd)
                            temp_nd = temp_nd[..., ::-1, :]
                        
                        # CLEANING
                        temp_nd = get_between(temp_nd, *intervals[variable])
                        # SAVING
                        self.data[variable] = self.append(self.data[variable], temp_nd)
                        # UPDATING
                        self.axis[variable]["year"].append(year)
                        self.axis_length[variable]["year"] += 1

            # # - MONTH(S) COULD BE MISSING
            # if "month" in list(self.axis[variable].keys()):

            #     # COORDINATES
            #     j_south, j_north, j_longitudes = coordinates[variable]

            #     for month in kwargs["month"]:
    
            #         if not month in self.axis[variable]["month"]:

            #             temp_nd = np.asarray(nc_files[variable][year][vars[variable]][month][..., j_south:j_north, j_longitudes])

            #             # INVERT IF NEEDED
            #             if inverted[variable]:
            #                 temp_nd = invert(self.axis[variable], temp_nd)
                        
            #             # CLEANING
            #             temp_nd = get_between(temp_nd, *intervals[variable])
            #             # SAVING
            #             self.data[variable] = self.append(self.data[variable], temp_nd)
            #             # UPDATING
            #             self.axis[variable]["year"].append(year)
            #             self.axis_length[variable]["year"] += 1


        except:
            # GETTING DATA FROM FILES

            timeline.sort()

            if "year" in list(kwargs.keys()):
                years = np.sort(kwargs["year"])
            else:
                years = timeline
            
            if "month" in list(kwargs.keys()):

                months_args = np.sort(np.asarray(kwargs["month"]) - 1)
            elif "month" in X_labels or "month" in Y_labels:
                months_args = np.arange(12)
            else:
                months_args = []

            load_file(borders, years, months_args, variable)

            self.axis[variable] = axis[variable]
            self.axis_length[variable] = axis_length[variable]

            shape = list(axis_length[variable].values())
        
            # INITIALISATION OF DATA
            self.data[variable] = np.empty(tuple(shape))

            # COORDINATES
            j_south, j_north, j_longitudes = coordinates[variable]

            try:
                # DEPTH INSTEAD OF YEARS
                temp_nd = np.asarray(nc_files[variable][vars[variable]][..., j_south:j_north, j_longitudes])
                self.data[variable] = temp_nd[0] 

            except:

                nb_of_years = len(years)
                months_are_files = type(nc_files[variable][int(years[0])]) == dict

                for i, year in zip(range(nb_of_years), years):

                    if months_are_files:
                        
                        nb_of_months = len(months_args)

                        for j, month in zip(range(nb_of_months), months_args):

                            temp_nd = np.asarray(nc_files[variable][int(year)][month+1][vars[variable]][..., j_south:j_north, j_longitudes])
                            # SAVING
                            self.data[variable][i][j] = temp_nd
                    else:

                        temp_nd = np.asarray(nc_files[variable][int(year)][vars[variable]][..., j_south:j_north, j_longitudes])

                        # SAVING
                        self.data[variable][i] = temp_nd
                
            # CLEANING
            self.data[variable] = get_between(self.data[variable], *intervals[variable])

    def generate_usr_data(self, variable, X_labels, Y_labels = None, **kwargs):

        self.usr_data = self.data[variable]
        self.usr_axis = self.axis[variable]
        self.usr_axis_length = self.axis_length[variable]
        self.avg_axis = []

        if "month" in list(kwargs.keys()):
            # GET DATA HAS ALREADY
            # TAKEN USER MONTHS
            del kwargs["month"]
        
        # UPDATING DATA AS USER PREFERENCES
        for label in kwargs.keys():
           
            usr_values = np.asarray(kwargs[label])
            
            values = self.usr_axis[label]
            
            # IS INSIDE THE RANGE OF VALUES?
            values.sort()

            Min = values[0]
            Max = values[-1]

            inf_min = np.unique(usr_values < Min)
            sup_max = np.unique(usr_values > Max)

            if len(inf_min) > 1:
                raise Exception("One (or more) " + label + " is(are) below the minimum")
            
            if len(sup_max) > 1:
                raise Exception("One (or more) " + label + " is(are) above the maximum")

            # SO, ALL USR_VALUES ARE IN THE INTERVAL
            # LET'S TAKE THE NEAREST FOR EACH VALUE
            usr_indices = np.zeros(usr_values.shape, dtype=int)
        
            for usr_value in usr_values:
                usr_indices[np.argmin(np.abs(values - usr_value))] = 1

            i = list(self.usr_axis.keys()).index(label)

            if label != "month" and label != "year":

                self.usr_data = np.delete(self.usr_data, not usr_indices, axis = i)

                self.usr_axis[label] = self.usr_axis[label][usr_indices]
                self.usr_axis_length[label] = len(usr_indices)

        labels = list(self.usr_axis.keys())
        nb_of_labels = len(labels)

        for i, label in zip(range(nb_of_labels), labels):

            # LABEL IS A VARIABLE
            if label in X_labels or label in Y_labels:
                
                print(label.upper() + " is a variable")

            # LABEL'S VALUES AVERAGE
            else:
                print("An average over " +  label.upper() + " has been calculated.")
                self.avg_axis.append(i)

    

    def figure(self, variable, X_label, Y_label = None, avg_delta = False, need_Z = False, **kwargs):

        if len(X_label) == 0:
            raise Exception("Need X axis")
        
        variable = variable.upper()

        X_labels = X_label.split()
        
        if Y_label:
            Y_labels = Y_label.split()
        else:
            Y_labels = []

        # MIN OR MAX
        if "min" in X_labels or "max" in X_labels:
            try:
                arg_min_or_max = X_labels.index("min")
            except:
                arg_min_or_max = X_labels.index("max")

            min_or_max_label = X_labels[arg_min_or_max+1]
            
        self.get_data(variable, X_labels, Y_labels, **kwargs)
        self.generate_usr_data(variable, X_labels, Y_labels, **kwargs)
        
        # FIGURE DIMENSIONS
        width = 7
        height = np.round(0.75*width, 2)

        # X THINGS
        # GROUPED SIZE
        X_j = self.usr_axis_length[X_labels[0]]
        j = list(self.usr_axis.keys()).index(X_labels[0])
        # GROUP SIZE
        X_k = 1
        # DEFAULT X
        X = np.arange(X_j)# self.axis[X[0]]

        # SAME ROUTINE FOR Y
        if Y_label:
            Y_j = self.usr_axis_length[Y_labels[0]]
            Y_k = 1
            Y = np.arange(Y_j)
        
    
        # TO AVOID THE "MEAN OF EMPTY SLICE" WARNING
        # DUE TO NANMEAN
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
        
            Z = np.nanmean(self.usr_data, axis=tuple(self.avg_axis))

        # 
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            # MIN
            if "min" in X_labels:
                j_min_or_max = list(self.usr_axis.keys()).index(min_or_max_label)
                if j_min_or_max <= j:
                    Z = np.nanmin(Z, axis = 0)
                else:
                    Z = np.nanmin(Z, axis = 1)

            # OR MAX
            if "max" in X_labels:
                j_min_or_max = list(self.usr_axis.keys()).index(min_or_max_label)
                
                if j_min_or_max <= j:
                    Z = np.nanmax(Z, axis = 0)
                else:
                    Z = np.nanmax(Z, axis = 1)

        if need_Z:
            Zx = check_and_round(self.usr_axis[X_labels[0]])
            return Z, Zx
        
        # MATPLOTLIB
        fig, ax = plt.subplots()

        # MULTIPLE LINES IN LEGEND
        # j GROUPED IN X-AXIS
        # k GROUP IN LEGEND
        if "and" in X_labels:

            for z, value in zip(Z, self.usr_axis[X_labels[-1]]):

                ax.scatter(X, z, label=value)

            ax.legend()

        # MULTIPLE LINES IN A ROW
        # k*j GROUPED IN X-AXIS
        elif "by" in X_labels:
            # UPDATING GROUP SIZE
            X_k = self.usr_axis_length[X_labels[-1]]

            X = np.arange(X_j*X_k)
            X = np.reshape(X, (X_k,X_j))

            if not X.shape == Z.shape:
                Z = np.reshape(Z, X.shape)

            for x, z in zip(X, Z):

                ax.scatter(x, z)

        # AVG DELTA   
        elif avg_delta:
            Z = Z - np.average(Z)

            ax.scatter(X, Z, color = colors[variable])

            ax.set_ylabel(variable.upper() + " $[" + units[vars[variable]] + "]$")

        
        elif not Y_label:
            ax.scatter(X, Z, color = colors[variable])
        
        # 2D FIGURE = IMSHOW
        else:
            # Y TICKS
            ax_yticks_label = check_and_round(np.repeat(self.usr_axis[Y_labels[0]], Y_k))# TODO Y_LABELS
            step = get_labels_resolution(Y_j, height)
            
            ax.set_yticks(Y.flatten()[::step], labels=ax_yticks_label[::-step])

            label = Y_labels[0].upper()

            # ADDING UNIT
            if units[Y_labels[0]] != "":
                label += " $[" + units[Y_labels[0]] + "]$"
            ax.set_ylabel(label)
            
            # CHECKING X, Y ORDER
            XY_shape = (Y.shape[0], X.shape[0])
            
            if not XY_shape == Z.shape:
                Z = np.reshape(Z, XY_shape)
        
            # BE CAREFUL: imshow DISPLAY ARRAYS
            # AS IMAGES SO IMAGE'S BOTTOM
            # IS ARRAY'S END : FOR OUR CASE
            # WHEN MAPS ARE GIVEN [S TO N]
            # THE RESULT IS UPSIDE DOWN WOLRDMAP
            # SO [::-1] IS USED TO FLIP THE ARRAY
            # EXCEPT FOR THOSE WHICH ARE [N TO S]
            try:
                if not inverted[variable]:
                    Z = Z[::-1]
            except:
                pass

            im = ax.imshow(Z, aspect="auto", cmap="coolwarm", norm = "linear")
            fig.colorbar(im, ax=ax, label = variable.upper() + " $[" + units[vars[variable]] + "]$")
            
        # X TICKS
        label = X_labels[0].upper()
        if label == "MONTH":
            
            ax.set_xticks(X.flatten(), labels = np.tile(months_letters, X_k))
        else:
            ax_xticks_label = check_and_round(np.tile(self.usr_axis[X_labels[0]], X_k))
            step = get_labels_resolution(X_j, width)

            ax.set_xticks(X.flatten()[::step], labels=ax_xticks_label[::step])
        
        # ADDING UNIT
        if units[X_labels[0]] != "":
            label += " [" + units[X_labels[0]] + "]"

        ax.set_xlabel(label)
        
        # Y TICKS AS A VARIABLE
        if not Y_label:
            ax.set_ylabel(variable + " $[" + units[vars[variable]] + "]$")


        fig.set_size_inches(width, height)
        # SAVING
        # USER PARAMETERS ARE IN FILE NAME
        kwargs_str = dict_to_str(kwargs)
        address = "FIGURES/" + variable.upper() + "/" + borders_str + "_" + "_".join(X_labels) + kwargs_str
        if Y_label:
            address += "_" + Y_label
        # EXTENSION
        address += "avg_delta" * avg_delta + ".png"
        plt.savefig(address, dpi=300)

    def figure_two_vars(self, varZ, varX, X_label, need_Zs = False, **kwargs):
        
        varZ = varZ.upper()
        varX = varX.upper()
        
        Zz, Zx = self.figure(varZ, X_label, need_Z = True, **kwargs)
        Xz, Xx = self.figure(varX, X_label, need_Z = True, **kwargs)
        
        Z = (Zz, Xz)
        X = (Zx, Xx)

        args = np.argsort(np.asarray([len(Zz), len(Xz)]))
        print(args)
        shorter_Z, longer_Z = Z[args[0]], Z[args[1]]
        print(shorter_Z)
        print(longer_Z)
        shorter_X, longer_X = X[args[0]], X[args[1]]
        shorter_var = (varZ, varX)[args[0]]

        interpolated_Z = np.empty(shorter_Z.shape)

        for j, x in zip(range(len(shorter_X)), shorter_X):
            
            if x in longer_X:
                indice = np.argwhere(longer_X == x).flatten()
                interpolated_Z[j] = longer_Z[indice[0]]

            else:
                # INTERPOLATION 
                previous_j = np.argmin(np.abs(longer_X - x))
                next_j = previous_j + 1

                previous_x = longer_X[previous_j]
                next_x = longer_X[next_j]

                t = (x - previous_x) / (next_x - previous_x)
                z = t * longer_Z[next_j] + (1 - t) * longer_Z[previous_j]
                
                interpolated_Z[j] = z

        
        if need_Zs:
            if shorter_var == varX:
                return (shorter_X, interpolated_Z, shorter_Z)
            else:
                return (shorter_X, shorter_Z, interpolated_Z)
        
        # MATPLOTLIB
        fig, ax = plt.subplots()

        if shorter_var == varX:
            ax.scatter(shorter_Z, interpolated_Z, color = colors[varZ])
        else:
            ax.scatter(interpolated_Z, shorter_Z, color = colors[varX])
        
        ax.set_ylabel(varZ + " $[" + units[vars[varZ]] + "]$")
        ax.set_xlabel(varX + " $[" + units[vars[varX]] + "]$")
        
        # SAVING
        # USER PARAMETERS ARE IN FILE NAME
        kwargs_str = dict_to_str(kwargs)
        address = "FIGURES/" + varZ + "/" + borders_str + "_" + varX + "_" + kwargs_str + ".png"

        plt.savefig(address, dpi=300)

    def figure_three_vars(self, varZ, varY, varX, X_label, **kwargs):

        varZ = varZ.upper()
        varY = varY.upper()
        varX = varX.upper()    

        X, Zy, Zx = self.figure_two_vars(varY, varX, X_label, need_Zs = True)
        _, Zz, _ = self.figure_two_vars(varZ, varY, X_label, need_Zs = True)

        fig = plt.figure()

        ax = fig.add_subplot(projection = "3d")

        ax.scatter(Zx, Zy, Zz, color = colors[varZ])

        ax.set_zlabel(varZ + " $[" + units[vars[varZ]] + "]$")
        ax.set_ylabel(varY + " $[" + units[vars[varY]] + "]$")
        ax.set_xlabel(varX + " $[" + units[vars[varX]] + "]$")
        
        ax.set_title("All three variables are function of " + X_label)

        kwargs_str = dict_to_str(kwargs)
        address = "FIGURES/" + varZ + "/" + borders_str + "_" + varY + "_" + varX + "_" + kwargs_str + ".png"
       
        plt.savefig(address, dpi=300)
        plt.show()
        

# REGIONS BORDERS : (N, W, S, E)
world_borders = {
    "N" : 90.,
    "W" : -180.,
    "S" : -90.,
    "E" : 180.
}

mediterrannee = {
    "N" : 46.,
    "W" : -6.,
    "S" : 30.,
    "E" : 34.
}

benguela = {
    "N" : -19.,
    "W" : 11.,
    "S" : -32.,
    "E" : 19.
}

borders = benguela

borders_str = "_".join([d + "_" + str(v) for d, v in borders.items()])

# TIMELINE
timeline = np.arange(2003, 2022, 1)

draw = Draw()

# FORMAT : draw.figure_two_vars(str : Y AXIS VAR, str : X AXIS VAR, COMMON X)

draw.figure("dzdt", "longitude max latitude")
# draw.figure("chlorophyll", "month by year", year = [2010, 2011, 2012])
# draw.figure_two_vars("chlorophyll", "nitrate", "longitude")
# draw.figure_two_vars("chlorophyll", "phosphate", "longitude")

# borders = world_borders
# draw.figure_two_vars("nitrate", "chlorophyll", "longitude")
# draw.figure_three_vars("chlorophyll", "phosphate", "nitrate", "longitude")

# draw.figure("dzdt", "month")
