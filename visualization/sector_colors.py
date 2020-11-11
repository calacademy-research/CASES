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

