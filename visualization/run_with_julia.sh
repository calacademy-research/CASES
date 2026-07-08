#!/bin/bash

export LD_LIBRARY_PATH=''
export JULIA_LOAD_PATH=/usr/local/julia/share/julia
export JULIA_PKGDIR=/usr/local/julia/share/julia/site/v0.6

python3 ./test.py

