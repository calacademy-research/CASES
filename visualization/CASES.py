#!/usr/bin/env python3
import dash
from derived_data_loader import DerivedDataLoader
from employment_input import EmploymentInput
from r_input import RInput
from pie_fig import PieFig
from cascades_fig import CascadesFig
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import make_response
from flask import Flask
import csv
import io
from sector_colors import SectorColors
import time

from dash.dependencies import Input, Output
import os

app = None


def data_setup():
    global derived_data_dict
    global cur_sector_ids
    global r_date_dict
    global sector_mode
    global graph_colors
    global cur_r
    global derived_data_loader
    global employment_data
    global cur_ses_id

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Initial values
    cur_r = 5.0
    cur_ses_id = 2

    graph_colors = SectorColors()
    sector_mode = False  # summary or sector
    employment_data = EmploymentInput()
    r_date_dict = RInput(employment_data.day_count).r_input_data_dict

    derived_data_loader = DerivedDataLoader(employment_data.sector_names)
    derived_data_dict = derived_data_loader.derived_data_dict
    # cur_sector_ids = list(derived_data_dict[cur_ses_id].sectors_dict.keys())
    cur_sector_ids = ["Farm", "Professional"]


def generate_ses_pulldown_data(metadata_dict):
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


def generate_sector_pulldown_data(derived_data_for_ses):
    retval = []
    for id in derived_data_for_ses.sectors_dict.keys():
        entry_dict = {'label': id, 'value': id}
        retval.append(entry_dict)
    return retval


def create_app():
    # 'https://codepen.io/chriddyp/pen/bWLwgP.css'
    external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css']
    # external_stylesheets = ['http://codepen.io/chriddyp/pen/bWLwgP.css']
    global server
    server = Flask(__name__)

    app = dash.Dash(__name__,
                    prevent_initial_callbacks=True,
                    external_stylesheets=external_stylesheets,
                    server=server)
    return app


def app_setup():
    global app
    app = create_app()
    pie_fig_instance = PieFig(app,
                              "pie-graph",
                              derived_data_dict,
                              derived_data_loader.data_files,
                              employment_data,
                              r_date_dict,
                              graph_colors)
    cascades_fig_instance = CascadesFig(app,
                                        "r-cascades-graph",
                                        derived_data_dict,
                                        derived_data_loader.data_files,
                                        graph_colors)
    pie_fig = pie_fig_instance.generate_initial_figure(cur_r, cur_ses_id, cur_sector_ids)
    cascades_fig = cascades_fig_instance.generate_initial_figure(cur_r, cur_ses_id, cur_sector_ids)

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
        cur_ses_name = derived_data_loader.data_files[pie_fig_instance.cur_ses_id][0]
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

    white_button_style = {'background-color': 'white',
                          }

    green_button_style = {'background-color': 'green',
                          }

    @app.callback(
        dash.dependencies.Output('enable-summary', 'style'),
        [dash.dependencies.Input('enable-sectors', 'n_clicks'),
         dash.dependencies.Input('enable-summary', 'n_clicks')])
    def update_output(n_clicks, n_clicks_2):
        retval = None
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'enable-summary' in changed_id:
            retval = False
        if 'enable-sectors' in changed_id:
            retval = True
        if retval is False:
            return green_button_style
        else:
            return white_button_style

    @app.callback(
        dash.dependencies.Output('enable-sectors', 'style'),
        [dash.dependencies.Input('enable-sectors', 'n_clicks'),
         dash.dependencies.Input('enable-summary', 'n_clicks')])
    def update_output(n_clicks, n_clicks_2):
        retval = None
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'enable-summary' in changed_id:
            retval = False
        if 'enable-sectors' in changed_id:
            retval = True
        if retval is True:
            return green_button_style
        else:
            return white_button_style

    @app.callback(
        dash.dependencies.Output('sector-pulldown', 'disabled'),
        [dash.dependencies.Input('enable-sectors', 'n_clicks'),
         dash.dependencies.Input('enable-summary', 'n_clicks')])
    def update_output(n_clicks, n_clicks_2):
        retval = None
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'enable-summary' in changed_id:
            retval = False
        if 'enable-sectors' in changed_id:
            retval = True

        sector_mode = retval
        pie_fig_instance.sector_mode = retval
        cascades_fig_instance.sector_mode = retval
        return not retval

    def sidebar_div():
        # the style arguments for the sidebar. We use position:fixed and a fixed width
        SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            # "width": "30rem",
            "backgroundColor": "#9c9c9c",
            "padding": "2rem 1rem"
        }
        return (html.Div(id='sidebar',
                         style=SIDEBAR_STYLE,
                         children=[
                             html.P("Change SES"),
                             dcc.Dropdown(
                                 id='ses-pulldown',
                                 options=generate_ses_pulldown_data(derived_data_loader.data_files),
                                 value=cur_ses_id
                             ),

                             html.Div(id='spacer1', style={'height': "3rem"}),
                             html.P("R0"),
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
                                              debounce=True,
                                              value=cur_r,
                                              style={'width': '8rem', 'height': "2rem", "marginLeft": "0rem"},
                                          ),
                                      ]),
                             html.Div([
                                 html.Label("Enable sector display"),

                                 html.Button("Summary", id="enable-summary", n_clicks=0, style=green_button_style),
                                 html.Button("Sectors", id="enable-sectors", n_clicks=0),

                             ]),

                             html.P("Change sector"),
                             dcc.Dropdown(
                                 id='sector-pulldown',
                                 options=generate_sector_pulldown_data(derived_data_dict[cur_ses_id]),
                                 value=cur_sector_ids,
                                 multi=True,
                                 disabled=True,
                                 style={'width': '30rem'},
                                 # options=derived_data_dict[cur_ses_id].sectors.keys(),
                                 # value=cur_sector_id
                             ),

                             html.Div([
                                 # dcc.Link(html.Button('back'), href="/testurl")
                                 html.A(html.Button('Download csv at current R0'), href='download_csv')

                             ])
                         ])
                )

    def page_content_div():
        # the styles for the main content position it to the right of the sidebar and
        # add some padding.
        CONTENT_STYLE = {
            # "marginLeft": "2rem",
            # "marginRight": "2rem",
            # "padding": "2rem 1rem"
        }
        return (html.Div(id="page-content",
                         className="row",
                         style=CONTENT_STYLE,
                         children=[

                             html.Div(style={},
                                      id="first-col",
                                      className="eight columns",
                                      children=[
                                          dcc.Graph(
                                              id='pie-graph',
                                              figure=pie_fig,
                                          )]),
                             html.Div(id="second-col",
                                      className="four columns",

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
                         ])
                )

    @app.callback(Output("loading-output-2", "children"), [Input("loading-input-2", "value")])
    def input_triggers_nested(value):
        time.sleep(1)
        return value

    TOPLEVEL_STYLE = {
        "width": "140rem",
    }

    main_div = html.Div(style=TOPLEVEL_STYLE,
                        className="row",
                        children=[

                            html.Div( className="three columns", children=[sidebar_div()]),
                            html.Div( className="nine columns", children=[page_content_div()])

                        ])

    app.layout = html.Div(children=
    [
        dcc.Input(id="loading-input-2",  style={"visibility": "hidden"},value='Input triggers nested spinner'),
        dcc.Loading(
            id="loading-2",
            fullscreen=True,

            children=[html.Div([html.Div(id="loading-output-2")]),
                      main_div],
            type="circle",
        )
    ]
    )

    # app.layout = main_div


def setup():
    if app is None:
        data_setup()
        app_setup()


staticmethod


def test_static():
    print("Joe static hit")


if __name__ == '__main__':
    print("Running internal server")
    setup()
    app.run_server(debug=True)
else:
    print(f"Running external server: {__name__}")
    setup()

print("exiting.")
