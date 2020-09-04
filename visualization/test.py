#!/usr/bin/env python3
import numpy as np
import csv
import time
import pandas as pd
import numpy as np
import pickle
RUN_JULIA=True
cases_1=cases_2=None
if (RUN_JULIA):
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
    julia_formatted_employed  = j.DataFrame(employed.to_dict(orient='list'))


    print("Starting Julia run...")
    j.include("CASES.jl")
    returned_result = j.main(I,age_fracs,julia_formatted_employed)
    print("Julia run complete.")

    cases_1 = returned_result[0]
    cases_2 = returned_result[1]
    pickle.dump( cases_1, open( "cases_1", "wb" ) )
    pickle.dump( cases_2, open( "cases_2", "wb" ) )

if cases_1 is None:
    cases_1 = pickle.load(open("cases_1", "rb"))
    cases_2 = pickle.load(open("cases_2", "rb"))


# print(f"result 1: {returned_result[0]}")
# print(f"result 2: {returned_result[1]}")
# print("done!")

with open("LA_CASES6_output_python.dat","w") as out:
    out.write("R,Day Farm_1,Farm_2,Farm_3,Farm_4,Mining_1,Mining_2,Mining_3,Mining_4,Utilities_1,Utilities_2,Utilities_3,Utilities_4,Construction_1,Construction_2,Construction_3,Construction_4,Manf_1,Manf_2,Manf_3,Manf_4,Wholesale_1,Wholesale_2,Wholesale_3,Wholesale_4,Retail_1,Retail_2,Retail_3,Retail_4,Transp_1,Transp_2,Transp_3,Transp_4,Information_1,Information_2,Information_3,Information_4,Financial_1,Financial_2,Financial_3,Financial_4,Prof_1,Prof_2,Prof_3,Prof_4,Ed_Hlth_1,Ed_Hlth_2,Ed_Hlth_3,Ed_Hlth_4,Leisure_1,Leisure_2,Leisure_3,Leisure_4,Other_1,Other_2,Other_3,Other_4,Gov_1,Gov_2,Gov_3,Gov_4,Farm,Mining,Utilities,Construction,Manf,Wholesale,Retail,Transp,Information,Financial,Prof,Ed_Hlth,Leisure,Other,Gov,Susceptible,Infected,Removed,total_E,Disease_only\n")
    for cur_line in cases_1:
        for cur_item in cur_line:
            out.write(str(cur_item))
            if cur_item == cur_line[-1]:
                out.write("\n")
            else:
                out.write(",")

with open("LA_CASES6_surfaces_python.dat","w") as out:
    for cur_line in cases_2:
        for cur_item in cur_line:
            out.write(str(cur_item))
            if cur_item == cur_line[-1]:
                out.write("\n")
            else:
                out.write(" ")
#loader_results = j.loader()
# print(f"{loader_results}")
#print(f"file variable foo: {j.foo}")
