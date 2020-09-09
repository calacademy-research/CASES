#!/usr/bin/env python3
import julia_loader
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

jl = julia_loader.JuliaLoader(False)
cases_1 = jl.get_results()[0]
surfaces = jl.get_results()[1]

# Read data from a csv
z_data = pd.read_csv('mt_bruno_elevation.csv')
surface_frame = pd.DataFrame(surfaces)
surface_frame.columns=['R','day','level1','level2']

# This revolting code transforms data in this form:
# R, day, level1, level 2
# into a dataframe of form:
#     1  2  3  4
#0.9  v  v  v  v
#0.91 v  v  v  v
# i.e.: R on the Y axis and day on the x, with one value per cell
https://community.plotly.com/t/two-3d-surface-with-different-color-map/18931/4
grouped = surface_frame.groupby(['R'])
surface_one_frame = None
for r, r_group in grouped:
    # print(f"r: {r}")
    # print(r_group)
    day_list = {}
    master_index = 0
    for index, row in r_group.iterrows():
        day_list[master_index+1] = row['level1']
        master_index+=1
    new_df = pd.DataFrame(day_list,index=[r])

    if surface_one_frame is None:
        surface_one_frame = new_df
    else:
        surface_one_frame = surface_one_frame.append(new_df)

print(f"final: {surface_one_frame}")


fig = go.Figure(data=[go.Surface(z=surface_one_frame.values)])

fig.update_layout(title='Surface1', autosize=False,
                  width=1500, height=1500,
                  margin=dict(l=65, r=50, b=65, t=90))
# 0.95 94 4.636797103492999e6 4.636799157752344e6
# 0.95 95 4.636797077189081e6 4.636799150103999e6
# 0.95 96 4.636797050977077e6 4.636799142482381e6
# 0.95 97 4.636797024856668e6 4.6367991348873945e6
# 0.95 98 4.636796998827534e6 4.636799127318948e6
# 0.95 99 4.636796972889357e6 4.636799119776948e6
# 0.95 100 4.636796947041822e6 4.636799112261306e6

#splot "Oxnard_CSA_CASES6_surfaces_08_29b.dat" using 2:1:3 with lines lw 2.5 \
# palette,"Oxnard_CSA_CASES6_surfaces_08_29b.dat" using 2:1:4 with lines lw .25 lc rgb "grey"

app.layout = html.Div(children=[
    html.H1(children='Jupyter notebook->Julia->python->dash proof of concept'),

    html.Div(children='''
        CASES: Pulse perturbation
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)

