#!/usr/bin/env python3
import julia_loader
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd


def create_app():
    external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    return app

app = create_app()




jl = julia_loader.JuliaLoader(False)
unemployed_df,incapacitated_df = jl.get_surfaces()


for col in unemployed_df.columns:
    print(col)

# go.Surface(z=surface_one_frame.values,
#            y=surface_one_frame.index,
#            x=surface_one_frame.columns)

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
        min=0,
        max=20,
        step=0.5,
        value=10,
    ),
    html.Div(id='slider-output-container')

])

if __name__ == '__main__':
    app.run_server(debug=True)