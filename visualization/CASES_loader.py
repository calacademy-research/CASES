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

import pandas as pd
import numpy as np
import pickle
import sys
# it would be nice to load this only when needed; it's slow. but it makes python unstable
# in certain circumstances (pycharm debugging mode for one)
import julia
julia.install()
from julia.api import Julia
jl = Julia(compiled_modules=False)
from julia import Main as j


class JuliaLoader:

    def __init__(self,
                 us_exchanges,
                 age_fracs,
                 employment,
                 run_julia=True,
                 load_all_data=True):
        print(f"Processing {us_exchanges}, employment:{employment}, age_fracs:{age_fracs}")
        self.us_exchanges_filename = us_exchanges
        self.age_fracs_filename = age_fracs
        self.employment_filename = employment
        # US_EXCHANGES = US_exchanges_2018c
        # AGE_FRACS = "LA_age_fracs.csv"
        # LA_EMPLOYMENT = "LA_employment_by_sector_02_2020.csv"
        self.results = []
        if run_julia:
            self.run_julia()
        else:
            if load_all_data:
                cases_1 = pickle.load(open(self.employment_filename+"_cases_1.bin", "rb"))
            else:
                cases_1 = None
            cases_2 = pickle.load(open(self.employment_filename+"_cases_2.bin", "rb"))
            self.results.append(cases_1)
            self.results.append(cases_2)

        cases_1 = self.get_results()[0]
        self.generate_derived_data()




    def get_results(self):
        return self.results

    def run_julia(self):
        print("Loading Julia....")


        # US_EXCHANGES = "US_exchanges_2018c.csv"
        # AGE_FRACS = "LA_age_fracs.csv"
        # LA_EMPLOYMENT = "LA_employment_by_sector_02_2020.csv"
        I = np.genfromtxt(self.us_exchanges_filename, delimiter=" ")
        age_fracs_with_name = np.genfromtxt(self.age_fracs_filename, delimiter=",")
        age_fracs = np.delete(age_fracs_with_name,0,1)

        employed = pd.read_csv(self.employment_filename,
                               dtype={"Sector": str, "Feb": np.int64})

        j.eval("using DataFrames")
        julia_formatted_employed = j.DataFrame(employed.to_dict(orient='list'))

        print("Starting Julia run...")
        j.include("CASES.jl")
        returned_result = j.main(I, age_fracs, julia_formatted_employed)
        print("Julia run complete.")

        cases_2 = returned_result[1]
        pickle.dump(cases_2, open(self.employment_filename+"_cases_2.bin", "wb"))

        cases_1 = returned_result[0]
        pickle.dump(cases_1, open(self.employment_filename+"_cases_1.bin", "wb"))
        self.results.append(cases_1)
        self.results.append(cases_2)

    def save_csv(self,filename,results):
        with open(filename, "w") as out:
            for cur_line in results:
                for cur_item in cur_line:
                    out.write(str(cur_item))
                    if cur_item == cur_line[-1]:
                        out.write("\n")
                    else:
                        out.write(" ")






    # Returns a tuple of 2d dataframes. Each row is a distinct R value
    # Each column is the day. (currently 0.90 -> 6.0 in 0.1 increments for R
    # and 1-151 inclusive for day.
    #            1             2    ...           150           151
    # 0.90  4636800.0  4.636800e+06  ...  4.636797e+06  4.636797e+06
    # 0.91  4636800.0  4.636800e+06  ...  4.636796e+06  4.636796e+06
    # 0.92  4636800.0  4.636800e+06  ...  4.636796e+06  4.636796e+06
    def get_surfaces(self):
        cases_1 = self.get_results()[0]


        return unemployed, incapacitated
