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
