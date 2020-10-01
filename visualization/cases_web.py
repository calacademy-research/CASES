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


def create_app():
    external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    return app

app = create_app()


@app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('my-slider', 'value')])

def update_output(value):
    return 'You have selected "{}"'.format(value)

jl = julia_loader.JuliaLoader(False)


surface_one_frame,surface_two_frame = jl.get_surfaces()

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

