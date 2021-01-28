import plotly.graph_objects as go
import CASES_loader
import numpy as np
import pandas as pd

# url = "http://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv"
# dataset = pd.read_csv('gapminderDataFiveYear.csv')

jl = CASES_loader.JuliaLoader(False, True)

cases_dict, day_count = jl.generate_dict_from_julia(2)
r_values = list(cases_dict.keys())

# Returns a 2d dict of days as columns and r values
# per row. Rows are indexed by r value and stored in order
# in the dict (python3.6+ - dicts are ordered)
day_list = list(range(1, day_count + 1))
# df = pd.DataFrame.from_dict(dict, orient='index', columns=day_list)
min_value = float('inf')
max_value = -1
for cur_r in r_values:
    values_list = cases_dict[cur_r]
    for element in cases_dict[cur_r]:
        if element > max_value:
            max_value = element
        if element < min_value:
            min_value = element

# make figure
fig_dict = {
    "data": [],
    "layout": {},
    "frames": []
}

# fill in most of layout
fig_dict["layout"]["xaxis"] = {"range": [day_list[0], day_list[-1]], "title": "Day"}
fig_dict["layout"]["yaxis"] = {"title": "Employment per R0 value", "type": "linear", "range": [min_value, max_value]}
fig_dict["layout"]["hovermode"] = "closest"
fig_dict["layout"]["updatemenus"] = [
    {
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 500, "redraw": False},
                                "fromcurrent": True, "transition": {"duration": 1,
                                                                    "easing": "quadratic-in-out"}}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": False,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }
]

sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
        "prefix": "R:",
        "visible": True,
        "xanchor": "right"
    },
    "transition": {"duration": 0.1, "easing": "cubic-in-out"},
    "pad": {"b": 10, "t": 50},
    "len": 0.9,
    "x": 0.1,
    "y": 0,
    "steps": []
}


def create_line_at_r(r_val):
    data = {
        "x": day_list,
        "y": list(cases_dict[r_val]),
        "mode": "lines",
        "name": cur_r
    }
    return data


def create_volume_at_r(r_val):
    z = [r_val] * len(day_list) # constant for this R
    data = go.Scatter3d(
        mode='lines',
        x=day_list,
        y=z,
        z=list(cases_dict[r_val]),

        line=dict(
            color='darkblue',
            width=2
        )
    )
    return data



# initial display

data_dict = create_volume_at_r(0.9)
fig_dict["data"].append(data_dict)

# make frames
for cur_r in r_values:
    frame = {"data": [], "name": str(cur_r)}
    data_dict = create_volume_at_r(cur_r)
    frame["data"].append(data_dict)

    fig_dict["frames"].append(frame)
    slider_step = {"args": [
        [cur_r],
        {"frame": {"duration": 0.1, "redraw": False},
         "mode": "immediate",
         "transition": {"duration": 0.1}}
    ],
        "label": cur_r,
        "method": "animate"}
    sliders_dict["steps"].append(slider_step)

fig_dict["layout"]["sliders"] = [sliders_dict]

fig = go.Figure(fig_dict)

fig.show()
