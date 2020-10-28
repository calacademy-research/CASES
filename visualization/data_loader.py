from derived_data import DerivedData
import sys
from os import path
import pickle
from julia_loader import JuliaLoader
import csv

class DataLoader:
    def __init__(self):
        self.data_files = self.read_input_metadata("inputs.tsv")
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
                                                     False,True)
                    except FileNotFoundError:
                        self.jl = JuliaLoader("US_exchanges_2018c.csv",
                                                     age_fracs_filename,
                                                     employment_filename,
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
        derived_data = DerivedData(self.jl.cases_surfaces,employment_filename)
        outfile = open(binary_dump_filename,'wb')
        pickle.dump(derived_data, outfile)
        outfile.close()
        print("... done.")
        return derived_data


    def fetch_derived_data(self,employment_filename):
        binary_dump_filename = JuliaLoader.get_filename_only(employment_filename) + "_derived.bin"
        if not path.exists(binary_dump_filename):
            return False
        else:
            return pickle.load(open(binary_dump_filename, "rb"))




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
                data_files[int(row[0])] = [row[1],employment_filename,age_fracs_filename]
        return data_files
