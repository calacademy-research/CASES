#!/usr/bin/env python3
import numpy as np
import csv
import time
import pandas as pd
import numpy as np
print("Loading julia....")
from julia import Main as j
US_EXCHANGES = "US_exchanges_2018c.csv"
AGE_FRACS = "LA_age_fracs.csv"
# age_fracs = list(csv.reader(open("LA_age_fracs.csv"), delimiter=' '))
I = np.genfromtxt(US_EXCHANGES,delimiter=" ")
age_fracs = np.genfromtxt(AGE_FRACS,delimiter=" ")
print("Starting julia include...")
j.include("CASES.jl")
#j.main(age_fracs)
returned_result = j.main(I,age_fracs)
result = j.io1a
print("Julia bootstrap complete.")

# print(f"result: {result}")
print(f"result 1: {returned_result[0]}")
print(f"result 2: {returned_result[1]}")
print("done!")
#loader_results = j.loader()
# print(f"{loader_results}")
#print(f"file variable foo: {j.foo}")
