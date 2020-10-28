#!/usr/bin/env python3
import dash
from data_loader import DataLoader
from pie_fig import PieFig
from cascades_fig import CascadesFig
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import make_response
import csv
import io

cur_r = 5.0
cur_ses_id = 2

loader = DataLoader()
derived_data_dict = loader.derived_data_dict

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


def create_app():
    external_stylesheets = [dbc.themes.BOOTSTRAP]
    # external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__,
                    prevent_initial_callbacks=True,
                    external_stylesheets=external_stylesheets)
    return app


app = create_app()

pie_fig_instance = PieFig(app,
                          "pie-graph",
                          derived_data_dict,
                          loader.data_files)
cascades_fig_instance = CascadesFig(app,
                                    "r-cascades-graph",
                                    derived_data_dict,
                                    loader.data_files)
pie_fig = pie_fig_instance.generate_initial_figure(cur_r, cur_ses_id)
cascades_fig = cascades_fig_instance.generate_initial_figure(cur_r, cur_ses_id)


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


@app.server.route('/download_csv')
def download_csv():
    cur_ses_name = loader.data_files[pie_fig_instance.cur_ses_id][0]
    cur_r = pie_fig_instance.cur_r
    cur_data_dict = derived_data_dict[pie_fig_instance.cur_ses_id]
    filename = f"{cur_ses_name}_{cur_r}.csv"
    data = [["day", "removed", "unemployed"]]
    for cur_day in range(0, cur_data_dict.day_count):
        removed = cur_data_dict.cases_removed[cur_r][cur_day]
        unemployed = cur_data_dict.cases_unemployed[cur_r][cur_day]

        data.append([cur_day + 1, removed, unemployed])

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(data)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    return output


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
                     options=generate_pulldown_data(loader.data_files),
                     value=loader.data_files[cur_ses_id][0]
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
                          ]),
                 html.Div([
                     # dcc.Link(html.Button('back'), href="/testurl")
                     html.A(html.Button('Download csv at current R'), href='download_csv')

                 ])
             ],

             ),

    html.Div(id="page-content",
             className="row",
             style=CONTENT_STYLE,
             children=[
                 html.Div(style={},
                          children=[
                              dcc.Graph(
                                  id='pie-graph',
                                  figure=pie_fig,
                              )]),
                 html.Div(id="second-col",

                          children=[
                              html.Div(id="top_in_col",
                                       style={},
                                       children=[
                                           dcc.Graph(
                                               id='r-cascades-graph',
                                               figure=cascades_fig,
                                           )
                                       ]),
                              html.Div(id="bottom_in_col",
                                       style={
                                              },

                                       )

                          ])
             ]),

])

if __name__ == '__main__':
    app.run_server(debug=True)
