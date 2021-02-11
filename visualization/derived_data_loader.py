'''
CASES - Economic Cascades and the Costs of a Business-as-Usual Approach to COVID-19
Copyright (C) 2021 California Academy of Sciences

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from derived_data import DerivedData
from os import path
import pickle
from julia_loader import JuliaLoader
import csv
import sys
import sys

# Something of a misnomer, as we read the julia model
# data inputs here.
class DerivedDataLoader:
    def __init__(self,sector_names):
        self.sector_names = sector_names
        self.data_files = self.read_input_metadata("derived_data_inputs.tsv")
        self.derived_data_dict = self.read_data()

    # entry point
    def read_data(self):
        derived_data_dict = {}
        failed_loads = []

        for id in self.data_files.keys():
            print(f"Common name: {self.data_files[id][0]} ID: {id}")
            try:
                age_fracs_filename = self.data_files[id][2]
                employment_filename = self.data_files[id][1]
                employemnt_percentage = self.data_files[id][3]

                derived = self.fetch_derived_data(employment_filename)
                if derived is not False:
                    print(f"Fetched {self.data_files[id][0]} from disk.")
                    derived_data_dict[id] = derived
                else:
                    try:
                        print("Attempting binary load for julia calculation...")
                        self.jl = JuliaLoader("US_exchanges_2018c.csv",
                                                     age_fracs_filename,
                                                     employment_filename,
                                                     employemnt_percentage,
                                                     False,True)
                    except FileNotFoundError:
                        self.jl = JuliaLoader("US_exchanges_2018c.csv",
                                                     age_fracs_filename,
                                                     employment_filename,
                                                     employemnt_percentage,
                                                     True,
                                                     True)
                    derived_data_dict[id] = self.generate_derived_data(employment_filename)
            except ValueError as e:
                print(f"Cannot load SES: {e}")
                failed_loads.append(id)

        for id in failed_loads:
            del self.data_files[id]

        return derived_data_dict


    def generate_derived_data(self,employment_filename):
        binary_dump_filename = JuliaLoader.get_filename_only(employment_filename) + "_derived.bin"

        print(f"Generating derived data for {employment_filename}",end=None,flush=True)
        derived_data = DerivedData(self.jl,employment_filename,self.sector_names)
        print(f"Derived data generated.. saving binary to {binary_dump_filename}")
        outfile = open(binary_dump_filename,'wb')
        pickle.dump(derived_data, outfile)
        outfile.close()
        print("... done.")
        return derived_data


    def fetch_derived_data(self,employment_filename):
        binary_dump_filename = JuliaLoader.get_filename_only(employment_filename) + "_derived.bin"
        pickle_load = None
        if not path.exists(binary_dump_filename):
            return False
        else:
            try:
                pickle_load = pickle.load(open(binary_dump_filename, "rb"))
            except ModuleNotFoundError:
                print("\n\nCurrent .bin files aren't compatible with the versions of the python libraries")
                print("loaded in the app. Remove the .bin files and re-run. This will take about 40 minutes.\n")
                sys.exit(1)
        return pickle_load



    # input Format, tsv (represented here with comma)
    # index (int id), human friendly name, employment file path, age_fracs_file_path
    # output: dict by ID=[human friendly name, employment file path, age_fracs_file_path]
    def read_input_metadata(self,filename):
        tsv_file = open(filename)
        read_tsv = csv.reader(tsv_file, delimiter="\t")

        data_files={}
        employment_directory = None
        age_fracs_directory = None
        for row in read_tsv:
            if row[0].startswith("#"):
                continue
            if employment_directory is None:
                employment_directory = row[0]
                age_fracs_directory = row[1]
            else:
                employment_filename = employment_directory + "/" + row[2]
                age_fracs_filename = age_fracs_directory + "/" + row[3]
                employment_percentage = float(row[4])
                data_files[int(row[0])] = [row[1],
                                           employment_filename,
                                           age_fracs_filename,
                                           employment_percentage]
        return data_files
