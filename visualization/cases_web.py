#!/usr/bin/env python3
import julia_loader
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd

# This revolting code transforms data in this form:
# R, day, level1, level 2
# into a dataframe of form:
#     1  2  3  4
#0.9  v  v  v  v
#0.91 v  v  v  v
# i.e.: R on the Y axis and day on the x, with one value per cell
def generate_dataframe_from_julia(surfaces,surface_column):
    surface_frame = pd.DataFrame(surfaces)
    surface_frame.columns = ['R', 'day', 'level1', 'level2']
    grouped = surface_frame.groupby(['R'])
    surface_one_frame = None
    for r, r_group in grouped:
        # print(f"r: {r}")
        # print(r_group)
        day_list = {}
        master_index = 0
        for index, row in r_group.iterrows():
            day_list[master_index + 1] = row[ surface_frame.columns[surface_column]]
            master_index += 1
        new_df = pd.DataFrame(day_list, index=[r])

        if surface_one_frame is None:
            surface_one_frame = new_df
        else:
            surface_one_frame = surface_one_frame.append(new_df)

    # print(f"final: {surface_one_frame}")
    return surface_one_frame

external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

jl = julia_loader.JuliaLoader(False)
cases_1 = jl.get_results()[0]
surfaces = jl.get_results()[1]

surface_one_frame = generate_dataframe_from_julia(surfaces,2)
surface_two_frame = generate_dataframe_from_julia(surfaces,3)


# https://community.plotly.com/t/two-3d-surface-with-different-color-map/18931/4

data = [
    go.Surface(z=surface_one_frame.values,
               y=surface_one_frame.index,
               x=surface_one_frame.columns,

               opacity=0.6,
               colorscale='Blues'),

    go.Surface(z=surface_two_frame.values,
               y=surface_two_frame.index,
               x=surface_two_frame.columns,

               opacity=0.6,
               colorscale='Greens')
]
fig = go.Figure(data=data)

fig.update_layout(title='Surfaces',
                  scene=dict(
                      yaxis_title='R',
                      zaxis_title='No. Employed',
                      xaxis_title='Days'),

                  # autosize=True,

                  legend_title="Legend Title",

                  width=1100,
                  height=1100
                  )




app.layout = html.Div(children=[
    html.H1(children='CASES'),

    html.Div(children='''
        CASES
    '''),

    dcc.Graph(
        id='cases-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)

