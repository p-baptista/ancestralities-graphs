import numpy as np
import csv

class MathTools:
    def __init__(self, sexual_bias: bool, n_pulses: int, ancestries):
        self.sexual_bias = sexual_bias
        self.n_pulses = n_pulses
        self.ancestries = ancestries
        
    #filters data by the Highest Density Region, informed by the percentage
    #90% region -> percentage = 90
    def filter(self, percentage, df_unfiltered):
        if self.sexual_bias:
            sexes = ("Female", "Male")
            scenarios = set(())
            df_filtered = df_unfiltered
            for sex in range(0,2):
                for pulse in range(1, (self.n_pulses+1)):
                    for anc in range(0, len(self.ancestries)):
                        #selecting only the values from this pulse, sex and ancestry
                        df_temp = df_filtered[(df_filtered["Pulse"] == pulse) & (df_filtered["Sex"] == sexes[sex]) & (df_filtered["Ancestry"] == self.ancestries[anc])]
                        
                        #calculating the percentile values
                        lower_quantile = np.percentile(df_temp["Value"], ((100-percentage)/2), method="closest_observation")
                        upper_quantile = np.percentile(df_temp["Value"], (100-((100-percentage)/2)), method="closest_observation")

                        size = df_temp.shape[0]
                        #avoiding the null stats (HYB percentages in the first pulse)
                        if lower_quantile != 0:
                            #searches for the scenarios that are outside the HDR
                            for i in range(size):
                                #if the value is outside the quantiles, we add to the set of scenarios which will be filtered out
                                if ((df_temp.iloc[i].iloc[-1] < lower_quantile) or (df_temp.iloc[i].iloc[-1] > upper_quantile)):
                                    scenarios.add(df_temp.iloc[i].iloc[0])
            #applies the HDR filter
            df_filtered = df_filtered[~df_filtered["Scenario"].isin(scenarios)]
            return df_filtered
        
        else:
            scenarios = set(())
            df_filtered = df_unfiltered
            for pulse in range(1,(self.n_pulses+1)):
                for anc in range(0, len(self.ancestries)):
                    #selecting only the values from this pulse and ancestry
                    df_temp = df_filtered[(df_filtered["Pulse"] == pulse) & (df_filtered["Ancestry"] == self.ancestries[anc])]
                    
                    #calculating the percentile values
                    lower_quantile = np.percentile(df_temp["Value"], ((100-percentage)/2), method="closest_observation")
                    upper_quantile = np.percentile(df_temp["Value"], (100-((100-percentage)/2)), method="closest_observation")

                    size = df_temp.shape[0]
                    #avoiding the null stats (HYB percentages in the first pulse)
                    if lower_quantile != 0:
                        #searches for the scenarios that are outside the HDR
                        for i in range(size):
                            #if the value is outside the quantiles, we add to the set of scenarios which will be filtered out
                            if ((df_temp.iloc[i].iloc[-1] < lower_quantile) or (df_temp.iloc[i].iloc[-1] > upper_quantile)):
                                scenarios.add(df_temp.iloc[i].iloc[0])
            #applies the HDR filter
            df_filtered = df_filtered[~df_filtered["Scenario"].isin(scenarios)]
            return df_filtered

    # Function to find mode from the continuous data
    def find_mode(self, df):
        if df.empty:
            return 0
        #calculating number of bins using Freedman-Diaconis rule
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

        return round(mode, 3)

    #writes data's statistics in a csv file
    def write_stats(self, df, file_name):
        if self.sexual_bias:
            sexes = ("Female", "Male")
            header = ["Sex", "Pulse", "Ancestry", "Min", "Mean", "Median", "Max", "Mode", "Std"]
            with open(file_name, 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter='\t')
                writer.writerow(header)
                for i in range (0, 2):
                    for j in range (1, self.n_pulses+1):
                            for k in range (0, len(self.ancestries)):
                                df_temp = df.loc[(df["Pulse"] == j) & (df["Sex"] == sexes[i])]
                                anc = df_temp.loc[(df_temp["Ancestry"] == self.ancestries[k])]

                                row = [sexes[i], j, self.ancestries[k], anc["Value"].min(), anc["Value"].mean(), anc["Value"].median(), anc["Value"].max(), self.find_mode(anc), anc["Value"].std()]
                                writer.writerow(row)
        else:
            header = ["Pulse", "Ancestry", "Min", "Mean", "Median", "Max", "Mode", "Std"]
            with open(file_name, 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter='\t')
                writer.writerow(header)
                for j in range (1, self.n_pulses+1):
                        for k in range (0, len(self.ancestries)):
                            df_temp = df.loc[(df["Pulse"] == j)]
                            anc = df_temp.loc[(df_temp["Ancestry"] == self.ancestries[k])]

                            row = [j, self.ancestries[k], anc["Value"].min(), anc["Value"].mean(), anc["Value"].median(), anc["Value"].max(), self.find_mode(anc), anc["Value"].std()]
                            writer.writerow(row)