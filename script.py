import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

#declaring "constants"
NUMBER_PULSES = 5
NUMBER_ANCESTRY = 4

#creates a new dataframe from raw input dataframe
def populate_dataframe(df_raw, first_column_scenario):
    length = int(df_raw.shape[0]*(2*NUMBER_PULSES*NUMBER_ANCESTRY))
    entries = np.empty((length, 5), dtype=object)
    n_entries=0

    #populating new dataframe
    for i in range (df_raw.shape[0]):
        if first_column_scenario == True: j = 1
        else: j = 0
        for j in range (j, df_raw.shape[1]):
            #assigning gender to new row
            if j < (df_raw.shape[1])/2: sex = "Female"
            else: sex = "Male"

            #assigning scenario
            if first_column_scenario == True: scenario = int(df_raw.iloc[i][0])
            else: scenario = i+1
            
            #assigning pulse
            if first_column_scenario == True: pulse = int(((np.floor((j-1)/NUMBER_ANCESTRY))%5)+1)
            else: pulse = int(((np.floor(j/NUMBER_ANCESTRY))%5)+1)

            #assigning ancestry
            ancestries = ("EUR", "AFR", "NAT", "HYB")
            if first_column_scenario == True: ancestry = ancestries[((j-1)%4)]
            else: ancestry = ancestries[((j)%4)]

            #assigning value of ancestry
            value = float(df_raw.iloc[i][j])

            new_entry = (scenario, sex, pulse, ancestry, value)
            entries[n_entries] = new_entry
            n_entries += 1

    df_new = pd.DataFrame(data = entries, columns=["Scenario", "Sex", "Pulse", "Ancestry", "Value"])
    return df_new

#plots graphs for each pulse, separated by sex
def plot_histograms(df, hybrid, type, savefile):
    if hybrid == "no_hybrid": 
        df_temp = df[(df["Ancestry"] != "HYB") & (df["Value"] != 0)]
        colors = ["red", "deepskyblue", "green"]
    elif hybrid == "only_hybrid":
        df_temp = df[(df["Ancestry"] == "HYB") & (df["Value"] != 0)]
        colors = ["darkviolet"]
    else:
        df_temp = df[(df["Value"] != 0)]
        colors = ["red", "deepskyblue", "green", "darkviolet"]
    
    max = df_temp["Value"].max()

    graph = sns.FacetGrid(df_temp, col="Pulse", row="Sex", hue="Ancestry", palette=colors)
    graph = (graph.map_dataframe(sns.histplot, x="Value", multiple=type).add_legend())
    # graph.set(yscale="log")
    plt.xlim([0, max])
    graph.savefig(savefile)

def make_bins(df, bins):
    if df.empty:
        return np.empty((0, 2), dtype=object)    
    bin_series = pd.Series(df["Value"].value_counts(bins=bins))
    new_bins = np.empty((len(bin_series), 2), dtype=object)
    for i in range(0, len(bin_series)):
        interval = str(bin_series[bin_series == bin_series.iat[i]].index[0])
        interval = (interval.split(" ",1)[1])
        interval = (interval.split("]",1)[0])
        interval = float(interval)
        new_bins[i] = (interval, bin_series.iat[i])
    return new_bins

def plot_lines(df, hybrid, bins, savefile):
    if hybrid == "no_hybrid":
        df_temp = df[(df["Ancestry"] != "HYB") & (df["Value"] != 0)]
        colors = ["red", "deepskyblue", "green"]
        ancestries = ("EUR", "AFR", "NAT")
    elif hybrid == "only_hybrid":
        df_temp = df[(df["Ancestry"] == "HYB") & (df["Value"] != 0)]
        colors = ["darkviolet"]
        ancestries = ("HYB",)
    else:
        df_temp = df[(df["Value"] != 0)]
        colors = ["red", "deepskyblue", "green", "darkviolet"]
        ancestries = ("EUR", "AFR", "NAT", "HYB")

    entries = np.empty((2*5*len(ancestries)*bins, 5), dtype=object)
    n_entries = 0
    
    sexes = ("Female", "Male")
    for i in range (0, 2):
        for j in range (1, 6):
            for k in range (0, len(ancestries)):
                df_bins = df_temp.loc[(df_temp["Pulse"] == j) & (df_temp["Sex"] == sexes[i]) & (df_temp["Ancestry"] == ancestries[k])]
                new_bins = make_bins(df_bins, bins)
                if not (len(new_bins) < 1):
                    for l in range(0, bins):
                        new_entry = (sexes[i], j, ancestries[k], new_bins[l][0], new_bins[l][1])
                        entries[n_entries] = new_entry
                        n_entries += 1

    
    df_lines = pd.DataFrame(data = entries, columns=["Sex", "Pulse", "Ancestry", "Value", "Count"])

    graph = sns.FacetGrid(df_lines, col="Pulse", row="Sex", hue="Ancestry", palette=colors)
    graph = (graph.map_dataframe(sns.lineplot, x="Value", y="Count"))
    # graph.set(yscale="log")
    plt.xlim([0, 1])
    graph.savefig(savefile)

def filter(percentage, df_unfiltered):
    ancestries = ("EUR", "AFR", "NAT", "HYB")
    sexes = ("Female", "Male")
    scenarios = set(())
    df_filtered = df_unfiltered

    for sex in range(0,2):
        for pulse in range(1,6):
            for anc in range(0,4):
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

def write_stats(df, file_name):
    ancestries = ("EUR", "AFR", "NAT", "HYB")
    sexes = ("Female", "Male")

    header = ["Sex", "Pulse", "Ancestry", "Min", "Mean", "Median", "Max", "Std"]

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(header)

        for i in range (0, 2):
            for j in range (1, 6):
                    for k in range (0, 4):
                        df_temp = df.loc[(df["Pulse"] == j) & (df["Sex"] == sexes[i])]
                        anc = df_temp.loc[(df_temp["Ancestry"] == ancestries[k])]

                        row = [sexes[i], j, ancestries[k], anc["Value"].min(), anc["Value"].mean(), anc["Value"].median(), anc["Value"].max(), anc["Value"].std()]
                        writer.writerow(row)
                    
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

#reading the files containing scenarios for population
df = pd.read_csv('./data_outputs/output_salvador.txt', delimiter=' ', header=None)
# df = pd.read_csv('./data_outputs/output-after-filter-genomic-ancestry_salvador.txt', delimiter='\t', header=None, skiprows=1)

#treating the raw data and creating the new dataframe
df_new = populate_dataframe(df, False)
del df

create_directories()

plot_histograms(df_new, "with_hybrid", "layer", "./NO_HDR/Standard/histogram.png")
plot_lines(df_new, "with_hybrid", 20, "./NO_HDR/Standard/line_graph.png")
plot_histograms(df_new, "no_hybrid", "layer", "./NO_HDR/Hybrid_Separated/no_hybrid_histogram.png")
plot_lines(df_new, "no_hybrid", 20, "./NO_HDR/Hybrid_Separated/no_hybrid_line_graph.png")
plot_histograms(df_new, "only_hybrid", "layer", "./NO_HDR/Hybrid_Separated/only_hybrid_histogram.png")
plot_lines(df_new, "only_hybrid", 20, "./NO_HDR/Hybrid_Separated/only_hybrid_line_graph.png")

#filtering for only 90% of density
df_new = filter(90, df_new)

plot_histograms(df_new, "with_hybrid", "layer", "./HDR/Standard/histogram.png")
plot_lines(df_new, "with_hybrid", 20, "./HDR/Standard/line_graph.png")
plot_histograms(df_new, "no_hybrid", "layer", "./HDR/Hybrid_Separated/no_hybrid_histogram.png")
plot_lines(df_new, "no_hybrid", 20, "./HDR/Hybrid_Separated/no_hybrid_line_graph.png")
plot_histograms(df_new, "only_hybrid", "layer", "./HDR/Hybrid_Separated/only_hybrid_histogram.png")
plot_lines(df_new, "only_hybrid", 20, "./HDR/Hybrid_Separated/only_hybrid_line_graph.png")

write_stats(df_new, "./stats.csv")