import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import math
import scipy.stats as st
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

    if (first_column_scenario):
        #populating new dataframe
        for i in range (df_raw.shape[0]):
            for j in range (1, df_raw.shape[1]):
                #assigning gender to new row
                if j < (df_raw.shape[1])/2: sex = "Female"
                else: sex = "Male"

                #assigning scenario
                scenario = int(df_raw.iloc[i][0])
                
                #assigning pulse
                pulse = int(((np.floor((j-1)/NUMBER_ANCESTRY))%5)+1)

                #assigning ancestry
                ancestries = ("EUR", "AFR", "NAT", "HYB")
                ancestry = ancestries[((j-1)%4)]

                #assigning value of ancestry
                value = float(df_raw.iloc[i][j])

                new_entry = (scenario, sex, pulse, ancestry, value)
                entries[n_entries] = new_entry
                n_entries += 1
    else:
        #populating new dataframe
        for i in range (df_raw.shape[0]):
            for j in range (0, df_raw.shape[1]):
                #assigning gender to new row
                sex = "Male"

                #assigning scenario
                scenario = i+1
                
                #assigning pulse
                pulse = int(((np.floor(j/NUMBER_ANCESTRY))%5)+1)

                #assigning ancestry
                ancestries = ("EUR", "AFR", "NAT", "HYB")
                ancestry = ancestries[((j)%4)]

                #assigning value of ancestry
                value = float(df_raw.iloc[i][j])

                new_entry = (scenario, sex, pulse, ancestry, value)
                entries[n_entries] = new_entry
                n_entries += 1

    
    df_new = pd.DataFrame(data = entries, columns=["Scenario", "Sex", "Pulse", "Ancestry", "Value"])
    return df_new

#plots graphs for each pulse, separated by sex
def plot_histograms(df, ancestries, type, percentage, savefile):
    sexes = ("Female", "Male")
    colours = list()

    for anc in ancestries:
        if anc == "EUR": colours.append("red")
        elif anc == "AFR": colours.append("deepskyblue")
        elif anc == "NAT": colours.append("green")
        elif anc == "HYB": colours.append("darkviolet")

    df_hist = df[(df["Ancestry"].isin(ancestries)) & (df["Value"] != 0)]

    graph = sns.FacetGrid(df_hist, col="Pulse", row="Sex", hue="Ancestry", palette=colours)
    graph = (graph.map_dataframe(sns.histplot, x="Value", multiple=type, stat='probability').add_legend())
    
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
                    axes[j].axvline(x=lower_quantile, color=colours[anc], linestyle='--', linewidth=0.8, label='05%')
                    axes[j].axvline(x=upper_quantile, color=colours[anc], linestyle='--', linewidth=0.8, label='90%')
    plt.xlim([0, 1])
    graph.savefig(savefile)

def plot_lines(df, ancestries, percentage, savefile):
    sexes = ("Female", "Male")
    colours = list()

    for anc in ancestries:
        if anc == "EUR": colours.append("red")
        elif anc == "AFR": colours.append("deepskyblue")
        elif anc == "NAT": colours.append("green")
        elif anc == "HYB": colours.append("darkviolet")

    df_hist = df[(df["Ancestry"].isin(ancestries)) & (df["Value"] != 0)]

    graph = sns.FacetGrid(df_hist, col="Pulse", row="Sex", hue="Ancestry", palette=colours)
    graph = (graph.map_dataframe(sns.histplot, x="Value", fill=False, linewidth=0, kde=True, stat='probability').add_legend())

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
                    axes[j].axvline(x=lower_quantile, color=colours[anc], linestyle='--', linewidth=0.8)
                    axes[j].axvline(x=upper_quantile, color=colours[anc], linestyle='--', linewidth=0.8)
                    # axes[j].text(lower_quantile-0.1, (axes[j].get_ylim()[1]-0.01), "5%")
                    # axes[j].text(upper_quantile+0.1, (axes[j].get_ylim()[1]-0.01), "90%")

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

def filter_ci(percentage, df_unfiltered):
    ancestries = ("EUR", "AFR", "NAT", "HYB")
    sexes = ("Female", "Male")
    scenarios = set(())
    df_filtered = df_unfiltered

    for sex in range(0,2):
        for pulse in range(1,6):
            for anc in range(0,4):
                #selecting only the values from this pulse, sex and ancestry
                df_temp = df_filtered[(df_filtered["Pulse"] == pulse) & (df_filtered["Sex"] == sexes[sex]) & (df_filtered["Ancestry"] == ancestries[anc])]

                mean_temp = df_temp["Value"].mean()
                std_temp = df_temp["Value"].std(ddof=0)
                sqrt_size_temp = np.sqrt(len(df_temp))

                print(f'Pulse', pulse, sexes[sex], ancestries[anc])

                print(f'mean, std and sqrt_size:', mean_temp, std_temp, sqrt_size_temp)

                #calculating confidence interval bounds
                ci_inf = mean_temp - 1.64*(std_temp/sqrt_size_temp)
                ci_sup = mean_temp + 1.64*(std_temp/sqrt_size_temp)

                print(ci_inf, ci_sup)

                size = df_temp.shape[0]
                #avoiding the null stats (HYB percentages in the first pulse)
                if ci_inf != 0:
                    #searches for the scenarios that are outside the 90% HDR
                    for i in range(size):
                        #if the value is outside the quantiles, we add to the set of scenarios which will be filtered out
                        if ((df_temp.iloc[i][4] < ci_inf) or (df_temp.iloc[i][4] > ci_sup)):
                            scenarios.add(df_temp.iloc[i][0])

    #applies the HDR filter
    df_filtered = df_filtered[~df_filtered["Scenario"].isin(scenarios)]
    # print(df_filtered.head(10))
    return df_filtered

# Function to find mode from the continuous data
def find_mode(df):
    return 0
    if df.empty:
        return 0
    
    x,y = sns.histplot(df, x="Value", fill=False, edgecolor="k", linewidth=0, kde=True).get_lines()[0].get_data()
    # print(np.shape(x), np.shape(y))
    
    max_prob = 0
    mode = 0
    it = 0
    for prob in y:
        it+=1
        print(prob)
        if prob > max_prob:
            max_prob = prob
    
    

    print(f'Max probability is:', max_prob)

    # for ind in df.index:
    #     value = df["Value"][ind]
    #     prob = scipy.stats.norm(value)
    #     if prob > max_prob:
    #         max_prob = prob
    #         mode = value
    
    return mode

def write_stats(df, file_name):
    ancestries = ("EUR", "AFR", "NAT", "HYB")
    sexes = ("Female", "Male")

    header = ["Sex", "Pulse", "Ancestry", "Min", "Mean", "Median", "Mode", "Max", "Std"]

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(header)

        for i in range (0, 2):
            for j in range (1, 6):
                    for k in range (0, 4):
                        df_temp = df.loc[(df["Pulse"] == j) & (df["Sex"] == sexes[i])]
                        anc = df_temp.loc[(df_temp["Ancestry"] == ancestries[k])]
                        # print(f'Pulse', j, sexes[i], ancestries[k])

                        row = [sexes[i], j, ancestries[k], anc["Value"].min(), anc["Value"].mean(), anc["Value"].median(), find_mode(anc), anc["Value"].max(), anc["Value"].std()]
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
# df = pd.read_csv('./data_outputs/output_salvador.txt', delimiter=' ', header=None)
df = pd.read_csv('./data_outputs/output-after-filter-genomic-ancestry_salvador.txt', delimiter='\t', header=None, skiprows=1)

#treating the raw data and creating the new dataframe
df_new = populate_dataframe(df, True)
del df

create_directories()

ancestries = ["EUR", "AFR", "NAT", "HYB"]

plot_histograms(df_new, ancestries, "layer", 90, "./NO_HDR/Standard/histogram.png")
plot_lines(df_new, ancestries, 90, "./NO_HDR/Standard/line_graph.png")

ancestries = ["EUR", "AFR", "NAT"]
plot_histograms(df_new, ancestries, "layer", 90, "./NO_HDR/Hybrid_Separated/no_hybrid_histogram.png")
plot_lines(df_new, ancestries, 90, "./NO_HDR/Hybrid_Separated/no_hybrid_line_graph.png")

ancestries = ["HYB",]
plot_histograms(df_new, ancestries, "layer", 90, "./NO_HDR/Hybrid_Separated/only_hybrid_histogram.png")
plot_lines(df_new, ancestries, 90, "./NO_HDR/Hybrid_Separated/only_hybrid_line_graph.png")

write_stats(df_new, "./stats_NO_HDR.csv")

#filtering for only 90% of density
# df_new = filter(90, df_new)

# plot_histograms(df_new, "with_hybrid", "layer", "./HDR/Standard/histogram.png")
# plot_lines(df_new, "with_hybrid", "./HDR/Standard/line_graph.png")
# plot_histograms(df_new, "no_hybrid", "layer", "./HDR/Hybrid_Separated/no_hybrid_histogram.png")
# plot_lines(df_new, "no_hybrid", "./HDR/Hybrid_Separated/no_hybrid_line_graph.png")
# plot_histograms(df_new, "only_hybrid", "layer", "./HDR/Hybrid_Separated/only_hybrid_histogram.png")
# plot_lines(df_new, "only_hybrid", "./HDR/Hybrid_Separated/only_hybrid_line_graph.png")

# write_stats(df_new, "./stats_HDR.csv")