# HOMEMADE IRI

This script is an attempt to generate figures from various databases like GODAS, WOA, OCEAN COLOR...

## SYNTAX

borders = {
N : float,
W : float,
S : float,
E : float
}
Already defined:
- world_borders,
- benguela,
- mediterrannee.

3 figures generators :
1. draw.figure(variable, X_labels, Y_labels, kwargs)
2. draw.figure_two_vars(variable1, variable2, X_labels, kwargs)
3. draw.figure_three_vars(variable1, variable2, variable3, X_labels, kwargs)

### TYPE
| variable | str |
| X_labels | list of str |
| Y_labels | list of str |
| kwargs | label = [list of values to restrict the selection] |

### VARIABLES 
| Name | Database | Unit | labels |
| ----------- | ----------- | ----------- | ----------- |
| chlorophyll | oceancolor | mg.m^{3} | year, month, latitude, longitude |
| sst | oceancolor | °C | year, month, latitude, longitude |
| nitrate | WOA23 | \mu mol.kg^{-1} | depth, latitude, longitude |
| phosphate | WOA23 | \mu mol.kg^{-1} | depth, latitude, longitude |
| silicate | WOA23 | \mu mol.kg^{-1} | depth, latitude, longitude |
| pottemp | GODAS | K | year, month, level, latitude, longitude |
| ucur | GODAS | m.s^{-1} | year, month, level, latitude, longitude |
| uflx | GODAS | N.m^{-2} | year, month, latitude, longitude |
| vcur | GODAS | m.s^{-1} | year, month, level, latitude, longitude |
| vflx | GODAS | N.m^{-2} | year, month, latitude, longitude |

### MORE OPTIONS

**and** : draw.figure(variable, "label1 and label2", label2 = [value1, ...]) will display variable in terms of label1 for label2 = value1 AND variable in terms of label1
for label2 = value2...

**by** : draw.figure(variable, "label1 by label2", label2 = [value1, ...]) will display variable in terms of label1 grouped
by label2'values

**max** and **min** : draw.figure(variable, "label1 max label2") will display the max value of variable 
over the label2 axis in terms of label1 values

### Examples


### LINKS
- [WOA23](https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/)
- [GODAS](https://psl.noaa.gov/data/gridded/data.godas.html)
- [OceanColor](https://oceancolor.gsfc.nasa.gov/l3/)
- [IRI MAPROOM](https://iridl.ldeo.columbia.edu/maproom/index.html)
