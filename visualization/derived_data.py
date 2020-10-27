import pandas as pd

REMOVED_INDEX=3
UNEMPLOYED_INDEX=2
class DerivedData:
    def __init__(self,cases,employment_filename):
        self.cases = cases
        self.employment_filename = employment_filename
        self.unemployed_surface_df = self.generate_dataframe_from_julia(UNEMPLOYED_INDEX)
        self.removed_surface_df = self.generate_dataframe_from_julia(REMOVED_INDEX)
        self.generate_derived_data()

    def generate_dataframe_from_julia(self, surface_column):
        dict,day_count = self.generate_dict_from_julia(surface_column)
        day_list = list(range(1, day_count + 1))
        df = pd.DataFrame.from_dict(dict, orient='index', columns=day_list)
        return df

    # Returns a tuple of 2d dataframes. Each row is a distinct R value
    # Each column is the day. (currently 0.90 -> 6.0 in 0.1 increments for R
    # and 1-151 inclusive for day.
    #            1             2    ...           150           151
    # 0.90  4636800.0  4.636800e+06  ...  4.636797e+06  4.636797e+06
    # 0.91  4636800.0  4.636800e+06  ...  4.636796e+06  4.636796e+06
    # 0.92  4636800.0  4.636800e+06  ...  4.636796e+06  4.636796e+06





    # Returns a 2d dict of days as columns and r values
    # per row. Rows are indexed by r value and stored in order
    # in the dict (python3.6+ - dicts are ordered)
    def generate_dict_from_julia(self, surface_column):
        surfaces = self.cases
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

    def generate_derived_data(self):
        # R, day, level1, level 2
        # into a dataframe of form:
        #     1  2  3  4
        # 0.9  v  v  v  v
        # 0.91 v  v  v  v
        # i.e.: R on the Y axis and day on the x, with one value per cell
        self.cases_removed, self.day_count = self.generate_dict_from_julia(REMOVED_INDEX)
        self.cases_unemployed, self.day_count = self.generate_dict_from_julia(UNEMPLOYED_INDEX)
        self.day_list = list(range(1, self.day_count + 1))
        self.r_min = list(self.cases_removed.keys())[0]
        self.r_max = list(self.cases_removed.keys())[-1]
        self.day_min = self.day_list[0]
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