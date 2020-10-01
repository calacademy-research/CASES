import pandas as pd
import numpy as np
import pickle

class JuliaLoader:

    def __init__(self,run_julia=True):
        self.results = []
        if run_julia:
            self.run_julia()
        else:
            cases_1 = pickle.load(open("cases_1", "rb"))
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

        cases_1 = returned_result[0]
        cases_2 = returned_result[1]
        pickle.dump(cases_1, open("cases_1", "wb"))
        pickle.dump(cases_2, open("cases_2", "wb"))

    def save_csv(self,filename,results):
        with open(filename, "w") as out:
            for cur_line in results:
                for cur_item in cur_line:
                    out.write(str(cur_item))
                    if cur_item == cur_line[-1]:
                        out.write("\n")
                    else:
                        out.write(" ")

    def generate_dataframe_from_julia(self, surfaces, surface_column):
        surface_frame = pd.DataFrame(surfaces)
        surface_frame.columns = ['R', 'day', 'level1', 'level2']
        grouped = surface_frame.groupby(['R'])
        surface_one_frame = None
        for r, r_group in grouped:
            # print(f"r: {r}")
            # print(r_group)
            day_list = {}
            master_index = 0
            for index, row in r_group.iterrows():
                day_list[master_index + 1] = row[surface_frame.columns[surface_column]]
                master_index += 1
            new_df = pd.DataFrame(day_list, index=[r])

            if surface_one_frame is None:
                surface_one_frame = new_df
            else:
                surface_one_frame = surface_one_frame.append(new_df)

        # print(f"final: {surface_one_frame}")
        return surface_one_frame

    # Returns a tuple of 2d dataframes. Each row is a distinct R value
    # Each column is the day. (currently 0.90 -> 6.0 in 0.1 increments for R
    # and 1-151 inclusive for day.
    def get_surfaces(self):
        cases_1 = self.get_results()[0]
        surfaces = self.get_results()[1]
        unemployemnt = self.generate_dataframe_from_julia(surfaces, 2)
        incapacitated = self.generate_dataframe_from_julia(surfaces, 3)
        return unemployemnt, incapacitated
