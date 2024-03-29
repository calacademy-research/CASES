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


# TODO: Double check that the LA_CASES6_output sector columns match up
# with self.sectors; ensure there's no off-by-one error
class DerivedData:


    #  "total_E", "Disease_only"

    def __init__(self, jl, employment_filename, sector_names,col_unemployed=3, col_removed=2):
        self.jl = jl
        self.sector_names = sector_names
        self.removed_index = col_unemployed
        self.unemployed_index = col_removed
        self.employment_filename = employment_filename
        self.sectors_dict = {}

        for value in sector_names.values():
            self.sectors_dict[value] = None
        self.complete_array = ['R', 'day',
                          "Farm_1", "Farm_2", "Farm_3", "Farm_4",
                          "Mining_1", "Mining_2", "Mining_3", "Mining_4",
                          "Utilities_1", "Utilities_2", "Utilities_3", "Utilities_4",
                          "Construction_1", "Construction_2", "Construction_3", "Construction_4",
                          "Manf_1", "Manf_2", "Manf_3", "Manf_4",
                          "Wholesale_1", "Wholesale_2", "Wholesale_3",
                          "Wholesale_4", "Retail_1", "Retail_2",
                          "Retail_3", "Retail_4", "Transp_1", "Transp_2", "Transp_3", "Transp_4",
                          "Information_1", "Information_2", "Information_3", "Information_4",
                          "Financial_1", "Financial_2", "Financial_3", "Financial_4",
                          "Prof_1", "Prof_2", "Prof_3", "Prof_4",
                          "Ed_Hlth_1", "Ed_Hlth_2", "Ed_Hlth_3", "Ed_Hlth_4",
                          "Leisure_1", "Leisure_2", "Leisure_3", "Leisure_4",
                          "Other_1", "Other_2", "Other_3", "Other_4",
                          "Gov_1", "Gov_2", "Gov_3", "Gov_4"]
        for value in sector_names.values():
            self.complete_array.append(value)
        self.complete_array.extend(["Susceptible", "Infected", "Removed"])
        self.sectors_df = {}
        self.sector_max = {}
        self.sector_min = {}
        self.generate_all_dataframes_from_julia()
        self.generate_derived_data()

    # Normalize to 1000
    def normalize_dict(self,dict):
        r_val_keys = list(dict.keys())
        r_val_keys.sort()
        val1 = dict[r_val_keys[0]][0]
        val2 = dict[r_val_keys[-1]][-1]
        # No python 3.8 for you.
        # val1a = dict[next(iter(dict))][0]
        # val2a = dict[next(reversed(dict))][-1]
        maxval = float(max(val1,val2))
        retval = {}
        for key in dict.keys():
            source_array = dict[key]
            target = [(x / maxval) * 100 for x in source_array]
            retval[key] = target
        return retval

    def generate_all_dataframes_from_julia(self):
        self.unemployed_surface_df,day_count = self.generate_dataframe_from_julia(self.jl.cases_surfaces, self.unemployed_index)
        self.removed_surface_df,day_count = self.generate_dataframe_from_julia(self.jl.cases_surfaces, self.removed_index)
        for cur_sector in self.sectors_dict.keys():
            print(f"  Generating derived surface for sector {cur_sector}")
            dict = self.generate_dict_from_julia_complete(self.complete_array.index(cur_sector))
            n_dict = self.normalize_dict(dict)
            self.sectors_dict[cur_sector] = n_dict
            day_list = list(range(1, day_count + 1))
            df = pd.DataFrame.from_dict(n_dict, orient='index', columns=day_list)
            self.sectors_df[cur_sector] = df

    def generate_dataframe_from_julia(self, cases_frame, surface_column):
        dict, day_count = self.generate_dict_from_julia_surfaces(cases_frame, surface_column)
        day_list = list(range(1, day_count + 1))
        df = pd.DataFrame.from_dict(dict, orient='index', columns=day_list)
        return df,day_count

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
    def generate_dict_from_julia_surfaces(self, cases_frame, surface_column):
        surfaces = cases_frame
        surface_frame = pd.DataFrame(surfaces)
        surface_frame.columns = ['R', 'day', 'unemployed', 'removed']
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
            surface_dict.update({round(r, 2): day_list})
        return surface_dict, max_day

    def generate_dict_from_julia_complete(self, surface_column_index):
        complete = self.jl.cases_complete
        surface_frame = pd.DataFrame(complete)
        surface_frame.columns = self.complete_array
        grouped = surface_frame.groupby(['R'])
        surface_dict = {}
        data_column = surface_frame.columns[surface_column_index]
        for r, r_group in grouped:
            # print(f"r: {r}")
            # print(r_group)
            day_list = []
            # Each row is 4 values: "R","day","unemployed" and "incapacitated".
            # one level for each surface. This is iterating over days grouped by R.
            for index, row in r_group.iterrows():
                day_list.append(row[data_column])

            surface_dict.update({round(r, 2): day_list})
        return surface_dict

    def generate_derived_data(self):
        # R, day, level1, level 2
        # into a dataframe of form:
        #     1  2  3  4
        # 0.9  v  v  v  v
        # 0.91 v  v  v  v
        # i.e.: R on the Y axis and day on the x, with one value per cell
        self.cases_removed, self.day_count = self.generate_dict_from_julia_surfaces(self.jl.cases_surfaces,
                                                                                    self.removed_index)
        self.cases_unemployed, self.day_count = self.generate_dict_from_julia_surfaces(self.jl.cases_surfaces,
                                                                                       self.unemployed_index)
        self.day_list = list(range(1, self.day_count + 1))
        self.r_min = list(self.cases_removed.keys())[0]
        self.r_max = list(self.cases_removed.keys())[-1]
        self.day_min = self.day_list[0]
        self.day_max = self.day_list[-1]
        # this is the absolute minimum; replacing this with a relative to pop_max minimum.

        # self.pop_min = min([min(list(self.cases_removed.items())[0][1]),
        #                     min(list(self.cases_removed.items())[-1][1]),
        #                     min(list(self.cases_unemployed.items())[0][1]),
        #                     min(list(self.cases_unemployed.items())[-1][1])
        #                     ])
        self.pop_max = max([max(list(self.cases_removed.items())[0][1]),
                            max(list(self.cases_removed.items())[-1][1]),
                            max(list(self.cases_unemployed.items())[0][1]),
                            max(list(self.cases_unemployed.items())[-1][1])
                            ])
        self.pop_min = self.pop_max * 0.8

        for sector_key in self.sectors_dict.keys():
            self.sector_max[sector_key] = self.sectors_dict[sector_key][self.r_min][0]
            self.sector_min[sector_key] = self.sectors_dict[sector_key][self.r_max][-1]


        print("Derived data complete.")
