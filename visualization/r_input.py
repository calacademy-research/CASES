import csv
from dateutil.parser import parse as date_parser

class RInput:
    def __init__(self,day_count):
        self.r_data_files = self.read_input_data("r_input_data.tsv")
        self.r_input_data_dict = {}
        self.day_count = day_count
        self.read_data()


    def read_data(self):
        failed_loads = []

        for id in self.r_data_files.keys():
            try:
                r_filename = self.r_data_files[id]
                self.r_input_data_dict[id] = self.load_r_data(r_filename)
            except ValueError as e:
                print(f"Cannot load r input data for ID {id}: {e}")
                failed_loads.append(id)

        for id in failed_loads:
            if id in self.sector_names.keys():
                del self.r_input_data_dict[id]

    def is_date(self,date_string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            date_parser(date_string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

    def load_r_data(self, r_filename):
        results = {}
        csv_file = open(r_filename)
        read_csv = csv.reader(csv_file, delimiter=",")

        # R-Effective County Model Time Series for San Francisco,,,,,,,
        # COVID Assessment Tool - Downloaded on 2020-08-27,,,,,,,
        # Date,CovidActNow,LEMMA,JHU,Stanford,UCSF,Harvard,Ensemble
        # 2020-01-31,0,0,2.35,0,0,0,0
        r_col = None

        for row in read_csv:
            date_string = row[0]
            if not self.is_date(date_string):
                if 'Ensemble' in row:
                    r_col = row.index('Ensemble')
                continue
            if r_col is None:
                raise ValueError(f"No Ensemble column found in {r_filename}")

            r = float(row[r_col])
            # print(f" {r_filename} Got {date_string}:{r}")
            day_val = (date_parser(date_string) - self.day_zero).days

            if day_val >= 0 and day_val < self.day_count:
                results[day_val] = r

        return results



    def read_input_data(self, filename):
        tsv_file = open(filename)
        read_tsv = csv.reader(tsv_file, delimiter="\t")

        data_files={}
        r_directory = None
        for row in read_tsv:
            if row[0].startswith("#"):
                continue
            if r_directory is None:
                r_directory = row[0]
                self.day_zero = date_parser(row[1])
            else:
                r_filename = r_directory + "/" + row[1]
                data_files[int(row[0])] = r_filename
        return data_files

