import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import seaborn as sns
import pandas as pd

from tools.math_tools import MathTools

class PlotTools:
    def __init__(self, sexual_bias: bool, n_pulses: int, ancestry_names, ancestry_colours):
        self.sexual_bias = sexual_bias
        self.n_pulses = n_pulses
        self.ancestry_names = ancestry_names
        self.ancestry_colours = ancestry_colours
        self.math_tools = MathTools(sexual_bias, n_pulses, ancestry_names)

    def plot_HPD_lines(self, df, axis, percentage, color):
        lower_quantile = np.percentile(df["Value"], ((100-percentage)/2), method="closest_observation")
        upper_quantile = np.percentile(df["Value"], (100-((100-percentage)/2)), method="closest_observation")

        #quantile bounds lines
        axis.axvline(x=lower_quantile, color=color, linestyle='--', linewidth=0.8)
        axis.axvline(x=upper_quantile, color=color, linestyle='--', linewidth=0.8)
        
        #mode line
        axis.axvline(x=self.math_tools.find_mode(df), color="black", linestyle=':', linewidth=1.2)
        
    #plots histograms for each pulse, separated by sex
    #ancestries param should be a list with the ancestries' names, eg. ancestries = ["EUR", "AFR", "NAT", "HYB"]
    def plot_histograms(self, df, selected_ancestries, type, savefile):
        colours = list()

        for anc1 in range(0, len(selected_ancestries)):
            for anc2 in range(0, len(self.ancestry_names)):
                if selected_ancestries[anc1] == self.ancestry_names[anc2]:
                    colours.append(self.ancestry_colours[anc2])
                    break

        df_hist = df[(df["Ancestry"].isin(selected_ancestries)) & (df["Value"] != 0)]

        if self.sexual_bias: graph = sns.FacetGrid(df_hist, col="Sex", row="Pulse", hue="Ancestry", palette=colours)
        else: graph = sns.FacetGrid(df_hist, col="Pulse", hue="Ancestry", palette=colours)

        graph = (graph.map_dataframe(sns.histplot, x="Value", multiple=type, stat='probability').add_legend())
        plt.xlim([-0.2, 1])
        graph.savefig(savefile)

    def plot_lines(self, df, selected_ancestries, savefile):
        colours = list()

        for anc1 in range(0, len(selected_ancestries)):
            for anc2 in range(0, len(self.ancestry_names)):
                if selected_ancestries[anc1] == self.ancestry_names[anc2]:
                    colours.append(self.ancestry_colours[anc2])
                    break

        df_hist = df[(df["Ancestry"].isin(selected_ancestries)) & (df["Value"] != 0)]

        if self.sexual_bias: graph = sns.FacetGrid(df_hist, col="Pulse", hue="Ancestry", palette=colours)
        else: graph = sns.FacetGrid(df_hist, col= "Pulse", hue="Ancestry", palette=colours)

        graph = (graph.map_dataframe(sns.histplot, x="Value", fill=False, linewidth=0, kde=True, stat='probability'))

        plt.xlim([-0.2, 1])
        
        #drawing the legend for each ancestry
        legend = list()
        for anc in range (0, len(selected_ancestries)):
            legend.append(mlines.Line2D([], [], color=colours[anc], marker='s', ls='', label=selected_ancestries[anc]))
        graph.figure.legend(handles=legend, loc=7, title="Ancestry", frameon=False)
        graph.figure.tight_layout()
        graph.figure.subplots_adjust(right=0.9)
        
        graph.savefig(savefile)

    def plot_points_by_ancestry(self, df, selected_ancestries, savefile):
        colours = list()

        for anc1 in range(0, len(selected_ancestries)):
            for anc2 in range(0, len(self.ancestry_names)):
                if selected_ancestries[anc1] == self.ancestry_names[anc2]:
                    colours.append(self.ancestry_colours[anc2])
                    break

        figure, axis = plt.subplots(1, len(self.ancestry_names))
        figure.set_figwidth(8 + 4*len(selected_ancestries))
        figure.set_figheight(4)
        
        #setting ticks and their lables
        ticks = list()
        labels = list()
        
        for pulse in range(1,(self.n_pulses+1)):
            ticks.append((1/(self.n_pulses+1))*(pulse))
            labels.append("Pulse {}".format(pulse))

        df_plot = df
        for anc in range(0,len(selected_ancestries)):
            for pulse in range(1,(self.n_pulses+1)):
                if self.sexual_bias:
                    sexes = ("Female", "Male")
                    for sex in range(0,2):
                        #selecting only the values from this pulse, sex and ancestry
                        df_temp = df_plot[(df_plot["Pulse"] == pulse) & (df_plot["Sex"] == sexes[sex]) & (df_plot["Ancestry"] == selected_ancestries[anc])]
                        
                        #calculating values
                        min_temp = df_temp["Value"].min()
                        max_temp = df_temp["Value"].max()
                        mean_temp = df_temp["Value"].mean()

                        #darkening the colour if gender is male
                        colour = [0.0, 0.0, 0.0, 1.0]
                        for i in range(0, len(colour)-1):
                            colour[i] = max(0, (colours[anc][i] - 0.25*sex))

                        #plotting point
                        buffer = 0.25 - 0.04 * self.n_pulses
                        point_x = (-buffer/2 + ((1/(self.n_pulses+1))*(pulse))) + buffer*sex
                        axis[anc].plot(point_x, mean_temp, marker='o', markersize=6, color=colour)

                        #plotting min and max lines
                        lines_x = [point_x - (0.015 * 4/(len(selected_ancestries))), point_x + (0.015 * 4/(len(selected_ancestries)))]
                        axis[anc].plot(lines_x, [min_temp, min_temp], linewidth=1.2, color=colour, alpha=1)
                        axis[anc].plot(lines_x, [max_temp, max_temp], linewidth=1.2, color=colour, alpha=1)
                        
                        #connecting line
                        axis[anc].plot([point_x, point_x], [min_temp, max_temp], linewidth=1, linestyle='--', color=colour, alpha=0.9)
                else:
                    #selecting only the values from this pulse and ancestry
                    df_temp = df_plot[(df_plot["Pulse"] == pulse) & (df_plot["Ancestry"] == selected_ancestries[anc])]
                    
                    #calculating values
                    min_temp = df_temp["Value"].min()
                    max_temp = df_temp["Value"].max()
                    mean_temp = df_temp["Value"].mean()

                    #plotting point
                    point_x = ((1/(self.n_pulses+1))*(pulse))
                    axis[anc].plot(point_x, mean_temp, marker='o', markersize=6, color=colours[anc])

                    #plotting min and max lines
                    lines_x = [point_x - (0.015 * 4/(len(selected_ancestries))), point_x + (0.015 * 4/(len(selected_ancestries)))]
                    axis[anc].plot(lines_x, [min_temp, min_temp], linewidth=1.2, color=colours[anc], alpha=1)
                    axis[anc].plot(lines_x, [max_temp, max_temp], linewidth=1.2, color=colours[anc], alpha=1)
                    
                    #connecting line
                    axis[anc].plot([point_x, point_x], [min_temp, max_temp], linewidth=1, linestyle='--', color=colours[anc], alpha=0.9)

            #setting axis limits, ticks and title
            axis[anc].set_xlim(-0.2, 1)
            axis[anc].set_ylim(0, 1)
            axis[anc].set_xticks(ticks, labels)
            axis[anc].set_title(selected_ancestries[anc])

        figure.tight_layout(pad=2)
        axis[0].set_ylabel("Ancestry Percentage")
        figure.savefig(savefile)


    def plot_points_with_errorbars(self, df, selected_ancestries, savefile):
        colours = list()

        for anc1 in range(0, len(selected_ancestries)):
            for anc2 in range(0, len(self.ancestry_names)):
                if selected_ancestries[anc1] == self.ancestry_names[anc2]:
                    colours.append(self.ancestry_colours[anc2])
                    break

        figure, axis = plt.subplots(1, self.n_pulses)
        figure.set_figwidth(8 + 4*len(selected_ancestries))
        figure.set_figheight(4)
        
        #setting ticks and their lables
        ticks = list()
        labels = list()
        
        for anc in range(0,len(selected_ancestries)):
            ticks.append((1/(len(selected_ancestries)+2))*(anc+1))
            labels.append(selected_ancestries[anc])

        df_plot = df
        for pulse in range(1,(self.n_pulses+1)):
            for anc in range(0,len(selected_ancestries)):
                if self.sexual_bias:
                    sexes = ("Female", "Male")
                    for sex in range(0,2):
                        #selecting only the values from this pulse, sex and ancestry
                        df_temp = df_plot[(df_plot["Pulse"] == pulse) & (df_plot["Sex"] == sexes[sex]) & (df_plot["Ancestry"] == selected_ancestries[anc])]
                        
                        #calculating values
                        min_temp = df_temp["Value"].min()
                        max_temp = df_temp["Value"].max()
                        mean_temp = df_temp["Value"].mean()

                        #darkening the colour if gender is male
                        colour = [0.0, 0.0, 0.0, 1.0]
                        for i in range(0, len(colour)-1):
                            colour[i] = max(0, (colours[anc][i] - 0.25*sex))

                        #plotting point
                        buffer = 0.25 - 0.05 * len(selected_ancestries)
                        point_x = (-buffer/2 + ((1/(len(selected_ancestries)+1))*(anc+1))) + buffer*sex
                        axis[pulse-1].plot(point_x, mean_temp, marker='o', markersize=6, color=colour)

                        #plotting min and max lines
                        lines_x = [point_x - (0.015 * 4/(len(selected_ancestries))), point_x + (0.015 * 4/(len(selected_ancestries)))]
                        axis[pulse-1].plot(lines_x, [min_temp, min_temp], linewidth=1.2, color=colour, alpha=1)
                        axis[pulse-1].plot(lines_x, [max_temp, max_temp], linewidth=1.2, color=colour, alpha=1)
                        
                        #connecting line
                        axis[pulse-1].plot([point_x, point_x], [min_temp, max_temp], linewidth=1, linestyle='--', color=colour, alpha=0.9)
                else:
                    #selecting only the values from this pulse and ancestry
                    df_temp = df_plot[(df_plot["Pulse"] == pulse) & (df_plot["Ancestry"] == selected_ancestries[anc])]
                    
                    #calculating values
                    min_temp = df_temp["Value"].min()
                    max_temp = df_temp["Value"].max()
                    mean_temp = df_temp["Value"].mean()

                    #plotting point
                    point_x = ((1/(len(selected_ancestries)+2))*(anc+1))
                    axis[pulse-1].plot(point_x, mean_temp, marker='o', markersize=6, color=colours[anc])

                    #plotting min and max lines
                    lines_x = [point_x - (0.015 * 4/(len(selected_ancestries))), point_x + (0.015 * 4/(len(selected_ancestries)))]
                    axis[pulse-1].plot(lines_x, [min_temp, min_temp], linewidth=1.2, color=colours[anc], alpha=1)
                    axis[pulse-1].plot(lines_x, [max_temp, max_temp], linewidth=1.2, color=colours[anc], alpha=1)
                    
                    #connecting line
                    axis[pulse-1].plot([point_x, point_x], [min_temp, max_temp], linewidth=1, linestyle='--', color=colours[anc], alpha=0.9)

            #setting axis limits, ticks and title
            axis[pulse-1].set_xlim(-0.2, 1)
            axis[pulse-1].set_ylim(0, 1)
            axis[pulse-1].set_xticks(ticks, labels)
            axis[pulse-1].set_title("Pulse {}".format(pulse))

        #drawing the legend for each ancestry
        legend = list()
        for anc in range (0, len(selected_ancestries)):
            legend.append(mlines.Line2D([], [], color=colours[anc], marker='o', ls='', label=selected_ancestries[anc]))
        figure.legend(handles=legend, loc=7, title="Ancestry", frameon=False)
        figure.tight_layout(pad=2)
        figure.subplots_adjust(right=0.925)
        axis[0].set_ylabel("Ancestry Percentage")
        
        figure.savefig(savefile)

    def priori_posteriori(self, df_priori, df_posteriori, selected_ancestries, savefile):
        colours = list()

        for anc1 in range(0, len(selected_ancestries)):
            for anc2 in range(0, len(self.ancestry_names)):
                if selected_ancestries[anc1] == self.ancestry_names[anc2]:
                    colours.append(self.ancestry_colours[anc2])
                    break
        
        df_priori_filtered = df_priori[(df_priori["Ancestry"].isin(selected_ancestries)) & (df_priori["Value"] != 0)]
        df_posteriori_filtered = df_posteriori[(df_posteriori["Ancestry"].isin(selected_ancestries)) & (df_posteriori["Value"] != 0)]

        figure, axis = plt.subplots(self.n_pulses, len(selected_ancestries))

        figure.set_figheight(8)
        figure.set_figwidth(9)
        for anc in range(0, len(selected_ancestries)):
            for pulse in range(0, self.n_pulses):
                axis[pulse][anc].set_title(f"{selected_ancestries[anc]} Pulse {pulse+1}")
                df_priori_temp = df_priori_filtered[(df_priori_filtered["Pulse"] == pulse+1) & (df_priori_filtered["Ancestry"] == selected_ancestries[anc])]
                df_posteriori_temp = df_posteriori_filtered[(df_posteriori_filtered["Pulse"] == pulse+1) & (df_posteriori_filtered["Ancestry"] == selected_ancestries[anc])]
                sns.kdeplot(x="Value", data=df_priori_temp, ax=axis[pulse][anc], color=colours[anc], linestyle="--")
                sns.kdeplot(x="Value", data=df_posteriori_temp, ax=axis[pulse][anc], color=colours[anc], linestyle="-")

                axis[pulse][anc].set_xlim(-0.2, 1)

        legend = list()
        legend.append(mlines.Line2D([], [], color="black", ls='--', label="Priori"))
        legend.append(mlines.Line2D([], [], color="black", ls='-', label="Posteriori"))
        figure.legend(handles=legend, loc=7, frameon=False)

        figure.tight_layout(pad=1)
        figure.subplots_adjust(right=0.85)
        figure.savefig(savefile)