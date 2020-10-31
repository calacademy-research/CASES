import dash
import plotly.graph_objects as go
from fig_utils import FigUtilsMixin


# cur_r and cur_ses_id are set when we call an generate_initial_figure
# and updated by callbacks.
class PieFig(FigUtilsMixin):
    def __init__(self, app, id, derived_data_dict, data_files):
        self.derived_data_dict = derived_data_dict
        self.app = app
        self.data_files = data_files
        self.cur_sector_ids = None
        self.cur_r = None
        self.cur_ses_id = None
        self.sector_mode = False
        app.callback(
            dash.dependencies.Output(id, "figure"),
            [dash.dependencies.Input('ses-pulldown', 'value'),
             dash.dependencies.Input('sector-pulldown', 'value'),
             dash.dependencies.Input('r-slider', 'value'),
             dash.dependencies.Input('r-input', 'value'),
             dash.dependencies.Input('enable-sectors', 'n_clicks'),
             dash.dependencies.Input('enable-summary', 'n_clicks')
             ])(self.update_pie_fig)

    # Initial call
    def generate_initial_figure(self, cur_r, cur_ses_id, cur_sector_ids):
        self.cur_r = cur_r
        self.cur_ses_id = cur_ses_id
        self.cur_sector_ids = cur_sector_ids
        return go.Figure(data=self.gen_pie_fig_data(),
                         layout=self.gen_pie_fig_layout())

    def refresh_pie_fig(self):
        pie_fig = go.Figure(data=self.gen_pie_fig_data())
        pie_fig.update_layout(self.gen_pie_fig_layout())
        return pie_fig

    # callback
    def update_pie_fig(self, new_ses_id, cur_sector_ids, r_slider, r_input, n_clicks_sectors, n_clicks_summary):
        self.update_ses_and_r(new_ses_id, cur_sector_ids, r_slider, r_input)
        return self.refresh_pie_fig()

    def gen_pie_fig_layout_data(self):
        title = self.data_files[self.cur_ses_id][0]
        # layout = go.Layout({'title': f"{title}: R={cur_r}",
        cur_ses_dict = self.derived_data_dict[self.cur_ses_id]

        scene = {}
        if not self.sector_mode:
            pop_min = cur_ses_dict.pop_min
            pop_max = cur_ses_dict.pop_max
            scene = dict(
                yaxis_title='R',
                zaxis_title='No. Employed',
                xaxis_title='Days',
                zaxis=dict(
                    autorange=False,
                    range=[pop_min, pop_max],
                )
            )
        else:
            scene = dict(
                yaxis_title='R',
                zaxis_title='No. Employed',
                xaxis_title='Days',
                zaxis=dict(
                    autorange=True
                )
            )

        return (
            {'title': f"{title}",

             'scene': scene,

             # autosize=True,
             'uirevision': 'true',
             # 'legend_title': f"Legend Title{cur_r}",
             'legend': dict(
                 yanchor="top",
                 y=0.99,
                 xanchor="left",
                 x=0.01
             ),
             'width': 800,
             'height': 800
             }
        )

    def create_lines_at_r(self, r_val, cases_dict, color, name):
        z = [r_val] * len(self.derived_data_dict[self.cur_ses_id].day_list)  # constant for this R
        if self.sector_mode:
            z_val = list(cases_dict[r_val])
        else:
            # Fix this, needs multiplexing. Joe.
            z_val = list(cases_dict[r_val])

            # z_val = self.derived_data_dict[self.cur_ses_id].sectors_dict[cur_sector_id][r_val]
        data = go.Scatter3d(
            mode='lines',
            name=name,
            x=self.derived_data_dict[self.cur_ses_id].day_list,
            y=z,
            z=z_val,

            line=dict(
                color=color,
                width=7
            )
        )
        return data

    def gen_pie_fig_layout(self):
        layout = go.Layout(self.gen_pie_fig_layout_data())
        return layout

    def gen_sector_display(self, ses_dict):
        retval = []

        for cur_sector_id in self.cur_sector_ids:
            unemployed_z = self.derived_data_dict[self.cur_ses_id].sectors_df[cur_sector_id]

            retval.append(
                go.Surface(z=unemployed_z,
                           y=ses_dict.unemployed_surface_df.index,
                           x=ses_dict.unemployed_surface_df.columns,
                           hoverinfo='none',
                           opacity=0.6,
                           colorscale='Greens'))

        return retval

    def gen_surfaces(self, ses_dict):
        retval = []
        if not self.sector_mode:
            unemployed_z = ses_dict.unemployed_surface_df.values

            retval.append(go.Surface(z=unemployed_z,
                                     y=ses_dict.unemployed_surface_df.index,
                                     x=ses_dict.unemployed_surface_df.columns,
                                     hoverinfo='none',
                                     opacity=0.6,
                                     colorscale='Greens',
                                     colorbar=dict(
                                         title="Total<br>employed",
                                         thickness=10,
                                         tickmode="auto",
                                         # nticks=5,
                                         x=1.20, )
                                     ))
            retval.append(go.Surface(z=ses_dict.removed_surface_df.values,
                                     y=ses_dict.removed_surface_df.index,
                                     x=ses_dict.removed_surface_df.columns,
                                     hoverinfo='none',
                                     opacity=0.6,
                                     colorscale='Greys',
                                     colorbar=dict(
                                         title="Total<br>removed",
                                         x=1.02,
                                         tickmode="auto",
                                         # nticks=5,
                                         thickness=10, )
                                     ))

            retval.append(
                self.create_lines_at_r(self.cur_r, ses_dict.cases_removed, 'black', "Removed from workpool"))
            retval.append(self.create_lines_at_r(self.cur_r, ses_dict.cases_unemployed, 'green', "Unemployed"))
        else:
            surfaces = self.gen_sector_display(ses_dict)
            if surfaces is not None:
                retval.extend(surfaces)

        return retval

    def gen_pie_fig_data(self):
        # x = days
        # y = R
        # z = pop value
        ses_dict = self.derived_data_dict[self.cur_ses_id]
        return self.gen_surfaces(ses_dict)
