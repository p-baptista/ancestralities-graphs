#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <math.h>

int main(int argc, char* argv[]) {
    //argument format: [input file path], [number of ancestries], [number of pulses], [ancestry list (separated by comma)], [skip first row], [first column scenario]
    //e.g.: ./data_outputs/output_salvador.txt 5 4 EUR,AFR,NAT,HYB, 0, 0

    std::fstream input_file;
    input_file.open(argv[1], std::ios::in);

    std::fstream output_file;
    output_file.open("./tools/input_data.csv", std::ios::out);

    std::string n_pulses_string = argv[2];
    int n_pulses = std::stoi(n_pulses_string);

    std::string n_ancestries_string = argv[3];
    int n_ancestries = std::stoi(n_ancestries_string);

    std::string ancestries_string = argv[4];
    std::stringstream ancestries_sstream(ancestries_string);
    std::vector<std::string> ancestries;

    bool skip_first_row = bool(std::stoi(argv[5]));

    bool first_col_scenario = bool(std::stoi(argv[6]));

    bool sex_bias = bool(std::stoi(argv[7]));

    while(!ancestries_sstream.eof()) {
        std::string temp_anc;
        getline(ancestries_sstream, temp_anc, ',');
        ancestries.push_back(temp_anc);
    }

    std::vector<std::string> sexes;
    sexes.push_back("Female");
    sexes.push_back("Male");

    std::string input_line;

    if(skip_first_row) {
        getline(input_file, input_line);
        input_line.clear();
    }
    
    if(first_col_scenario) {
        if(sex_bias) {
            while (input_file >> input_line) {
                int scenario = std::stoi(input_line);

                for (int anc_it = 0; anc_it < n_pulses * n_ancestries * 2; anc_it++) {
                    input_file >> input_line;
                    std::string anc_temp = ancestries[anc_it%ancestries.size()];
                    int sex_int = floor(anc_it / (n_pulses * n_ancestries));
                    std::string sex = sexes[sex_int%2];
                    int pulse = int(floor(anc_it/n_ancestries))%n_pulses + 1;
                    output_file << scenario << " " << sex << " " << pulse << " " << anc_temp << " " << input_line << std::endl;
                }
            }
        }
        else {
            while (input_file >> input_line) {
                int scenario = std::stoi(input_line);

                for (int anc_it = 0; anc_it < n_pulses * n_ancestries * 2; anc_it++) {
                    input_file >> input_line;
                    std::string anc_temp = ancestries[anc_it%ancestries.size()];
                    int pulse = int(floor(anc_it/n_ancestries))%n_pulses + 1;
                    output_file << scenario << " " << pulse << " " << anc_temp << " " << input_line << std::endl;
                }
            }
        }
        
    }
    else {
        if (sex_bias) {
            int anc_it=0;

            while (input_file >> input_line) {
                std::string anc_temp;
                anc_temp = ancestries[anc_it%ancestries.size()];
                int scenario = floor(anc_it / (n_pulses * n_ancestries * 2))+1;
                int sex_int = floor(anc_it / (n_pulses * n_ancestries));
                std::string sex = sexes[sex_int%2];
                int pulse = int(floor(anc_it/n_ancestries))%n_pulses + 1;
                output_file << scenario << " " << sex << " " << pulse << " " << anc_temp << " " << input_line << std::endl;

                anc_it++;
            }
        }
        else {
            int anc_it=0;

            while (input_file >> input_line) {
                std::string anc_temp;
                anc_temp = ancestries[anc_it%ancestries.size()];
                int scenario = floor(anc_it / (n_pulses * n_ancestries * 2))+1;
                int pulse = int(floor(anc_it/n_ancestries))%n_pulses + 1;
                output_file << scenario << " " << pulse << " " << anc_temp << " " << input_line << std::endl;

                anc_it++;
            }
        }
    }

    

    input_file.close();
    output_file.close();

    return 0;
}