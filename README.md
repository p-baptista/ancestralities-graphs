# About
_Code made by Pedro Baptista._

This code extracts graphs and statistics from a series of scenarios from a .txt file

## How To Use
For ease of use, code configuration is made in the config.ini file. There, the following parametres must be passed:
```
N_PULSES=                Number of pulses
N_ANCESTRIES=            Number of ancestries
ANCESTRIES=              Names of all ancestries in the file
SELECT_ANCESTRIES=       Names of all ancestries to be plotted in the graphs
```

### Parameters
```
--file or -f              .txt file path
--graph or -g             Graph type to be created
```
### Optional Parameters
```
--hdr or -h               Percentage of Highest Density filter to be applied (default set to 100%)
```
## Output
The resulting graphs