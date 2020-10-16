#!/usr/bin/env python3
import dash
import data_loader
from pie_fig import PieFig
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


pie_fig = None
cascades_fig = None
cur_r = 5.0
cur_ses_id = 2

data_files = data_loader.read_input_metadata("inputs.tsv")
derived_data_dict = data_loader.read_data(data_files)


def update_ses_and_r(new_ses_id, r_slider, r_input):
    global cur_r
    global cur_ses_id
    ctx = dash.callback_context
    triggered_item = ctx.triggered[0]['prop_id']
    # 'r-slider.value' 'r-input.value'
    if triggered_item == 'r-input.value':
        cur_r = float(r_input)
    if triggered_item == 'r-slider.value':
        cur_r = float(r_slider)
    if isinstance(new_ses_id, int):
        cur_ses_id = new_ses_id

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



def gen_cascades_fig_layout():
    global cur_r
    title = data_files[cur_ses_id][0]

    return go.Layout(
        {'title': f"{title}",

         'scene': dict(
             yaxis_title='No. Employed',
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


def create_app():
    external_stylesheets = [dbc.themes.BOOTSTRAP]
    # external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    return app


app = create_app()

pie_fig_instance = PieFig(app,derived_data_dict,data_files,cur_r,cur_ses_id)


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
    dash.dependencies.Output("r-cascades-graph", "figure"),
    [dash.dependencies.Input('ses-pulldown', 'value'),
     dash.dependencies.Input('r-slider', 'value'),
     dash.dependencies.Input('r-input', 'value')])
def update_cascades_fig(new_ses_id, r_slider, r_input):
    global cur_ses_id
    global cur_r
    update_ses_and_r(new_ses_id, r_slider, r_input)

    cascades_fig = go.Figure(data=gen_cascades_fig_data(cur_r, derived_data_dict[cur_ses_id]))
    cascades_fig.update_layout(gen_cascades_fig_layout())

    return cascades_fig








def gen_cascades_fig_data(r_value, ses_dict):
    global cur_r
    data = [go.Scatter(
            mode='lines',
            name="removed",
            x=derived_data_dict[cur_ses_id].day_list,
            y=list(ses_dict.cases_removed[cur_r]),

            line=dict(
                color='black',
                width=1
            )
        ),
        go.Scatter(
            mode='lines',
            name="Unemployed",
            x=derived_data_dict[cur_ses_id].day_list,
            y=list(ses_dict.cases_unemployed[cur_r]),

            line=dict(
                color='black',
                width=1
            )
        )
    ]

    return data


pie_fig = go.Figure(data=pie_fig_instance.gen_pie_fig_data(cur_r, derived_data_dict[cur_ses_id]),
                    layout=pie_fig_instance.gen_pie_fig_layout())
cascades_fig = go.Figure(data=gen_cascades_fig_data(cur_r, derived_data_dict[cur_ses_id]),
                         layout=gen_cascades_fig_layout())

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
                              html.Div(style={'width': "20rem", },
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
                                  style={'width': '4rem', 'height': "2rem", "margin-left": "0rem"},
                              ),
                          ])
             ],

             ),

    html.Div(id="page-content",
             style=CONTENT_STYLE,
             children=[
                 dcc.Graph(
                     id='pie-graph',
                     figure=pie_fig
                 ),
                 dcc.Graph(
                     id='r-cascades-graph',
                     figure=cascades_fig
                 )
             ]),

])

if __name__ == '__main__':
    app.run_server(debug=True)
