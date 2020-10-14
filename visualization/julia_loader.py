import pandas as pd
import numpy as np
import pickle
import ntpath
import os
import sys
from julia import Main as j

class JuliaLoader:

    def __init__(self,
                 us_exchanges,
                 age_fracs,
                 employment,
                 run_julia=True,
                 load_all_data=False):
        # the first dataframe contains metadata not currently in use.
        # default to do not load.
        print(f"Processing {us_exchanges}, employment:{employment}, age_fracs:{age_fracs}")
        self.us_exchanges_filename = us_exchanges
        self.age_fracs_filename = age_fracs
        self.employment_filename = employment

        self.results = []
        if run_julia:
            self.run_julia()
        else:
            if load_all_data:
                pass
                # not currently used
                # self.cases_1 = pickle.load(open(self.employment_filename+"_cases_1.bin", "rb"))
            else:
                self.cases_1 = None
            binary_dump_filename = self.get_filename_only(self.employment_filename) + "_cases_2.bin"
            self.cases_2 = pickle.load(open(binary_dump_filename, "rb"))

    def run_julia(self):
        print("Loading Julia....")


        # US_EXCHANGES = "US_exchanges_2018c.csv"
        # AGE_FRACS = "LA_age_fracs.csv"
        # LA_EMPLOYMENT = "LA_employment_by_sector_02_2020.csv"
        I = np.genfromtxt(self.us_exchanges_filename, delimiter=" ")
        age_fracs_orig = np.genfromtxt(self.age_fracs_filename, delimiter=",")
        # first column is
        age_fracs = np.delete(age_fracs_orig,0,1)

        employed = pd.read_csv(self.employment_filename,
                               dtype={"Sector": str, "Feb": np.int64})

        # if np.isnan(I).any() or np.isnan(age_fracs).any() or np.isnan(employed).any():
        if np.isnan(I).any():
            raise ValueError(f"NAN found in US_EXCHANGES file {self.us_exchanges_filename}; skipping")

        if np.isnan(age_fracs).any():
            raise ValueError(f"NAN found in age_fracs file {self.age_fracs_filename}; skipping")


        j.eval("using DataFrames")
        julia_formatted_employed = j.DataFrame(employed.to_dict(orient='list'))

        if employed.isnull().values.any():
            raise ValueError(f"NAN found in employment data {self.employment_filename}; skipping")


        print("Starting Julia run...")
        j.include("CASES.jl")
        returned_result = j.main(I, age_fracs, julia_formatted_employed)
        print("Julia run complete.")

        self.cases_2 = returned_result[1]

        binary_dump_filename = self.get_filename_only(self.employment_filename)+"_cases_2.bin"
        print("Writing binary dump: " + binary_dump_filename)
        outfile = open(binary_dump_filename,'wb')
        pickle.dump(self.cases_2, outfile)
        outfile.close()

        self.cases_1 = returned_result[0]
        # Not currently using this metadata
        # pickle.dump(self.cases_1, open(self.employment_filename+"_cases_1.bin", "wb"))

    @staticmethod
    def get_filename_only(full_filename):
        no_path_filename = ntpath.basename(full_filename)
        return os.path.splitext(no_path_filename)[0]

    def save_csv(self,filename,results):
        with open(filename, "w") as out:
            for cur_line in results:
                for cur_item in cur_line:
                    out.write(str(cur_item))
                    if cur_item == cur_line[-1]:
                        out.write("\n")
                    else:
                        out.write(" ")




