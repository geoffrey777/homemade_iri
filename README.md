# IRI

This script is an attempt to generate figures from various databases like GODAS, WOA, OCEAN COLOR...
And to do basicaly the same thing as mapbox of iri.columbia.edu

## SYNTAX

3 figures generators :
1. draw.figure(variable, X_labels, Y_labels, kwargs)
2. draw.figure_two_vars(variable1, variable2, X_labels, kwargs)
3. draw.figure_three_vars(variable1, variable2, variable3, X_labels, kwargs)

### VARIABLES 
| Name | Database | Unit | labels |
| ----------- | ----------- | ----------- | ----------- |
| chlorophyll | oceancolor | mg.m^{3} | year, month, latitude, longitude |
| sst | oceancolor | °C | year, month, latitude, longitude |
| nitrate | WOA23 | \mu mol.kg^{-1} | month, latitude, longitude |
| phosphate | WOA23 | \mu mol.kg^{-1} | month, latitude, longitude |
| silicate | WOA23 | \mu mol.kg^{-1} | month, latitude, longitude |
| pottemp | GODAS | °C | level, latitude, longitude |
| ucur | GODAS | m.s^{-1} | ? |
| uflx | GODAS | N.m^{-2} | ? |




### LINKS
- WOA23(https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/)
- GODAS(https://psl.noaa.gov/data/gridded/data.godas.html)
- OceanColor(https://oceancolor.gsfc.nasa.gov/l3/)
