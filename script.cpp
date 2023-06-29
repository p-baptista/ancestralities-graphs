#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <math.h>

int main(int argc, char* argv[]) {

    std::fstream input_file;
    input_file.open(argv[1], std::ios::in);

    std::fstream output_file;
    output_file.open("./input_data.csv", std::ios::out | std::ios::app);

    char delimiter = argv[2][0];

    std::string n_ancestries_string = argv[3];
    int n_ancestries = std::stoi(n_ancestries_string);

    std::string n_pulses_string = argv[4];
    int n_pulses = std::stoi(n_pulses_string);

    std::string ancestries_string = argv[5];
    std::stringstream ancestries_sstream(ancestries_string);
    std::vector<std::string> ancestries;

    while(!ancestries_sstream.eof()) {
        std::string temp_anc;
        getline(ancestries_sstream, temp_anc, ',');
        ancestries.push_back(temp_anc);
    }

    std::vector<std::string> sexes;
    sexes.push_back("Female");
    sexes.push_back("Male");

    std::string input_line;
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

    input_file.close();
    output_file.close();

    return 0;
}