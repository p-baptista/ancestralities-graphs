import os

class CodeIntegrity:
    def __init__(self):
        pass

    @classmethod
    def check_output_folders(self):
        #creating directory for outputs
        if not os.path.exists("./Outputs"):
            os.mkdir("./Outputs")
        #creating directory for graphs
        if not os.path.exists("./Outputs/Graphs"):
            os.mkdir("./Outputs/Graphs")
        #creating directory for graphs
        if not os.path.exists("./Outputs/Statistics"):
            os.mkdir("./Outputs/Statistics")
    
    @classmethod
    def check_tools_folder(self):
        file_names = ["math_tools.py", "plot_tools.py", "code_integrity.py", "input_reader.py", "input_reader.cpp"]
        
        for file in file_names:
            if not os.path.exists(f"./tools/{file}"):
                raise FileNotFoundError(f"There seems to be a file missing [{file}]. Please verify the integrity of the program folders or download the repository again.")