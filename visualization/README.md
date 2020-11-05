TODO:
Make it so this outputs .csv or .tsv for the model(s).
  Verify against roopnarine raw model runs
Test on windows
we're using '/' in paths in r_input_data.tsv. Check this works on windows.
We've got spaces in paths for r_input_data.tsv; test & verify.



Document input files.

r_input_data.tsv:
Contains per-day R values for each SES. Used for graphing the true 
trajectory of the pandemic.

Format:
<ses ID>    <relative path to csv file>

Input file format example below. We pull data from the "Ensenble" column.
R-Effective County Model Time Series for San Francisco,,,,,,,
COVID Assessment Tool - Downloaded on 2020-08-27,,,,,,,
Date,CovidActNow,LEMMA,JHU,Stanford,UCSF,Harvard,Ensemble
2020-01-31,0,0,2.35,0,0,0,0





To convert notebook code to a script:


jupyter nbconvert --to script ../CASES5-01-Basic_model.ipynb
outputs:
CASES5-01-Basic_model.jl

Create a python environment:
python3 -m venv env
source ./env/bin/activate
python3 -m pip install -r requirements.txt
./cases.py

surf to: http://127.0.0.1:8050/
per the output

-----------
gnuplot was run thusly:
gnuplot> set xlabel "Day"
gnuplot> set ylabel "R0"
gnuplot> set title "Los Angeles-Glendale, 08/25"
gnuplot> splot "LA_CASES6_surfaces_08_25b.dat" using 2:1:3 with lines lw 2.5 palette,"LA_CASES6_surfaces_08_25b.dat" using 2:1:4 with lines lw .25 lc rgb "grey"
gnuplot> set title "Stockton-Lodi, 08/26"
gnuplot> splot "Stockton-Lodi_CASES6_surfaces_08_26b.dat" using 2:1:3 with lines lw 2.5 palette,"Stockton-Lodi_CASES6_surfaces_08_26b.dat" using 2:1:4 with lines lw .25 lc rgb "grey"

----------------
Pyjulia 
Getting pyJulia setup requires a bit of work, and it will require upkeep if your
python3 environment changes signifigantly. 

First, install python and setup your pyenv:
```
python3 -m venv env
activate ./env/bin/activate
```

Next, install julia from (here)[https://julialang.org/downloads/]

Next, install pyJulia from (here)[https://pyjulia.readthedocs.io/en/latest/installation.html]
(don't forget to run the "julia.install()" step)

Add julia to your path. On the mac, that's going to look like this:
```
handball:~ joe$ grep -i julia ~/.bash_profile
export PATH="/Applications/Julia-1.5.app/Contents/Resources/julia/bin:$PATH"
```

Finally, run julia and type:

```
import Pkg; Pkg.add("DataFrames")
import Pkg; Pkg.add("DifferentialEquations")
import Pkg; Pkg.add("CSV")
```
control-d to exit.

Run and enjoy!