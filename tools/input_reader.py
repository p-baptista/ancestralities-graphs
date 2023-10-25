import os
import pandas as pd
import csv

class InputReader:
    def __init__(self, file_path: str, number_pulses: int, number_ancestry: int, ancestries_string: str, sex_bias: bool):
        self.file_path = file_path
        self.number_pulses = number_pulses
        self.number_ancestry = number_ancestry
        self.ancestries_string = ancestries_string
        self.sex_bias = sex_bias
        pass

    def get_file_parameters(self):
        #identifying the delimiter, if there are rows to skip and if the first column shows the row's scenario
        with open(self.file_path, 'r') as csvfile:
            first_line = csvfile.readline()
            second_line = csvfile.readline()
            dialect = csv.Sniffer().sniff(csvfile.readline())
            delimiter = dialect.delimiter
            first_element = first_line.split(delimiter, 1)[0]
            second_element = second_line.split(delimiter, 1)[0]

            try: 
                float(first_element)
                self.skip_row=0
            except ValueError:
                self.skip_row=1
            except:
                print("ERROR READING FILE")

            if (float(second_element) == int(float(second_element))) and (float(second_element) != 0):
                self.first_column_scenario=1
            else: self.first_column_scenario=0
    
    def compile_code(self):
        os.system('g++ ./tools/input_reader.cpp -o ./tools/input_reader')
    
    def run_code(self):
        command = "./tools/input_reader {} {} {} {} {} {} {}".format(self.file_path, self.number_pulses, self.number_ancestry, self.ancestries_string, self.skip_row, self.first_column_scenario, self.sex_bias)
        os.system('{}'.format(command))

    def code_cleanup(self):
        os.remove("./tools/input_reader")
        os.remove("./tools/input_data.csv")

    def read_input(self):
        self.get_file_parameters()
        self.compile_code()
        self.run_code()
        
        if self.sex_bias: col_names=["Scenario", "Sex", "Pulse", "Ancestry", "Value"]
        else: col_names=["Scenario", "Pulse", "Ancestry", "Value"]

        df = pd.read_csv("./tools/input_data.csv", delimiter=' ', header=None, names=col_names)
        self.code_cleanup()
        return df