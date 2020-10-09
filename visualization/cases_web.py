#!/usr/bin/env python3
import julia_loader
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

fig = None

jl = julia_loader.JuliaLoader("US_exchanges_2018c.csv",
                              "LA_age_fracs.csv",
                              "LA_employment_by_sector_02_2020.csv",
                              True)


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
    z = [r_val] * len(jl.day_list)  # constant for this R
    data = go.Scatter3d(
        mode='lines',
        x=jl.day_list,
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
        go.Surface(z=jl.surface_one_frame.values,
                   y=jl.surface_one_frame.index,
                   x=jl.surface_one_frame.columns,
                   hoverinfo='none',
                   opacity=0.6,
                   colorscale='Blues'),

        go.Surface(z=jl.surface_two_frame.values,
                   y=jl.surface_two_frame.index,
                   x=jl.surface_two_frame.columns,
                   hoverinfo='none',
                   opacity=0.6,
                   colorscale='Greens'),
        # go.Surface(x=[day_min, day_min, day_max, day_max],
        #            y=[r_value, r_value, r_value, r_value],
        #            z=[pop_max, pop_max, pop_min, pop_min],
        #            opacity=0.5
        #            ),

        create_lines_at_r(r_value, jl.cases_removed, 'black'),
        create_lines_at_r(r_value, jl.cases_unemployed, 'green')
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
        min=jl.r_min,
        max=jl.r_max,
        step=0.01,
        value=jl.r_max
    ),
    html.Div(id='slider-output-container')

])

if __name__ == '__main__':
    app.run_server(debug=False)
