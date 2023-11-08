from matplotlib import colors
from configparser import ConfigParser
import argparse

from tools.math_tools import MathTools
from tools.plot_tools import PlotTools
from tools.code_integrity import CodeIntegrity
from tools.input_reader import InputReader

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

try: CodeIntegrity.check_tools_folder()
except Exception as error:
    print(f"[UNEXPECTED ERROR] {error}")
    exit()

CodeIntegrity.check_output_folders()

#assigning ancestry to a string to be passed as a parameter to the c++ script
ancestries_string = str()
for anc in ANCESTRY_NAMES:
    ancestries_string += anc
    ancestries_string += ','
ancestries_string = ancestries_string[:-1]

input_reader = InputReader(FILE_PATH, NUMBER_PULSES, NUMBER_ANCESTRY, ancestries_string, SEXUAL_BIAS)

df = input_reader.read_input()

#applying HDR filter 
if(FILTER == 1): df = math_tools.filter(HDR, df)

match GRAPH_TYPE:
    case 'bars':
        plot_tools.plot_histograms(df, SELECT_ANCESTRIES, "layer", "./Outputs/Graphs/histogram.png")
    case 'lines':
        plot_tools.plot_lines(df, SELECT_ANCESTRIES, "./Outputs/Graphs/line_graph.png")
    case 'point-pulse':
        plot_tools.plot_points__with_errorbars(df, SELECT_ANCESTRIES, "./Outputs/Graphs/point_graph_pulse.png")
    case 'point-ancestry':
        plot_tools.plot_points__by_ancestry(df, SELECT_ANCESTRIES, "./Outputs/Graphs/point_graph_ancestry.png")
    case 'priori_posteriori':
        plot_tools.priori_posteriori(df, math_tools.filter(HDR, df), SELECT_ANCESTRIES, "./Outputs/Graphs/weird.png")
    case _:
        print("[ERROR] Error in graph type selection. Check config.ini file.")
        exit()

math_tools.write_stats(df, "./Outputs/Statistics/stats.csv")