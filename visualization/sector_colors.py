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

import csv


class SectorColors:
    def __init__(self):
        self.surface_color_mappings = {}
        self.trace_color_mappings = {}
        self.read_color_mappings("sector_color_mappings.tsv")



    def read_color_mappings(self, filename):
        tsv_file = open(filename)
        read_tsv = csv.reader(tsv_file, delimiter="\t")

        for row in read_tsv:
            if row[0].startswith("#"):
                continue
            sector_name = row[0]
            start_color = row[1]
            end_color = row[2]
            trace_color = row[3]
            # [1, "rgb(0, 204, 255)"],
            # [0, "rgb(0, 41, 51)"]

            value = [f"rgb({start_color})",
                     f"rgb({end_color})"]

            self.surface_color_mappings[sector_name] = value

            self.trace_color_mappings[sector_name] = f"rgb({trace_color})"

