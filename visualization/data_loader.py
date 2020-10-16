from derived_data import DerivedData
import sys
from os import path
import pickle
from julia_loader import JuliaLoader
import csv

def read_data(data_files):
    derived_data_dict = {}
    failed_loads = []

    for id in data_files.keys():
        print(f"Common name: {data_files[id][0]} ID: {id}")
        try:
            age_fracs_filename = data_files[id][2]
            employment_filename = data_files[id][1]

            derived = fetch_derived_data(employment_filename)
            if derived is not False:
                print(f"Fetched {data_files[id][0]} from disk.")
                derived_data_dict[id] = derived
            else:
                try:
                    print("Attempting binary load for julia calculation...")
                    jl = JuliaLoader("US_exchanges_2018c.csv",
                                                 age_fracs_filename,
                                                 employment_filename,
                                                 False)
                except FileNotFoundError:
                    jl = JuliaLoader("US_exchanges_2018c.csv",
                                                 age_fracs_filename,
                                                 employment_filename,
                                                 True)
                derived_data_dict[id] = generate_derived_data(jl, employment_filename)
                derived = derived_data_dict[id]
        except ValueError as e:
            print(f"Cannot load SES: {e}")
            failed_loads.append(id)

    for id in failed_loads:
        del data_files[id]
    return derived_data_dict

def fetch_derived_data(employment_filename):
    binary_dump_filename = JuliaLoader.get_filename_only(employment_filename) + "_derived.bin"
    if not path.exists(binary_dump_filename):
        return False
    else:
        return pickle.load(open(binary_dump_filename, "rb"))


def generate_derived_data(jl,employment_filename):
    binary_dump_filename = JuliaLoader.get_filename_only(employment_filename) + "_derived.bin"

    print("Generating derived data...")
    derived_data = DerivedData (jl.cases_2,employment_filename)
    outfile = open(binary_dump_filename,'wb')
    pickle.dump(derived_data, outfile)
    outfile.close()
    return derived_data

# input Format, tsv (represented here with comma)
# index (int id), human friendly name, employment file path, age_fracs_file_path
# output: dict by ID=[human friendly name, employment file path, age_fracs_file_path]
def read_input_metadata(filename):
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
