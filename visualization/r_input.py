from derived_data import DerivedData
from os import path
import csv

class EmploymentInput:

    def __init__(self, sector_names):
        self.sector_names = sector_names
        self.employment_data_files = self.read_input_data("r_input_data.tsv")
        self.employment_input_data_dict = {}
        self.read_data()


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
                sector_name = self.sector_names[row[0]]
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