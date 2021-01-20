import pandas as pd
import numpy as np
import pickle
import ntpath
import os

class JuliaLoader:

    def __init__(self,
                 us_exchanges,
                 age_fracs,
                 employment,
                 employment_percentage,
                 run_julia=True,
                 load_all_data=False):
        # the first dataframe contains metadata not currently in use.
        # default to do not load.
        print(f"Processing {us_exchanges}, employment:{employment}, age_fracs:{age_fracs}")
        self.us_exchanges_filename = us_exchanges
        self.age_fracs_filename = age_fracs
        self.employment_filename = employment
        self.cases_complete = None
        self.employment_percentage=employment_percentage
        self.results = []

        self.binary_dump_filename_surfaces = \
            self.get_filename_only(self.employment_filename) + "_cases_surfaces.bin"
        self.binary_dump_filename_complete = \
            self.get_filename_only(self.employment_filename) + "_cases_complete.bin"
        if run_julia:
            self.run_julia()
        else:
            # R, Day  ( [R x Day] matrix. )
            # Farm_1, Farm_2, Farm_3, Farm_4,
            # Mining_1, Mining_2, Mining_3, Mining_4,
            # Utilities_1, Utilities_2, Utilities_3, Utilities_4,
            # Construction_1, Construction_2, Construction_3, Construction_4,
            # Manf_1, Manf_2, Manf_3, Manf_4, Wholesale_1,
            # Wholesale_2, Wholesale_3, Wholesale_4,
            # Retail_1, Retail_2, Retail_3, Retail_4,
            # Transp_1, Transp_2, Transp_3, Transp_4,
            # Information_1, Information_2, Information_3, Information_4,
            # Financial_1, Financial_2, Financial_3, Financial_4,
            # Prof_1, Prof_2, Prof_3, Prof_4,
            # Ed_Hlth_1, Ed_Hlth_2, Ed_Hlth_3, Ed_Hlth_4,
            # Leisure_1, Leisure_2, Leisure_3, Leisure_4,
            # Other_1, Other_2, Other_3, Other_4,
            # Gov_1, Gov_2, Gov_3, Gov_4,
            # Farm, Mining, Utilities, Construction, Manf, Wholesale, Retail, Transp, Information, Financial, Prof, Ed_Hlth, Leisure, Other, Gov,
            # Susceptible, Infected, Removed, total_E, Disease_only

            # These will throw a file not found error, which is handled
            # upstream. Typically it will then invoke a run.
            # if not path.exists(self.binary_dump_filename_surfaces):
            #     raise FileNotFoundError()
            self.cases_surfaces = pickle.load(open(self.binary_dump_filename_surfaces, "rb"))
            if load_all_data:
                # if not path.exists(self.binary_dump_filename_complete):
                #     raise FileNotFoundError()
                self.cases_complete = pickle.load(open(self.binary_dump_filename_complete, "rb"))


    def run_julia(self):
        print("Loading Julia....")
        from julia import Main as j

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
        returned_result = j.main(I, age_fracs, julia_formatted_employed,self.employment_percentage)
        print("Julia run complete.")

        self.cases_surfaces = returned_result[1]
        self.cases_complete = returned_result[0]

        self.write_binary_dump(self.binary_dump_filename_surfaces,self.cases_surfaces)
        self.write_binary_dump(self.binary_dump_filename_complete,self.cases_complete)


    def write_binary_dump(self,filename,array):
        print("Writing  binary dump: " + filename)
        outfile = open(filename,'wb')
        pickle.dump(array, outfile)
        outfile.close()

    # Strip leading path info from the filename.
    # typically used to determine the target (local) .bin
    # for various pickles.
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




