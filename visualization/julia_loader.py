import pandas as pd
import numpy as np
import pickle

class JuliaLoader:

    def __init__(self,run_julia=True,load_all_data=True):
        self.results = []
        if run_julia:
            self.run_julia()
        else:
            if load_all_data:
                cases_1 = pickle.load(open("cases_1", "rb"))
            else:
                cases_1 = None
            cases_2 = pickle.load(open("cases_2", "rb"))
            self.results.append(cases_1)
            self.results.append(cases_2)

    def get_results(self):
        return self.results

    def run_julia(self):
        print("Loading Julia....")
        from julia import Main as j
        US_EXCHANGES = "US_exchanges_2018c.csv"
        AGE_FRACS = "LA_age_fracs.csv"
        LA_EMPLOYMENT = "LA_employment_by_sector_02_2020.csv"
        I = np.genfromtxt(US_EXCHANGES, delimiter=" ")
        age_fracs = np.genfromtxt(AGE_FRACS, delimiter=" ")

        employed = pd.read_csv(LA_EMPLOYMENT,
                               dtype={"Sector": str, "Feb": np.int64})

        j.eval("using DataFrames")
        julia_formatted_employed = j.DataFrame(employed.to_dict(orient='list'))

        print("Starting Julia run...")
        j.include("CASES.jl")
        returned_result = j.main(I, age_fracs, julia_formatted_employed)
        print("Julia run complete.")

        cases_2 = returned_result[1]
        pickle.dump(cases_2, open("cases_2", "wb"))

        cases_1 = returned_result[0]
        pickle.dump(cases_1, open("cases_1", "wb"))
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
