import pandas as pd
import numpy as np
import pickle
import sys
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
        self.generate_derived_data()

    def generate_derived_data(self):
        # R, day, level1, level 2
        # into a dataframe of form:
        #     1  2  3  4
        # 0.9  v  v  v  v
        # 0.91 v  v  v  v
        # i.e.: R on the Y axis and day on the x, with one value per cell
        print("Generating derived data...")
        print("slow 1")
        self.cases_removed, self.day_count = self.generate_dict_from_julia(2)
        self.cases_unemployed, self.day_count = self.generate_dict_from_julia(3)
        self.day_list = list(range(1, self.day_count + 1))
        print("slow 3")
        self.surface_one_frame, self.surface_two_frame = self.get_surfaces()
        print("slow 3.1")
        self.r_min = list(self.cases_removed.keys())[0]
        print("slow 3.2")
        self.r_max = list(self.cases_removed.keys())[-1]
        print("slow 3.3")
        self.day_min = self.day_list[0]
        print("slow 3.4")
        self.day_max = self.day_list[-1]
        self.pop_min = min([min(list(self.cases_removed.items())[0][1]),
                       min(list(self.cases_removed.items())[-1][1]),
                       min(list(self.cases_unemployed.items())[0][1]),
                       min(list(self.cases_unemployed.items())[-1][1])
                       ])
        self.pop_max = max([max(list(self.cases_removed.items())[0][1]),
                       max(list(self.cases_removed.items())[-1][1]),
                       max(list(self.cases_unemployed.items())[0][1]),
                       max(list(self.cases_unemployed.items())[-1][1])
                       ])
        print("Derived data complete.")


    def get_results(self):
        return self.results

    def run_julia(self):
        print("Loading Julia....")


        # US_EXCHANGES = "US_exchanges_2018c.csv"
        # AGE_FRACS = "LA_age_fracs.csv"
        # LA_EMPLOYMENT = "LA_employment_by_sector_02_2020.csv"
        I = np.genfromtxt(self.us_exchanges_filename, delimiter=" ")
        age_fracs = np.genfromtxt(self.age_fracs_filename, delimiter=",")
        print (age_fracs.iloc[0].iloc[0])
        sys.exit(1)
        df.drop(df.columns[i], axis=1)

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

    def generate_dataframe_from_julia(self, surface_column):
        dict,day_count = self.generate_dict_from_julia(surface_column)
        day_list = list(range(1, day_count + 1))
        df = pd.DataFrame.from_dict(dict, orient='index', columns=day_list)
        return df

    # Returns a 2d dict of days as columns and r values
    # per row. Rows are indexed by r value and stored in order
    # in the dict (python3.6+ - dicts are ordered)
    def generate_dict_from_julia(self, surface_column):
        surfaces = self.get_results()[1]
        surface_frame = pd.DataFrame(surfaces)
        surface_frame.columns = ['R', 'day', 'unemployed', 'incapacitated']
        grouped = surface_frame.groupby(['R'])
        surface_dict = {}
        max_day = 0
        data_column = surface_frame.columns[surface_column]
        for r, r_group in grouped:
            # print(f"r: {r}")
            # print(r_group)
            day_list = []
            # Each row is 4 values: "R","day","unemployed" and "incapacitated".
            # one level for each surface. This is iterating over days grouped by R.
            for index, row in r_group.iterrows():
                day_list.append(row[data_column])
                # Optimizaiton. if covid lasts more than three years, we're in trouble.
                if (index < 1500):
                    day = int(row['day'])
                    if max_day < day:
                        max_day = day
            surface_dict.update({round(r, 2):day_list})
        return surface_dict,max_day


    # Returns a tuple of 2d dataframes. Each row is a distinct R value
    # Each column is the day. (currently 0.90 -> 6.0 in 0.1 increments for R
    # and 1-151 inclusive for day.
    #            1             2    ...           150           151
    # 0.90  4636800.0  4.636800e+06  ...  4.636797e+06  4.636797e+06
    # 0.91  4636800.0  4.636800e+06  ...  4.636796e+06  4.636796e+06
    # 0.92  4636800.0  4.636800e+06  ...  4.636796e+06  4.636796e+06
    def get_surfaces(self):
        cases_1 = self.get_results()[0]

        unemployed = self.generate_dataframe_from_julia(2)
        incapacitated = self.generate_dataframe_from_julia(3)
        return unemployed, incapacitated
