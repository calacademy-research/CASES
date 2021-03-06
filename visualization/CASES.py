#!/usr/bin/env python3
'''
CASES - Economic Cascades and the Costs of a Business-as-Usual Approach to COVID-19
Copyright (C) 2021 California Academy of Sciences

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import dash
from derived_data_loader import DerivedDataLoader
from employment_input import EmploymentInput
from r_input import RInput
from pie_fig import PieFig
from cascades_fig import CascadesFig
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Response
import base64
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
    external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css']
    global server
    server = Flask(__name__)

    app = dash.Dash(__name__,
                    title='CASES',
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
        filename = filename.replace(", ", "-")
        filename = filename.replace(",", "-")
        filename = filename.replace(" ", "_")

        # filename = f"temp.csv" # use md5 so no collision
        data = [["day", "removed", "unemployed"]]
        for cur_day in range(0, cur_data_dict.day_count):
            removed = cur_data_dict.cases_removed[cur_r][cur_day]
            unemployed = cur_data_dict.cases_unemployed[cur_r][cur_day]

            data.append([cur_day + 1, removed, unemployed])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(data)
        csv_string = output.getvalue()

        return Response(
            csv_string,
            mimetype="text/csv",
            headers={
                "Content-disposition": "attachment; filename=" + filename
            }
        )

    white_button_style = {'background-color': 'white',
                          }

    green_button_style = {'background-color': 'green',
                          }

    @app.callback(
        [dash.dependencies.Output('enable-summary', 'style'),
         dash.dependencies.Output('sectors-enabled', 'children')],

        [dash.dependencies.Input('enable-sectors', 'n_clicks'),
         dash.dependencies.Input('enable-summary', 'n_clicks')])
    def update_output(n_clicks, n_clicks_2):
        enable_sectors = None
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'enable-summary' in changed_id:
            enable_sectors = False
        if 'enable-sectors' in changed_id:
            enable_sectors = True
        assert enable_sectors is not None, "No value set for sector mode"

        pie_fig_instance.sector_mode = enable_sectors
        cascades_fig_instance.sector_mode = enable_sectors
        pie_fig_instance.refresh_pie_fig()
        cascades_fig_instance.refresh_cascades_fig()


        if enable_sectors is False:
            return green_button_style,enable_sectors
        else:
            return white_button_style,enable_sectors

    @app.callback(
        dash.dependencies.Output('enable-sectors', 'style'),
        [dash.dependencies.Input('enable-sectors', 'n_clicks'),
         dash.dependencies.Input('enable-summary', 'n_clicks')])
    def update_output(n_clicks, n_clicks_2):
        enable_sectors = None
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'enable-summary' in changed_id:
            enable_sectors = False
        if 'enable-sectors' in changed_id:
            enable_sectors = True
        assert enable_sectors is not None, "No value set for sector mode"

        if enable_sectors is True:
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

        return not retval

    def sidebar_div():
        # the style arguments for the sidebar. We use position:fixed and a fixed width
        SIDEBAR_STYLE = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "backgroundColor": "#F5F5F5",
            "padding": "2rem 1rem"
        }
        denison_logo_image = base64.b64encode(open("denison-logo.png", 'rb').read()).decode('ascii')
        cas_logo_image = base64.b64encode(open("cas-logo.png", 'rb').read()).decode('ascii')
        github_logo = base64.b64encode(open("GitHub_Logo.png", 'rb').read()).decode('ascii')
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

                             ),

                             html.Div([
                                 html.A(html.Button('Download csv at current R0'), href='download_csv')

                             ]),

                             html.Div(id='logos',
                                      style={"position": "fixed",
                                             "bottom": "0"},
                                      children=[
                                          html.A(href='https://github.com/calacademy-research/CASES',
                                                 children=[
                                                     html.Img(style={"width": "10rem",
                                                                     "margin-left": "10rem",
                                                                     "margin-right": "auto"},
                                                              src='data:image/png;base64,{}'.format(github_logo))
                                                 ]),
                                          html.P(""),
                                          html.A(href='https://www.calacademy.org',
                                                 children=[
                                                     html.Img(style={"width": "30rem"},
                                                              src='data:image/png;base64,{}'.format(cas_logo_image))
                                                 ]),
                                          html.P(""),
                                          html.A(href='https://denison.edu/',
                                                 children=[
                                                     html.Img(style={"width": "30rem",
                                                                     "margin-bottom": "3rem"},
                                                              src='data:image/png;base64,{}'.format(denison_logo_image))
                                                 ])
                                      ]
                                      )

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
                             html.Div(id="first-col",
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
                                      ]),
                             html.Div(id='sectors-enabled', style={'display': 'none'})
                         ])
                )

    @app.callback(Output("loading-output-2", "children"), [Input("loading-input-2", "value")])
    def input_triggers_nested(value):
        time.sleep(1)
        return value

    TOPLEVEL_STYLE = {
        "width": "160rem"

    }

    main_div = html.Div(style=TOPLEVEL_STYLE,
                        className="row",
                        children=[
                            html.Div(className="three columns", children=[sidebar_div()]),
                            html.Div(className="nine columns",
                                     style={'overflow': 'auto',
                                            'overflow': 'visible'},
                                     children=[page_content_div()])
                        ])

    app.layout = html.Div(
        children=
        [
            dcc.Input(id="loading-input-2",
                      style={"visibility": "hidden"},
                      value='Input triggers nested spinner'),
            dcc.Loading(
                id="loading-2",
                fullscreen=True,

                children=[html.Div([html.Div(id="loading-output-2")]),
                          main_div],
                type="circle",
            )
        ]
    )


def setup():
    if app is None:
        data_setup()
        app_setup()

copyright_string = '''
 CASES  Copyright (C) 2021 California Academy of Sciences 
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions. See included license for details.
'''
print(copyright_string)

if __name__ == '__main__':
    print("Running internal server")
    setup()
    app.run_server(debug=True)
else:
    print(f"Running external server: {__name__}")
    setup()

print("exiting.")
