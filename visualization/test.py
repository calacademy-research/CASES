#!/usr/bin/env python3
import numpy as np
import time
print("Loading julia....")
from julia import Main as j

print("Starting julia include...")
j.include("test.jl")
print("Julia bootstrap complete.")

print("Executing loader... ")
loader_results = j.loader()
# print(f"{loader_results}")
print(f"file variable foo: {j.foo}")
