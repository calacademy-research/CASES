TODO:

Docker note: increase the ram to more than the default 2gb

visual key/hover/explanation of WTF is going on

Note that docker runs as user www-data, so set permissions accordingly on visualiztion dir for deployment



input files.
---------------------
derived_data_inputs.tsv 
This is the master file listing. The first line lists the directories containing
the the employment file path and the age fracs path. 
Subsequent lines contain:
# SES ID, display name, employment filename, age_fracs filename
 "Employment filename" will look in 



r_input_data.tsv:
Contains per-day R values for each SES. 

Format:
<ses ID>    <relative path to csv file>

Input file format example below. We pull data from the column marked "Ensenble".
The index of this column may vary.

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

Add julia to your path. On the mac, that's going to look like this (add this line to your .bashrc):
```
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
