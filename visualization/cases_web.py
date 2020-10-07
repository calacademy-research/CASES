#!/usr/bin/env python3
import julia_loader
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

fig = None

# R, day, level1, level 2
# into a dataframe of form:
#     1  2  3  4
# 0.9  v  v  v  v
# 0.91 v  v  v  v
# i.e.: R on the Y axis and day on the x, with one value per cell
jl = julia_loader.JuliaLoader(False)
cases_removed, day_count = jl.generate_dict_from_julia(2)
cases_unemployed, day_count = jl.generate_dict_from_julia(3)
day_list = list(range(1, day_count + 1))
surface_one_frame, surface_two_frame = jl.get_surfaces()
r_min = list(cases_removed.keys())[0]
r_max = list(cases_removed.keys())[-1]
day_min = day_list[0]
day_max = day_list[-1]
pop_min = min([min(list(cases_removed.items())[0][1]),
           min(list(cases_removed.items())[-1][1]),
           min(list(cases_unemployed.items())[0][1]),
           min(list(cases_unemployed.items())[-1][1])
           ])
pop_max = max([max(list(cases_removed.items())[0][1]),
           max(list(cases_removed.items())[-1][1]),
           max(list(cases_unemployed.items())[0][1]),
           max(list(cases_unemployed.items())[-1][1])
           ])

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
    z = [r_val] * len(day_list)  # constant for this R
    data = go.Scatter3d(
        mode='lines',
        x=day_list,
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
        go.Surface(z=surface_one_frame.values,
                   y=surface_one_frame.index,
                   x=surface_one_frame.columns,
                   hoverinfo='none',
                   opacity=0.6,
                   colorscale='Blues'),

        go.Surface(z=surface_two_frame.values,
                   y=surface_two_frame.index,
                   x=surface_two_frame.columns,
                   hoverinfo='none',
                   opacity=0.6,
                   colorscale='Greens'),
        # go.Surface(x=[day_min, day_min, day_max, day_max],
        #            y=[r_value, r_value, r_value, r_value],
        #            z=[pop_max, pop_max, pop_min, pop_min],
        #            opacity=0.5
        #            ),

        create_lines_at_r(r_value, cases_removed, 'black'),
        create_lines_at_r(r_value, cases_unemployed, 'green')
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
        min=r_min,
        max=r_max,
        step=0.01,
        value=r_max
    ),
    html.Div(id='slider-output-container')

])

if __name__ == '__main__':
    app.run_server(debug=True)
