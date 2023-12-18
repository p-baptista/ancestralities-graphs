import os

class CodeIntegrity:
    def __init__(self):
        pass

    @classmethod
    def check_output_folders(self, output_path):
        #creating directory for outputs
        if not os.path.exists("./Outputs"):
            os.mkdir("./Outputs")

        if not os.path.exists(output_path):
            os.mkdir(output_path)
    
    @classmethod
    def check_tools_folder(self):
        file_names = ["math_tools.py", "plot_tools.py", "code_integrity.py", "input_reader.py", "input_reader.cpp"]
        
        for file in file_names:
            if not os.path.exists(f"./tools/{file}"):
                raise FileNotFoundError(f"There seems to be a file missing [{file}]. Please verify the integrity of the program folders or download the repository again.")