# About
_Code made by Pedro Baptista._

This code extracts graphs and statistics from a series of scenarios from a .txt file

# How To Use
For ease of use, most of the code configuration is made in the config.ini file, while only the input file path is passed by a parameter in the command line. These are as follows:
### Command Parameters
```
--file or -f              .txt file path
```


### Config.ini Parameters
```
[Basic Configuration]
N_PULSES=                Number of pulses (integer greater than 0)
N_ANCESTRIES=            Number of ancestries (integer greater than 0)
ANCESTRIES=              Names of all ancestries in the file (number of names must be the same as the number of ancestries)
                         Separate names with comma (eg.: EUR,AFR,NAT)

[Filter Configuration]
FILTER=                  Filters the distribution by the Highest Density Region (set as 0 or 1)
HDR=                     Percentage of HDR filter (value from 0 to 100)

[Graph Configuration]
GRAPH=                   Graph type (without quotes): 'bars', 'lines', 'min-max-pulse' or 'min-max-ancestry'
ANCESTRIES_COLOURS=      Names of the ancestries' colours, taken from https://matplotlib.org/stable/gallery/color/named_colors.html
                         The order of the colours should be the same as the ancestries in ANCESTRIES parameter
SELECT_ANCESTRIES=       Names of all ancestries to be plotted in the graphs (at least one should be passed)
```
# Output
## Graph Types
### Bar Graph
Graph of ancestry percentage in the population by the probability of said percentage. Separated by pulses and sex.
### Line Graph
Graph containing same information as the bar graph. Instead of bars, shows a distribution line.
### Min-Max Point Graph
Graph that shows the average, minimum and maximum values of each ancestry. The values are separated by sex, which is indicated by the difference in colors of the points and bars: the female-related are slightly lighter while the male-related are slightly darker. The graph can be organized either by pulse or by ancestry.
## Statistics
The code generates a .csv file containing the following statistics for each combination of sex, pulse and ancestry:
- Minimum
- Mean
- Median
- Max
- Mode
- Standard Deviation
# Code Structure
_This section explains important parts of the code design and functionality._
## Input Handling
### Header and Scenario Column
The input file informs the percentages of each ancestry for each pulse, separated by sex. Normally, the .txt file has only the percentage values. But it is also common to first filter some scenarios using an R script and, if so, the file would have a header in the first line and the scenario number in the first column. This script automatically identifies these alterations and adjusts the read routine accordingly.

The header will always be ignored if the first element is not a number (more specifically, if the first word cannot be turned into a float type variable). The first column will be considered the scenario if the second line's first word is not a percentage value (if the float and integer interpretations of the number are the same).
### Input Processing and C++ Code
The [Pandas library](https://pandas.pydata.org/) was used to more easily handle data and plot graphs. The library offers a relatively fast way of importing data through the [read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) method. Changing the original input file to fit this method using common Python methods is excessively slow and, as such, a C++ code was written to make this process significantly faster. A .csv file is created, which is then read by the _read_csv_ method normally.

Depending on the computer running the program, a already compiled C++ code may not run properly. To circumvent this problem, the C++ code is compiled in each execution using the G++ compiler, distributed by the GNU Compiler Collection.
## Graph Types
### Bar Graph
Graph calculated using the  Distribution is separated into bins using the maximum between [Sturges' formula](https://en.wikipedia.org/wiki/Histogram#Sturges'_formula) and [Freedman-Diaconis' choice](https://en.wikipedia.org/wiki/Histogram#Freedman%E2%80%93Diaconis'_choice), as is standard in the [Matplotlib library](https://matplotlib.org/).
### Line Graph
This graph is plotted using the same method as the bar graph, but the bars are hidden. The distribution line which is using [Kernel Density Estimation](https://en.wikipedia.org/wiki/Kernel_density_estimation).
## HDR Filter
The data can be filtered and include only the Highest Density Region. The filter first calculates the percentiles which the area between them results in the desired percentage for each combination of sex, pulse and ancestry. Then, it searches for scenarios that have values outside the area between the percentages and excludes them from the distribution. This means that each scenario has every value evaluated in relation to its respective sex, pulse and ancestry and is only included in the distribution if all values pass the filter.
## Statistics
The statistics were extracted from their respective Pandas methods, with the exception of the mode. Because the distribution is continuous, to find the mode it was necessary to divide the distribution into bins (using the [Freedman-Diaconis' choice](https://en.wikipedia.org/wiki/Histogram#Freedman%E2%80%93Diaconis'_choice)) and the bin with most observations was selected as the mode. The value was then rounded to three decimal spaces.
