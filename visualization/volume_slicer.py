#!/usr/bin/env python3
import julia_loader
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
r_range = np.arange(0.90,6.00,0.01)

def create_app():
    external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    return app

app = create_app()


jl = julia_loader.JuliaLoader(False,True)

dict, day_count = jl.generate_dict_from_julia(3)
day_list = list(range(1, day_count + 1))
df = pd.DataFrame.from_dict(dict, orient='index', columns=day_list)

unemployed_df,incapacitated_df = jl.get_surfaces()

print(unemployed_df)
# print(unemployed_df.iloc[6]) # 6th R value; 0.96
rval_df = unemployed_df.iloc[6]

def make_figs():
    for index, row in unemployed_df.iterrows():
        # index is R value
        # tuples are day, value
        fig = px.line(rval_df,  title=index)

        print(row)

make_figs()
# fig = px.line(rval_df, x="unemployed", y="day", title='unemployment')
fig = px.line(rval_df )
#fig = go.Figure(data=go.Scatter(rval_df))
#
# def make_plot(z):
#
#
# frame_data = go.Surface(
#     z=(6.7 - k * 0.1) * np.ones((r, c)),
#     surfacecolor=np.flipud(volume[67 - k]),
#     cmin=0, cmax=200
# )
#
# frames_var = [go.Frame(data=frame_data ,
#     name=str(k) # you need to name the frame for the animation to behave properly
#     )
#     for k in range(68)]
#
# fig = go.Figure(frames= frames_var)
#
#
#
# def frame_args(duration):
#     return {
#             "frame": {"duration": duration},
#             "mode": "immediate",
#             "fromcurrent": True,
#             "transition": {"duration": duration, "easing": "linear"},
#         }

# go.Surface(z=surface_one_frame.values,
#            y=surface_one_frame.index,
#            x=surface_one_frame.columns)

sliders = [
            {
                "pad": {"b": 10, "t": 60},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f.name], frame_args(0)],
                        "label": str(k),
                        "method": "animate",
                    }
                    for k, f in enumerate(fig.frames)
                ],
            }
        ]

fig.update_layout(
         title='Slices in volumetric data',
         width=600,
         height=600,

         sliders=sliders
)

fig.show()