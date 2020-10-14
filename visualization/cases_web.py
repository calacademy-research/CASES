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

cur_r = 5.0
cur_ses_id = 2

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

# input Format, tsv (represented here with comma)
# index (int id), human friendly name, employment file path, age_fracs_file_path
# output: dict by ID=[human friendly name, employment file path, age_fracs_file_path]
def read_input_metadata(filename):
    tsv_file = open(filename)
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
            employment_filename = employment_directory + "/" + row[2]
            age_fracs_filename = age_fracs_directory + "/" + row[3]
            data_files[int(row[0])] = [row[1],employment_filename,age_fracs_filename]
    return data_files

def generate_pulldown_data(metadata_dict):
    # Format:
    # [
    #     {'label': 'New York City', 'value': 'NYC'},
    #     {'label': 'Montreal', 'value': 'MTL'},
    #     {'label': 'San Francisco', 'value': 'SF'}
    # ]
    retval = []
    for id,entry in metadata_dict.items():
        entry_dict = {'label':entry[0],'value':id}
        retval.append(entry_dict)
    return retval

data_files = read_input_metadata("inputs.tsv")
derived_data_dict = {}
fig = None
for id in data_files.keys():
    print(f"Common name: { data_files[id][0]} ID: {id}")
    try:
        age_fracs_filename = data_files[id][2]
        employment_filename = data_files[id][1]

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

def gen_layout():
    title = data_files[cur_ses_id][0]
    layout = go.Layout({'title': title,
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
    [dash.dependencies.Input('ses-pulldown', 'value'),
     dash.dependencies.Input('my-slider', 'value')])
def update_output(new_ses_id,r_value):
    global cur_ses_id
    ctx = dash.callback_context
    if isinstance(new_ses_id, int):
        cur_ses_id = new_ses_id
    # for key,value in data_files.items():
    #     if value[0] == ses_string:
    #         cur_ses_id = key

    data = gen_fig_data(r_value,derived_data_dict[cur_ses_id])
    fig = go.Figure(data=data,
                    layout=gen_layout())

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


def gen_fig_data(r_value,ses_dict):
    # x = days
    # y = R
    # z = pop value
    return [
        go.Surface(z=ses_dict.unemployed_surface_df.values,
                   y=ses_dict.unemployed_surface_df.index,
                   x=ses_dict.unemployed_surface_df.columns,
                   hoverinfo='none',
                   opacity=0.6,
                   colorscale='Blues'),

        go.Surface(z=ses_dict.removed_surface_df.values,
                   y=ses_dict.removed_surface_df.index,
                   x=ses_dict.removed_surface_df.columns,
                   hoverinfo='none',
                   opacity=0.6,
                   colorscale='Greens'),
        # go.Surface(x=[day_min, day_min, day_max, day_max],
        #            y=[r_value, r_value, r_value, r_value],
        #            z=[pop_max, pop_max, pop_min, pop_min],
        #            opacity=0.5
        #            ),

        create_lines_at_r(r_value, ses_dict.cases_removed, 'black'),
        create_lines_at_r(r_value, ses_dict.cases_unemployed, 'green')
    ]


data = gen_fig_data(cur_r,derived_data_dict[cur_ses_id])
fig = go.Figure(data=data,layout=gen_layout())



app.layout = html.Div(children=[
    html.H1(children='CASES'),

    html.Div(children='CASES'),

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
    html.Div(id='slider-output-container'),
    dcc.Dropdown(
        id='ses-pulldown',
        options=generate_pulldown_data(data_files),
        value=data_files[cur_ses_id][0]
    ),
    html.Div(id='dd-pulldown-container')

])

if __name__ == '__main__':
    app.run_server(debug=True)
