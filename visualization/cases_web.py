#!/usr/bin/env python3
import dash
import data_loader
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

fig = None
cur_r = 5.0
cur_ses_id = 2

data_files = data_loader.read_input_metadata("inputs.tsv")
derived_data_dict = data_loader.read_data(data_files)
fig = None


def generate_pulldown_data(metadata_dict):
    # Format:
    # [
    #     {'label': 'New York City', 'value': 'NYC'},
    #     {'label': 'Montreal', 'value': 'MTL'},
    #     {'label': 'San Francisco', 'value': 'SF'}
    # ]
    retval = []
    for id, entry in metadata_dict.items():
        entry_dict = {'label': entry[0], 'value': id}
        retval.append(entry_dict)
    return retval


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
         # 'legend_title': f"Legend Title{cur_r}",
         'legend': dict(
             yanchor="top",
             y=0.99,
             xanchor="left",
             x=0.01
         ),
         'width': 900,
         'height': 900}
    )


def gen_layout():
    layout = go.Layout(gen_layout_data())
    return layout


def create_app():
    external_stylesheets = [dbc.themes.BOOTSTRAP]
    # external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    return app


app = create_app()
#  Causes a circular dependancy. Works fine. Suppressing errors (turning debug off)
# makes this work.
# solution here: https://community.plotly.com/t/synchronize-components-bidirectionally/14158/11
# does not work; it sees the deeper cycle and ignores. (note; the code in this example
# does not run - requires "groups" from dash_extensions using new syntax.
@app.callback(
    dash.dependencies.Output('r-input', 'value'),
    [dash.dependencies.Input('r-slider', 'value')])
def update_input_from_slider(new_r):
    return new_r

@app.callback(
    dash.dependencies.Output('r-slider', 'value'),
    [dash.dependencies.Input('r-input', 'value')])
def update_sider_from_input(new_r):
    return new_r

@app.callback(
    dash.dependencies.Output("cases-graph", "figure"),
    [dash.dependencies.Input('ses-pulldown', 'value'),
     dash.dependencies.Input('r-slider', 'value'),
     dash.dependencies.Input('r-input', 'value')])
def update_output(new_ses_id, r_slider,r_input):
    global cur_ses_id
    global cur_r
    ctx = dash.callback_context
    # Joe use ctx to figure out what got hit. update r val accordingly.

    triggered_item = ctx.triggered[0]['prop_id']
    # 'r-slider.value' 'r-input.value'
    if triggered_item == 'r-input.value':
        cur_r = float(r_input)
    if triggered_item == 'r-slider.value':
        cur_r = float(r_slider)
    if isinstance(new_ses_id, int):
        cur_ses_id = new_ses_id
    # for key,value in data_files.items():
    #     if value[0] == ses_string:
    #         cur_ses_id = key

    data = gen_fig_data(cur_r, derived_data_dict[cur_ses_id])
    fig = go.Figure(data=data)
    fig.update_layout(gen_layout_data())

    return fig


def create_lines_at_r(r_val, cases_dict, color, name):
    z = [r_val] * len(derived_data_dict[cur_ses_id].day_list)  # constant for this R
    data = go.Scatter3d(
        mode='lines',
        name=name,
        x=derived_data_dict[cur_ses_id].day_list,
        y=z,
        z=list(cases_dict[r_val]),

        line=dict(
            color=color,
            width=7
        )
    )
    return data


def gen_fig_data(r_value, ses_dict):
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

        create_lines_at_r(r_value, ses_dict.cases_removed, 'black', "Removed from workpool"),
        create_lines_at_r(r_value, ses_dict.cases_unemployed, 'green', "Unemployed")
    ]


data = gen_fig_data(cur_r, derived_data_dict[cur_ses_id])
fig = go.Figure(data=data, layout=gen_layout())

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "25rem",
    "background-color": "#9c9c9c",
    "padding": "2rem 1rem"
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "25rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
app.layout = html.Div(children=[

    html.Div(children='CASES'),
    html.Div(id='sidebar',
             style=SIDEBAR_STYLE,
             children=[
                 html.P("Change SES"),
                 dcc.Dropdown(
                     id='ses-pulldown',
                     options=generate_pulldown_data(data_files),
                     value=data_files[cur_ses_id][0]
                 ),
                 html.Div(id='spacer1', style={'height': "3rem"}),
                 html.P("R value"),
                 html.Div(id='rpickers',
                          className="row",
                          style={"padding": "0rem 0rem"},
                          children=[
                              html.Div(style={'width': "20rem",},
                                       children=[
                              dcc.Slider(
                                  id='r-slider',
                                  min=derived_data_dict[cur_ses_id].r_min,
                                  max=derived_data_dict[cur_ses_id].r_max,
                                  step=0.01,
                                  value=cur_r
                              )]),
                              dcc.Input(
                                  id="r-input",
                                  type="number",
                                  min=derived_data_dict[cur_ses_id].r_min,
                                  max=derived_data_dict[cur_ses_id].r_max,
                                  step=0.01,
                                  value=cur_r,
                                  style={'width': '4rem', 'height': "2rem","margin-left": "0rem"},
                              ),
                          ])
             ],

             ),

    html.Div(id="page-content",
             style=CONTENT_STYLE,
             children=[
                 dcc.Graph(
                     id='cases-graph',
                     figure=fig
                 ),
             ]),

])

if __name__ == '__main__':
    app.run_server(debug=True)
