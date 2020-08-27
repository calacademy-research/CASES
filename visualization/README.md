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
