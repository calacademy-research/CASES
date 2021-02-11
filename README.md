This is the CASES data visualzaiton project. Original manuscript 
[here](https://www.preprints.org/manuscript/202101.0200/v1).

# Overview
The CASES app has two major sections - data generation and data
visualization. The data generation is done in Julia, but the data is parsed
in, and preserved by, the Python code. 

The initial run will execute the Julia code on each sector, as specified in derived_data_inputs.tsv
and employment_input_data.tsv. 

Initial run will take quite some time (> 1hr). Once these data are generated, launching
will take only a few seconds. 

Production runs should be done in the Docker environemnt.

## Inputs


| Input file      | Description |
| ----------- | ----------- |
| derived_data_inputs.tsv      | Master file.  <p> The first line lists the directories containing <br> the employment file path and the age fracs path. |
| ../employment_by_sector_Feb2020   | Starting point data. Path referencing derived_data_inputs.tsv.        |
|../age_fracs|Per SES age per sector age breakdown percentages.|
|r_input_data.tsv|Specifies the R actuals by SES index number.|
|../R|Per SES R actuals refrenced by r_input_data.tsv.|
|employment_input_data.tsv| First line points to the containing directory, subsequent<br>lines contain SES index number and actual employment by SES. |
|../employment_by_sector_by_month| Employment actuals referenced by employment_input_data.tsv|
|../mortality| Mortality by SES time series. Not used, included for completeness.|
|sector_color_mappings.tsv|Color values assigned to each sector. Taste the rainbow!|
|sector_names.tsv|Maps sector name as expressed in data to the display sector name|





## Running in docker - scripts
build.sh will create the environment.

Delete.sh does what it says on the tin - removes the Docker environment

run.sh runs the production environment.

exec.sh will attach to a running docker so you can run in a shell.

docker_start.sh is used internally during dockerized running.

## Initial run

Build the system with "build.sh". These are standard docker commands, and
can be run manually on windows systems.

Run with "run.sh". This will start the system but won't kick off intermediate file
generation until the web url is hit (url wil be http://127.0.0.1:80 ). However, 
for better progress reports, it's easier to run "exec.sh". 
```
# ./exec.sh
root@de13780a0da3:/var/www/apache-flask# cd app
root@de13780a0da3:/var/www/apache-flask/app# python3 ./CASES.py
```
 
This will take about 45 minutes to run and will generate the intermediate .bin files.

At this point, it's safe to exit the prompt. The systems should be running on
localhost port 80. If not, "delete.sh" "build.sh" and, finally, "run.sh".

All done!

----------------
# Manual setup - NOT REQUIRED
This is for development only; the entire system can and should be run in docker.

### Set up Pyjulia 
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

### Set up and run the python environment

Create a python environment:

    python3 -m venv env
    source ./env/bin/activate
    python3 -m pip install -r requirements.txt
    ./cases.py

Navigate to: http://127.0.0.1:8050/
per the output



# Notes and bugs

## Docker
Docker will require more than the default 2gb that's assigned on Macs 
(Linux docker runs out of the box.)

Note that docker runs as user www-data, so set permissions accordingly on visualiztion dir for deployment





