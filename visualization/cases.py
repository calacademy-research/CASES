#!/usr/bin/env python3
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
print("Loading julia....")
from julia import Main as j

print("Starting julia include...")
j.include("CASES5-01-Basic_model.jl")
print("Julia bootstrap complete.")
# julia_array_ep = j.ep
# julia_array_e = j.e
# julia_array_u = j.u
#
#
# print(f"Got ep:\n {j.ep}")
# print(f"Got e:\n {j.e}")

df = pd.DataFrame({
    "Pulse model": j.ep,
    "Basic press model": j.e
})


#fig = px.line(df, x="t", y="Total employment")

fig = px.line(df)
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
