import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import colors
import csv
import os

#declaring "constants"
NUMBER_PULSES = 5
NUMBER_ANCESTRY = 4
ANCESTRY_NAMES = ["EUR", "AFR", "NAT", "HYB"]

#colours should be written as the name in here: https://matplotlib.org/stable/gallery/color/named_colors.html
#order must be the same
#if rgba values are to be passed, remove "colors.to_rgba("colour_name")" and pass the rgba value
ANCESTRY_COLOURS = [colors.to_rgba("red"), colors.to_rgba("deepskyblue"), colors.to_rgba("green"), colors.to_rgba("darkviolet")]

# file_path = './data_inputs/output_salvador.txt'
file_path = './data_inputs/output-after-filter-genomic-ancestry_salvador.txt'

#plots histograms for each pulse, separated by sex
#ancestries param should be a list with the ancestries' names, eg. ancestries = ["EUR", "AFR", "NAT", "HYB"]
def plot_histograms(df, ancestries, type, percentage, lines, savefile):
    sexes = ("Female", "Male")
    colours = list()

    for anc in range(0,len(ancestries)):
        if ancestries[anc] in ANCESTRY_NAMES:
            colours.append(ANCESTRY_COLOURS[anc])

    df_hist = df[(df["Ancestry"].isin(ancestries)) & (df["Value"] != 0)]

    graph = sns.FacetGrid(df_hist, col="Sex", row="Pulse", hue="Ancestry", palette=colours)
    graph = (graph.map_dataframe(sns.histplot, x="Value", multiple=type, stat='probability').add_legend())
    
    if lines == True:
        #draw lines in graphs
        for i in range(0, 2):
            axes = graph.axes[i]
            for j in range (0, len(axes)):
                    for anc in range (0, len(ancestries)):
                        if (len(ancestries) == 1 and ancestries[0] == "HYB"): pulse = j+2
                        else: pulse = j+1
                        df_temp = df_hist.loc[(df_hist["Pulse"] == pulse) & (df_hist["Sex"] == sexes[i]) & (df_hist["Ancestry"] == ancestries[anc])]
                        if df_temp.empty:
                            continue
                        #drawing quantile bounds in graph
                        lower_quantile = np.percentile(df_temp["Value"], ((100-percentage)/2), method="closest_observation")
                        upper_quantile = np.percentile(df_temp["Value"], (100-((100-percentage)/2)), method="closest_observation")
                        
                        #quantile bounds lines
                        axes[j].axvline(x=lower_quantile, color=colours[anc], linestyle='--', linewidth=0.8)
                        axes[j].axvline(x=upper_quantile, color=colours[anc], linestyle='--', linewidth=0.8)
                        
                        #mode line
                        axes[j].axvline(x=find_mode(df_temp), color="black", linestyle=':', linewidth=1.2)
    plt.xlim([0, 1])
    graph.savefig(savefile)

#plots the line graph and saves
#ancestries param should be a list with the ancestries' names, eg. ancestries = ["EUR", "AFR", "NAT", "HYB"]
#if lines=True, the graph will show mode and quantiles for the percentage
def plot_lines(df, ancestries, percentage, lines, savefile):
    sexes = ("Female", "Male")
    colours = list()

    for anc in range(0,len(ancestries)):
        if ancestries[anc] in ANCESTRY_NAMES:
            colours.append(ANCESTRY_COLOURS[anc])

    df_hist = df[(df["Ancestry"].isin(ancestries)) & (df["Value"] != 0)]

    graph = sns.FacetGrid(df_hist, col="Sex", row="Pulse", hue="Ancestry", palette=colours)
    graph = (graph.map_dataframe(sns.histplot, x="Value", fill=False, linewidth=0, kde=True, stat='probability'))

    if lines == True:
        #draw lines in graphs
        for i in range(0, 2):
            axes = graph.axes[i]
            for j in range (0, len(axes)):
                    for anc in range (0, len(ancestries)):
                        if (len(ancestries) == 1 and ancestries[0] == "HYB"): pulse = j+2
                        else: pulse = j+1
                        df_temp = df_hist.loc[(df_hist["Pulse"] == pulse) & (df_hist["Sex"] == sexes[i]) & (df_hist["Ancestry"] == ancestries[anc])]
                        if df_temp.empty:
                            continue
                        #drawing quantile bounds in graph
                        lower_quantile = np.percentile(df_temp["Value"], ((100-percentage)/2), method="closest_observation")
                        upper_quantile = np.percentile(df_temp["Value"], (100-((100-percentage)/2)), method="closest_observation")

                        #quantile bounds lines
                        axes[j].axvline(x=lower_quantile, color=colours[anc], linestyle='--', linewidth=0.8)
                        axes[j].axvline(x=upper_quantile, color=colours[anc], linestyle='--', linewidth=0.8)
                        
                        #mode line
                        axes[j].axvline(x=find_mode(df_temp), color="black", linestyle=':', linewidth=1.2)

    plt.xlim([0, 1])
    
    #drawing the legend for each ancestry
    legend = list()
    for anc in range (0, len(ancestries)):
        legend.append(mlines.Line2D([], [], color=colours[anc], marker='s', ls='', label=ancestries[anc]))
    graph.figure.legend(handles=legend, loc=7, title="Ancestry", frameon=False)
    graph.figure.tight_layout()
    graph.figure.subplots_adjust(right=0.9)
    
    graph.savefig(savefile)


def plot_points__with_errorbars(df, ancestries, percentage, lines, savefile):
    sexes = ("Female", "Male")
    colours = list()

    for anc in range(0,len(ancestries)):
        if ancestries[anc] in ANCESTRY_NAMES:
            colours.append(ANCESTRY_COLOURS[anc])

    figure, axis = plt.subplots(1, NUMBER_PULSES)
    figure.set_figwidth(8 + 4*len(ancestries))
    figure.set_figheight(4)
    
    #setting ticks and their lables
    ticks = list()
    labels = list()
    
    for anc in range(0,len(ancestries)):
        ticks.append((1/(len(ancestries)+1))*(anc+1))
        labels.append(ancestries[anc])

    df_plot = df
    for pulse in range(1,(NUMBER_PULSES+1)):
        for anc in range(0,len(ancestries)):
            for sex in range(0,2):
                #selecting only the values from this pulse, sex and ancestry
                df_temp = df_plot[(df_plot["Pulse"] == pulse) & (df_plot["Sex"] == sexes[sex]) & (df_plot["Ancestry"] == ancestries[anc])]
                
                #calculating values
                min_temp = df_temp["Value"].min()
                max_temp = df_temp["Value"].max()
                mean_temp = df_temp["Value"].mean()

                #darkening the colour if gender is male
                colour = [0.0, 0.0, 0.0, 1.0]
                for i in range(0, len(colour)-1):
                    colour[i] = max(0, (colours[anc][i] - 0.25*sex))

                #plotting point
                buffer = 0.25 - 0.05 * len(ancestries)
                point_x = (-buffer/2 + ((1/(len(ancestries)+1))*(anc+1))) + buffer*sex
                axis[pulse-1].plot(point_x, mean_temp, marker='o', markersize=6, color=colour)

                #plotting min and max lines
                lines_x = [point_x - (0.015 * 4/(len(ancestries))), point_x + (0.015 * 4/(len(ancestries)))]
                axis[pulse-1].plot(lines_x, [min_temp, min_temp], linewidth=1.2, color=colour, alpha=1)
                axis[pulse-1].plot(lines_x, [max_temp, max_temp], linewidth=1.2, color=colour, alpha=1)
                
                #connecting line
                axis[pulse-1].plot([point_x, point_x], [min_temp, max_temp], linewidth=1, linestyle='--', color=colour, alpha=0.9)

        #setting axis limits, ticks and title
        axis[pulse-1].set_xlim(0, 1)
        axis[pulse-1].set_ylim(0, 1)
        axis[pulse-1].set_xticks(ticks, labels)
        axis[pulse-1].set_title("Pulse {}".format(pulse))

    #drawing the legend for each ancestry
    legend = list()
    for anc in range (0, len(ancestries)):
        legend.append(mlines.Line2D([], [], color=colours[anc], marker='o', ls='', label=ancestries[anc]))
    figure.legend(handles=legend, loc=7, title="Ancestry", frameon=False)
    figure.tight_layout(pad=2)
    figure.subplots_adjust(right=0.925)
    
    figure.savefig(savefile)

#filters data by the Highest Density Region, informed by the percentage
#90% region -> percentage = 90
def filter(percentage, df_unfiltered):
    ancestries = ("EUR", "AFR", "NAT", "HYB")
    sexes = ("Female", "Male")
    scenarios = set(())
    df_filtered = df_unfiltered

    for sex in range(0,2):
        for pulse in range(1,(NUMBER_PULSES+1)):
            for anc in range(0,NUMBER_ANCESTRY):
                #selecting only the values from this pulse, sex and ancestry
                df_temp = df_filtered[(df_filtered["Pulse"] == pulse) & (df_filtered["Sex"] == sexes[sex]) & (df_filtered["Ancestry"] == ancestries[anc])]
                
                #calculating the percentile values
                lower_quantile = np.percentile(df_temp["Value"], ((100-percentage)/2), method="closest_observation")
                upper_quantile = np.percentile(df_temp["Value"], (100-((100-percentage)/2)), method="closest_observation")

                size = df_temp.shape[0]
                #avoiding the null stats (HYB percentages in the first pulse)
                if lower_quantile != 0:
                    #searches for the scenarios that are outside the 90% HDR
                    for i in range(size):
                        #if the value is outside the quantiles, we add to the set of scenarios which will be filtered out
                        if ((df_temp.iloc[i][4] < lower_quantile) or (df_temp.iloc[i][4] > upper_quantile)):
                            scenarios.add(df_temp.iloc[i][0])

    #applies the HDR filter
    df_filtered = df_filtered[~df_filtered["Scenario"].isin(scenarios)]
    return df_filtered

# Function to find mode from the continuous data
def find_mode(df):
    if df.empty:
        return 0
    
    #calculating number of bins using IQR
    Q1 = np.quantile(df["Value"], 0.25)
    Q3 = np.quantile(df["Value"], 0.75)
    IQR = Q3 - Q1
    cube = np.cbrt(len(df["Value"]))
    bin_width = 2*IQR/cube
    if bin_width == 0: return 0
    n_bins = round(1/bin_width, 0)    

    hist = np.histogram(df["Value"], bins=int(n_bins))

    count_max=0
    mode=0

    for i in range(len(hist[0])):
        if hist[0][i] > count_max:
            count_max = hist[0][i]
            mode = (hist[1][i] + hist[1][i+1])/2

    return round(mode, 2)

#writes data's statistics in a csv file
def write_stats(df, file_name):
    ancestries = ("EUR", "AFR", "NAT", "HYB")
    sexes = ("Female", "Male")

    header = ["Sex", "Pulse", "Ancestry", "Min", "Mean", "Median", "Max", "Mode", "Std"]

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(header)

        for i in range (0, 2):
            for j in range (1, 6):
                    for k in range (0, 4):
                        df_temp = df.loc[(df["Pulse"] == j) & (df["Sex"] == sexes[i])]
                        anc = df_temp.loc[(df_temp["Ancestry"] == ancestries[k])]
                        # print(f'Pulse', j, sexes[i], ancestries[k])

                        row = [sexes[i], j, ancestries[k], anc["Value"].min(), anc["Value"].mean(), anc["Value"].median(), anc["Value"].max(), find_mode(anc), anc["Value"].std()]
                        writer.writerow(row)

#function creates folders for graphs, if they don't exist yet                    
def create_directories():   
    directory = "HDR"
    parent_directory = "./"
    path = os.path.join(parent_directory, directory)
    if not os.path.exists(path):
        os.mkdir(path)
        
        directory = "Hybrid_Separated"
        parent_directory = "./HDR/"
        path = os.path.join(parent_directory, directory)
        if not os.path.exists(path):
            os.mkdir(path)
        
        directory = "Standard"
        parent_directory = "./HDR/"
        path = os.path.join(parent_directory, directory)
        if not os.path.exists(path):
            os.mkdir(path)
        
    directory = "NO_HDR"
    parent_directory = "./"
    path = os.path.join(parent_directory, directory)
    if not os.path.exists(path):
        os.mkdir(path)
        directory = "Hybrid_Separated"
        parent_directory = "./NO_HDR/"
        path = os.path.join(parent_directory, directory)
        if not os.path.exists(path):
            os.mkdir(path)
        directory = "Standard"
        parent_directory = "./NO_HDR/"
        path = os.path.join(parent_directory, directory)
        if not os.path.exists(path):
            os.mkdir(path)

#identifying the delimiter, if there are rows to skip and if the first column shows the row's scenario
with open(file_path, 'r') as csvfile:
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
        print("opa2")

    if (float(second_element) == int(float(second_element))) and (float(second_element) != 0):
        first_column_scenario=True
    else: first_column_scenario=False



#assigning ancestry to a string to be passed as a parameter to the c++ script
ancestries_string = str()
for anc in ANCESTRY_NAMES:
    ancestries_string += anc
    ancestries_string += ','
ancestries_string = ancestries_string[:-1]

#running c++ script
command = "./script_c {} {} {} {} {} {}".format(file_path, NUMBER_PULSES, NUMBER_ANCESTRY, ancestries_string, int(skip_row), int(first_column_scenario))
os.system('{}'.format(command))

#reading the files containing scenarios for population
col_names=["Scenario", "Sex", "Pulse", "Ancestry", "Value"]
df = pd.read_csv("./input_data2.csv", delimiter=' ', header=None, names=col_names)

create_directories()

ancestries = ["EUR", "AFR", "NAT", "HYB"]
plot_histograms(df, ancestries, "layer", 90, False, "./NO_HDR/Standard/histogram.png")
plot_lines(df, ancestries, 90, False, "./NO_HDR/Standard/line_graph.png")
plot_points__with_errorbars(df, ancestries, 90, False, "./NO_HDR/Standard/point_graph.png")

ancestries = ["EUR", "AFR", "NAT"]
plot_histograms(df, ancestries, "layer", 90, False, "./NO_HDR/Hybrid_Separated/no_hybrid_histogram.png")
plot_lines(df, ancestries, 90, False, "./NO_HDR/Hybrid_Separated/no_hybrid_line_graph.png")
plot_points__with_errorbars(df, ancestries, 90, False, "./NO_HDR/Hybrid_Separated/no_hybrid_point_graph.png")

ancestries = ["HYB",]
plot_histograms(df, ancestries, "layer", 90, False, "./NO_HDR/Hybrid_Separated/only_hybrid_histogram.png")
plot_lines(df, ancestries, 90, False, "./NO_HDR/Hybrid_Separated/only_hybrid_line_graph.png")
plot_points__with_errorbars(df, ancestries, 90, False, "./NO_HDR/Hybrid_Separated/only_hybrid_point_graph.png")

write_stats(df, "./stats_NO_HDR.csv")

#filtering for only 90% of density
df_filtered = filter(90, df)

ancestries = ["EUR", "AFR", "NAT", "HYB"]
plot_histograms(df, ancestries, "layer", 90, False, "./HDR/Standard/histogram.png")
plot_lines(df, ancestries, 90, False, "./HDR/Standard/line_graph.png")
plot_points__with_errorbars(df, ancestries, 90, False, "./HDR/Standard/point_graph.png")

ancestries = ["EUR", "AFR", "NAT"]
plot_histograms(df, ancestries, "layer", 90, False, "./HDR/Hybrid_Separated/no_hybrid_histogram.png")
plot_lines(df, ancestries, 90, False, "./HDR/Hybrid_Separated/no_hybrid_line_graph.png")
plot_points__with_errorbars(df, ancestries, 90, False, "./NO_HDR/Hybrid_Separated/no_hybrid_point_graph.png")

ancestries = ["HYB",]
plot_histograms(df, ancestries, "layer", 90, False, "./HDR/Hybrid_Separated/only_hybrid_histogram.png")
plot_lines(df, ancestries, 90, False, "./NO_HDR/Hybrid_Separated/only_hybrid_line_graph.png")
plot_points__with_errorbars(df, ancestries, 90, False, "./HDR/Hybrid_Separated/only_hybrid_point_graph.png")

write_stats(df_filtered, "./stats_HDR.csv")