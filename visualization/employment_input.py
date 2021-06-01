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

from derived_data import DerivedData
from os import path
import csv
import sys

class EmploymentInput:

    def __init__(self):
        self.employment_data_files = self.read_input_data("employment_input_data.tsv")
        self.sector_names = self.read_input_mappings("sector_names.tsv")
        self.months = {"Feb":29,"Mar":31,"Apr":30,"May":31,"Jun":30,"Jul":30,"Aug":31,"Sep":30,"Oct":31,"Nov":30,"Dec":31}
        self.employment_input_data_dict = {}
        self.employment_by_ses_by_day = {}
        self.employment_by_ses_by_sector_by_day = {}

        self.read_data()
        self.create_daily_sector_data()
        self.create_daily_total_data()


 # entry point
    def read_data(self):
        failed_loads = []

        for id in self.employment_data_files.keys():
            try:
                employment_filename = self.employment_data_files[id]
                self.employment_input_data_dict[id] = self.load_employemnt_data(id,employment_filename)
            except ValueError as e:
                print(f"Cannot load employment input data for ID {id}: {e}")
                failed_loads.append(id)

        for id in failed_loads:
            if id in self.sector_names.keys():
                del self.employment_input_data_dict[id]

    def create_daily_total_data(self):
        self.employment_by_ses_by_day={}
        for id in self.employment_data_files.keys():
            self.employment_by_ses_by_day[id] = []
            for day in range(0,self.day_count):
                total = 0

                for cur_sector in self.sector_names.values():
                    total += self.employment_by_ses_by_sector_by_day[id][cur_sector][day]
                self.employment_by_ses_by_day[id].append(total)

    def create_daily_sector_data(self):
        """
        This ugly thing creates self.day_count entries in
        self.employment_by_day_by_ses_by_sector[id][cur_sector] - since the
        employment data is by month and the R data is by day, we're stretching
        out the values. There's a better way to do this. Probably numpy.
        :return:
        """
        try:
            for id in self.employment_data_files.keys():
                if id not in self.employment_by_ses_by_sector_by_day.keys():
                    self.employment_by_ses_by_sector_by_day[id] = {}
                cur_data_dict = self.employment_input_data_dict[id]
                for cur_sector in self.sector_names.values():
                    if cur_sector not in self.employment_by_ses_by_sector_by_day[id]:
                        self.employment_by_ses_by_sector_by_day[id][cur_sector] = []
                    for cur_month in self.months.keys():
                        if cur_month in cur_data_dict[cur_sector]:

                            employment = cur_data_dict[cur_sector][cur_month]
                            # print(f"in SES {self.employment_data_files[id]}, sector employment in {cur_sector} in {cur_month}: {employment}")
                            for i in range (0,self.months[cur_month]):
                                if len(self.employment_by_ses_by_sector_by_day[id][cur_sector]) < self.day_count:
                                    self.employment_by_ses_by_sector_by_day[id][cur_sector].append(employment)
        except KeyError as e:
            print(f"Bad key. Probably a missing sector. Aborting: {e}")
            sys.exit(1)



    def load_employemnt_data(self,id,employment_filename):
        results = {}
        tsv_file = open(employment_filename)
        read_tsv = csv.reader(tsv_file, delimiter="\t")


        months=None
        for row in read_tsv:


            if months is None and row[0].startswith("#"):
                months=[]
                for index,month in enumerate(row):
                    if index > 0:
                        months.append(month)
                continue

            else:
                try:
                    sector_name = self.sector_names[row[0]]
                except KeyError as e:
                    print(f"invalid key:{row[0]}")
                    sys.exit(1)
                for index,month_val in enumerate(row):
                    if index > 0:
                        month = months[index -1]
                        if not month_val.isnumeric():
                            print(f"Bad row in {employment_filename}: {row}")
                        results[sector_name][month] = int(month_val)
                    else:
                        results[sector_name] = {}

        for cur_sector in results:
            sector_total=0
            for month in months:
                sector_total += results[cur_sector][month]
            results[cur_sector]['total'] = sector_total


        return results


    def read_input_data(self,filename):
        tsv_file = open(filename)
        read_tsv = csv.reader(tsv_file, delimiter="\t")

        data_files={}
        employment_directory = None
        for row in read_tsv:
            if row[0].startswith("#"):
                continue
            if employment_directory is None:
                employment_directory = row[0]
                self.day_count = int(row[1])

            else:
                employment_filename = employment_directory + "/" + row[1]
                data_files[int(row[0])] = employment_filename
        return data_files

    # Returns a name mapping from the employment tsv to the internal
    # final display names.
    def read_input_mappings(self,filename):
        tsv_file = open(filename)
        read_tsv = csv.reader(tsv_file, delimiter="\t")

        sector_names={}
        for row in read_tsv:
            if row[0].startswith("#"):
                continue
            sector_names[row[0]] = row[1]
        return sector_names