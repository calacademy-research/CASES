#!/usr/bin/env python3
import dash
import data_loader
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go


fig = None
cur_r = 5.0
cur_ses_id = 2

data_files = data_loader.read_input_metadata("inputs.tsv")
derived_data_dict = data_loader.read_data(data_files)

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




fig = None




def gen_layout_data():
    global cur_r
    title = data_files[cur_ses_id][0]
    # layout = go.Layout({'title': f"{title}: R={cur_r}",

    return (
    {'title': f"{title}",

     'scene': dict(
         yaxis_title='R',
         zaxis_title='No. Employed',
         xaxis_title='Days'),

     # autosize=True,
     'uirevision': 'true',
     'legend_title': f"Legend Title{cur_r}",
     'width': 900,
     'height': 900}
    )

def gen_layout():

    layout = go.Layout(gen_layout_data())
    return layout



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
    cur_r=r_value
    # for key,value in data_files.items():
    #     if value[0] == ses_string:
    #         cur_ses_id = key

    data = gen_fig_data(r_value,derived_data_dict[cur_ses_id])
    fig = go.Figure(data=data)
    fig.update_layout(gen_layout_data())

    return fig

def create_lines_at_r(r_val, cases_dict, color):
    z = [r_val] * len(derived_data_dict[cur_ses_id].day_list)  # constant for this R
    data = go.Scatter3d(
        mode='lines',
        x=derived_data_dict[cur_ses_id].day_list,
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
                   colorscale='Reds'),

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

    html.Div(children='CASES'),

    dcc.Graph(
        id='cases-graph',
        figure=fig
    ),
    dcc.Slider(
        id='my-slider',
        min=derived_data_dict[cur_ses_id].r_min,
        max=derived_data_dict[cur_ses_id].r_max,
        step=0.01,
        value=derived_data_dict[cur_ses_id].r_max
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
