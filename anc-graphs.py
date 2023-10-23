import pandas as pd
from matplotlib import colors
import csv
import os
from configparser import ConfigParser
import argparse
import sys

from tools.math_tools import MathTools
from tools.plot_tools import PlotTools

#setting basic parameters from config file
config = ConfigParser()
config.read('./config.ini')

#basic config
NUMBER_PULSES = int(config.get('Basic Configuration', 'N_PULSES'))
NUMBER_ANCESTRY = int(config.get('Basic Configuration', 'N_ANCESTRIES'))
ANCESTRY_NAMES = config.get('Basic Configuration', 'ANCESTRIES')
ANCESTRY_NAMES = ANCESTRY_NAMES.split(',')
SEXUAL_BIAS = int(config.get('Basic Configuration', 'SEXUAL_BIAS'))

#filter config
FILTER = int(config.get('Filter Configuration', 'FILTER'))
HDR = float(config.get('Filter Configuration', 'HDR'))

#graph config
GRAPH_TYPE = config.get('Graph Configuration', 'GRAPH')
ANCESTRIES_COLOURS = []
temp_colours = config.get('Graph Configuration', 'ANCESTRIES_COLOURS')
temp_colours = temp_colours.split(',')
for col in temp_colours:
    ANCESTRIES_COLOURS.append(colors.to_rgba(col))

SELECT_ANCESTRIES = config.get('Graph Configuration', 'SELECT_ANCESTRIES')
# removing comma if added to last element
if SELECT_ANCESTRIES[-1] == ',': SELECT_ANCESTRIES = SELECT_ANCESTRIES[:-1]
SELECT_ANCESTRIES = SELECT_ANCESTRIES.split(',')

# getting file path from command line
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, required=True)
args = parser.parse_args()
FILE_PATH = args.file

math_tools = MathTools(SEXUAL_BIAS, NUMBER_PULSES, ANCESTRY_NAMES)

plot_tools = PlotTools(SEXUAL_BIAS, NUMBER_PULSES, ANCESTRY_NAMES, ANCESTRIES_COLOURS)

#identifying the delimiter, if there are rows to skip and if the first column shows the row's scenario
with open(FILE_PATH, 'r') as csvfile:
    first_line = csvfile.readline()
    second_line = csvfile.readline()
    dialect = csv.Sniffer().sniff(csvfile.readline())
    delimiter = dialect.delimiter

    first_element = first_line.split(delimiter, 1)[0]
    
    second_element = second_line.split(delimiter, 1)[0]

    try: 
        float(first_element)
        skip_row=0
    except ValueError:
        skip_row=1
    except:
        print("ERROR READING FILE")

    if (float(second_element) == int(float(second_element))) and (float(second_element) != 0):
        first_column_scenario=True
    else: first_column_scenario=False

#creating directory for graphs
if not os.path.exists("./Graphs"):
        os.mkdir("./Graphs")

#assigning ancestry to a string to be passed as a parameter to the c++ script
ancestries_string = str()
for anc in ANCESTRY_NAMES:
    ancestries_string += anc
    ancestries_string += ','
ancestries_string = ancestries_string[:-1]

#compiling c++ code
os.system('g++ ./c++_code/anc-graphs.cpp -o ./c++_code/anc-graphs')

#running c++ code
command = "./c++_code/anc-graphs {} {} {} {} {} {}".format(FILE_PATH, NUMBER_PULSES, NUMBER_ANCESTRY, ancestries_string, int(skip_row), int(first_column_scenario))
os.system('{}'.format(command))

# cleaning c++ code binary
os.remove("./c++_code/anc-graphs")

#reading the files containing scenarios for population
col_names=["Scenario", "Sex", "Pulse", "Ancestry", "Value"]
df = pd.read_csv("./c++_code/input_data.csv", delimiter=' ', header=None, names=col_names)

# cleaning input csv
os.remove("./c++_code/input_data.csv")

#applying HDR filter 
if(FILTER == 1): df = math_tools.filter(HDR, df)

match GRAPH_TYPE:
    case 'bars':
        plot_tools.plot_histograms(df, SELECT_ANCESTRIES, "layer", "./Graphs/histogram.png")
    case 'lines':
        plot_tools.plot_lines(df, SELECT_ANCESTRIES, "./Graphs/line_graph.png")
    case 'min-max-pulse':
        plot_tools.plot_points__with_errorbars(df, SELECT_ANCESTRIES, "./Graphs/point_graph.png")
    case 'min-max-ancestry':
        plot_tools.plot_points__by_ancestry(df, SELECT_ANCESTRIES, "./Graphs/point_graph_ancestry.png")
    case _:
        print("[ERROR] Error in graph type selection. Check config.ini file.")
        sys.exit()

math_tools.write_stats(df, "./stats.csv")