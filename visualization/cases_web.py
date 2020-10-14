#!/usr/bin/env python3
import dash
import csv
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from julia_loader import JuliaLoader
from derived_data import DerivedData
import sys
from os import path
import pickle


fig = None

tsv_file = open("inputs.tsv")
read_tsv = csv.reader(tsv_file, delimiter="\t")

data_files={}
employment_directory = None
age_fracs_directory = None
for row in read_tsv:
    if row[0].startswith("#"):
        continue
    if employment_directory is None:
        employment_directory = row[0]
        age_fracs_directory = row[1]
    else:
        data_files[row[0]]=[row[1],row[2],row[3]]

derived_data_dict = {}

def fetch_derived_data(employment_filename):
    binary_dump_filename = JuliaLoader.get_filename_only(employment_filename) + "_derived.bin"
    if not path.exists(binary_dump_filename):
        return False
    else:
        return pickle.load(open(binary_dump_filename, "rb"))


def generate_derived_data(jl,employment_filename):
    binary_dump_filename = JuliaLoader.get_filename_only(employment_filename) + "_derived.bin"

    print("Generating derived data...")
    derived_data = DerivedData (jl.cases_2,employment_filename)
    outfile = open(binary_dump_filename,'wb')
    pickle.dump(derived_data, outfile)
    outfile.close()
    return derived_data


for id in data_files.keys():
    print("Common name: " +  data_files[id][0] + " ID: " + id)
    try:
        age_fracs_filename =  age_fracs_directory +"/" + data_files[id][2]
        employment_filename = employment_directory +"/" + data_files[id][1]

        derived = fetch_derived_data(employment_filename)
        if derived is not False:
            print(f"Fetched {data_files[id][0] } from disk.")
            derived_data_dict[id] = derived
        else:
            try:
                print("Attempting binary load for julia calculation...")
                jl = JuliaLoader("US_exchanges_2018c.csv",
                                              age_fracs_filename,
                                              employment_filename,
                                              False)
            except FileNotFoundError:
                jl = JuliaLoader("US_exchanges_2018c.csv",
                                 age_fracs_filename,
                                 employment_filename,
                                 True)
            derived_data_dict[id] = generate_derived_data(jl,employment_filename)
            derived = derived_data_dict[id]
    except ValueError as e:
        print(f"Cannot load SES: {e}")


layout = go.Layout({'title': 'Surfaces',
                    'scene': dict(
                        yaxis_title='R',
                        zaxis_title='No. Employed',
                        xaxis_title='Days'),

                    # autosize=True,
                    'uirevision': 'true',
                    'legend_title': "Legend Title",
                    'width': 900,
                    'height': 900})



def create_app():
    external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    return app


app = create_app()

@app.callback(
    dash.dependencies.Output("cases-graph", "figure"),
    # dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('my-slider', 'value')])
def update_output(value):
    data = gen_fig_data(value)
    fig = go.Figure(data=data,
                    layout=layout)

    return fig


def create_lines_at_r(r_val, cases_dict, color):
    z = [r_val] * len(derived.day_list)  # constant for this R
    data = go.Scatter3d(
        mode='lines',
        x=derived.day_list,
        y=z,
        z=list(cases_dict[r_val]),

        line=dict(
            color=color,
            width=7
        )
    )
    return data


def gen_fig_data(r_value):
    # x = days
    # y = R
    # z = pop value
    return [
        go.Surface(z=derived.unemployed_surface_df.values,
                   y=derived.unemployed_surface_df.index,
                   x=derived.unemployed_surface_df.columns,
                   hoverinfo='none',
                   opacity=0.6,
                   colorscale='Blues'),

        go.Surface(z=derived.removed_surface_df.values,
                   y=derived.removed_surface_df.index,
                   x=derived.removed_surface_df.columns,
                   hoverinfo='none',
                   opacity=0.6,
                   colorscale='Greens'),
        # go.Surface(x=[day_min, day_min, day_max, day_max],
        #            y=[r_value, r_value, r_value, r_value],
        #            z=[pop_max, pop_max, pop_min, pop_min],
        #            opacity=0.5
        #            ),

        create_lines_at_r(r_value, derived.cases_removed, 'black'),
        create_lines_at_r(r_value, derived.cases_unemployed, 'green')
    ]


data = gen_fig_data(5)
fig = go.Figure(data=data,layout=layout)



app.layout = html.Div(children=[
    html.H1(children='CASES'),

    html.Div(children='''
    CASES
'''),

    dcc.Graph(
        id='cases-graph',
        figure=fig
    ),
    dcc.Slider(
        id='my-slider',
        min=derived.r_min,
        max=derived.r_max,
        step=0.01,
        value=derived.r_max
    ),
    html.Div(id='slider-output-container')

])

if __name__ == '__main__':
    app.run_server(debug=True)
