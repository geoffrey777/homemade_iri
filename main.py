# coding=utf-8

from matplotlib import pyplot as plt
import numpy as np
import matplotlib as mpl

from data import *

print(days)

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
        value.sort()
        value = list_to_str(value)

        #print([str(v) for v in value])
        str += key + "_(" + "_".join(value) + ")"
    return str

def get_labels_resolution(length, dimension):
    resolution_min = 1. #inch
    length_max = dimension / resolution_min
    step = int( length / length_max )
    return step

def check_and_round(arr):
    if type(arr[0]) == np.float32:
        return np.round(arr, 2)
    return arr

class Draw:
    def __init__(self, axis, data, var, unit):

        self.axis = axis
        self.data = data
        
        self.var = var
        self.unit = unit

        self.labels = list(axis.keys())

        self.ps = length_dict(axis)

    def generate_usr_data(self, X_label, Y_label, **kwargs):
        self.usr_data = data.copy()
        self.usr_axis = self.axis
        self.avg_axis = []

        # UPDATING DATA AS USER PREFERENCES
        for label in kwargs.keys():
           
            i = self.labels.index(label)
            usr_values = kwargs[label]
            
            values = self.axis[label]
            
            # IS INSIDE THE RANGE OF VALUES?
            # ASSUMING VALUES ARE SORTED
            Min = values[0]
            Max = values[-1]

            inf_min = set(usr_values < Min)
            sup_max = set(usr_values > Max)

            if len(inf_min) > 1:
                raise Exception("One (or more) " + label + " is(are) below the minimum")
            
            if len(sup_max) > 1:
                raise Exception("One (or more) " + label + " is(are) above the maximum")

            # SO, ALL USR_VALUES ARE IN THE INTERVAL
            # TAKING THE NEAREST IN CASE OF ?
            usr_indices = []
            for usr_value in usr_values:
                # print(values)
                
                usr_indices.append(np.argmin(abs(values-usr_value)))

            usr_indices_complement = np.delete(np.arange(self.ps[label]), usr_indices)
               
            # REMOVING INDICES
            self.usr_axis[label] = np.delete(self.usr_axis[label], usr_indices_complement)

            self.usr_data = np.delete(self.usr_data, usr_indices_complement, axis=i)

            self.ps[label] -= len(usr_indices_complement)

        X_labels = X_label.split()

        for i, label in zip(range(len(self.axis)), self.labels):

            # LABEL IS A VARIABLE
            if label in X_labels or label == Y_label:
                # LABEL IS A VARIABLE
                print(label.upper() + " is a variable")

            # LABEL VALUES AVERAGE
            else:
                print("An average over " +  label.upper() + " has been calculated.")
                self.avg_axis.append(i)

                
    def figure(self, X_label, Y_label = None, avg_delta = False, **kwargs):

        # if len(X) == 0:
        #     raise Exception("Need X axis")
        
        self.generate_usr_data(X_label, Y_label, **kwargs)
        
        # FIGURE DIMENSIONS
        width = 7.4
        height = np.round(0.75*width, 2)

        # MATPLOTLIB
        fig, ax = plt.subplots()
        
        # X THINGS
        X_labels = X_label.split()
        # GROUPED SIZE
        X_j = self.ps[X_labels[0]]
        # GROUP SIZE
        X_k = 1
        # DEFAULT X
        X = np.arange(X_j)# self.axis[X[0]]

        # SAME ROUTINE FOR Y
        if Y_label:
            Y_labels = Y_label.split()
            Y_j = self.ps[Y_label]
            Y_k = 1
            Y = np.arange(Y_j)

        Z = np.average(self.usr_data, axis=tuple(self.avg_axis))

        # 1D FIGURE : SCATTER / HIST
        if not Y_label:

            # MULTIPLES LINES
            if len(X_labels) > 1:

                # UPDATING GROUP SIZE
                k = self.ps[X_labels[-1]]

                # MULTIPLE LINES IN LEGEND
                # j GROUPED IN X-AXIS
                # k GROUP IN LEGEND
                if X_labels[1] == "and":
                    if X_k == 1:
                        raise Exception("You have given only one " + X_labels[-1] + " so 'and' keyword is useless just try : '" + X_labels[0] + "'")

                    for z, value in zip(Z, self.usr_axis[X_labels[-1]]):
                        print(self.axis[X_labels[-1]])
                        ax.scatter(X, z, label=value)

                    ax.legend()

                # MULTIPLE LINES IN A ROW
                # k*j GROUPED IN X-AXIS
                elif X_labels[1] == "by":
                    
                    X = np.arange(X_j*X_k)
                    X = np.reshape(X, (X_k,X_j))

                    print(X.shape)
                    print(Z.shape)

                    if not X.shape == Z.shape:
                        Z = np.reshape(Z, X.shape)

                    for x, z in zip(X, Z):
                        
                        #ax.scatter(x,z)
                        ax.plot(x, z)

                else:
                    raise Exception("Keyword in X label sentence is incorrect")

            else:
                
                if avg_delta:
                    Z = Z - np.average(Z)

                ax.scatter(X, Z)

            ax.set_ylabel(self.var.upper() + "[" + units[var] + "]")
                    
        # 2D FIGURE = IMSHOW
        else:
            # Y TICKS
            ax_yticks_label = check_and_round(np.repeat(self.axis[Y_labels[0]], Y_k))# TODO Y_LABELS
            step = get_labels_resolution(Y_j, height)
            
            ax.set_yticks(Y.flatten()[::step], labels=ax_yticks_label[::step])

            label = Y_labels[0].upper()
            # ADDING UNIT
            if units[Y_labels[0]] != "":
                label += " [" + units[Y_labels[0]] + "]"
            ax.set_ylabel(label)
            
            # CHECKING X, Y ORDER
            XY_shape = (Y.shape[0], X.shape[0])
            
            if not XY_shape == Z.shape:
                Z = np.reshape(Z, XY_shape)
        
            im = ax.imshow(Z[::-1], aspect="auto", cmap="coolwarm")
            fig.colorbar(im, ax=ax, label = var.upper() + " [" + units[var] + "]")
            
        # X TICKS
        ax_xticks_label = check_and_round(np.repeat(self.axis[X_labels[0]], X_k))
        step = get_labels_resolution(X_j, width)

        ax.set_xticks(X.flatten()[::step], labels=ax_xticks_label[::step])
        label = X_labels[0].upper()
        # ADDING UNIT
        if units[X_labels[0]] != "":
            label += " [" + units[X_labels[0]] + "]"
        ax.set_xlabel(label)
        
        fig.set_size_inches(width, height)
        # SAVING
        # USER PARAMETERS ARE IN FILE NAME
        kwargs_str = dict_to_str(kwargs)
        address = "FIGURES/" + self.var.upper() + "/" + "_".join(X_labels) + kwargs_str
        if Y_label:
            address += "_" + Y_label
        # EXTENSION
        address += ".png"
        plt.savefig(address, dpi=300)

# print(temp_nc.variables)

# REGION BORDERS : (N, W, S, E)
borders = (90., -180., -90., 180.)
# TIMELINE
timeline = np.arange(2002, 2022, 1)

sshg_draw = Draw(axis, data, var, unit)# adding color!
sshg_draw.figure("longitude", "latitude", avg_delta=True)