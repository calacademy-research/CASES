import dash
import plotly.graph_objects as go
from fig_utils import FigUtilsMixin


class CascadesFig(FigUtilsMixin):
    def __init__(self, app, id, derived_data_dict, data_files, sector_colors):
        self.derived_data_dict = derived_data_dict
        self.app = app
        self.data_files = data_files
        self.cur_sector_ids = None
        self.cur_r = None
        self.cur_ses_id = None
        self.sector_mode = False
        self.sector_colors = sector_colors

        app.callback(
            dash.dependencies.Output(id, "figure"),
            [dash.dependencies.Input('ses-pulldown', 'value'),
             dash.dependencies.Input('sector-pulldown', 'value'),
             dash.dependencies.Input('r-slider', 'value'),
             dash.dependencies.Input('r-input', 'value'),
             dash.dependencies.Input('enable-sectors', 'n_clicks'),
             dash.dependencies.Input('enable-summary', 'n_clicks')
             ])(self.update_cascades_fig)

    # initial call
    def generate_initial_figure(self, cur_r, cur_ses_id, cur_sector_ids):
        self.cur_sector_ids = cur_sector_ids
        self.cur_r = cur_r
        self.cur_ses_id = cur_ses_id
        fig = go.Figure(data=self.gen_cascades_fig_data(),
                        layout=self.gen_cascades_fig_layout())

        return fig

    # callback
    def update_cascades_fig(self, new_ses_id, new_sector_ids, r_slider, r_input, n_clicks_sectors, n_clicks_summary):
        self.update_ses_and_r(new_ses_id, new_sector_ids, r_slider, r_input)

        cascades_fig = go.Figure(data=self.gen_cascades_fig_data())
        cascades_fig.update_layout(self.gen_cascades_fig_layout())

        return cascades_fig

    def gen_cascades_fig_layout(self):
        cur_ses_dict = self.derived_data_dict[self.cur_ses_id]
        scene = {}
        yaxis = {}
        legend = {}
        if not self.sector_mode:
            scene = dict(
                yaxis_title='No. Employed',
                xaxis_title='Days',
                aspectmode='manual',
                xaxis=dict(
                    autorange=False,
                ))

            yaxis = dict(
                range=[cur_ses_dict.pop_min, cur_ses_dict.pop_max],
            )
            legend = dict(
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            )
            width = 400
        else:
            scene = dict(
                yaxis_title='No. Employed',
                xaxis_title='Days',
                yaxis=dict(
                    autorange=True,
                ))
            yaxis = dict(
                autorange=True,
            )
            legend = dict(
                yanchor="bottom",
                y=0,
                xanchor="right",
                x=1.8
            )
            width = 520

        layout = go.Layout(
            {
                'yaxis': yaxis,
                'scene': scene,

                'uirevision': 'true',
                # 'legend_title': f"Legend Title{cur_r}",
                'legend': legend,
                'width': width,
                'height': 400
            }
        )

        return layout

    def gen_sector_cascades(self):
        retval = []

        for cur_sector_id in self.cur_sector_ids:

            y = self.derived_data_dict[self.cur_ses_id].sectors_dict[cur_sector_id][self.cur_r]
            retval.append(go.Scatter(
                mode='lines',
                name=cur_sector_id,
                x=self.derived_data_dict[self.cur_ses_id].day_list,
                y=y,
                line=dict(
                    color=self.sector_colors.trace_color_mappings[cur_sector_id],
                    width=1
                )))
        return retval

    def gen_cascades(self, ses_dict):
        retval = []
        if not self.sector_mode:
            retval.append(go.Scatter(
                mode='lines',
                name="COVID-19 sick or dead",
                x=self.derived_data_dict[self.cur_ses_id].day_list,
                y=list(ses_dict.cases_removed[self.cur_r]),
                line=dict(
                    color='black',
                    width=1
                )))
            retval.append(go.Scatter(
                mode='lines',
                name="Unemployed",
                x=self.derived_data_dict[self.cur_ses_id].day_list,
                y=list(ses_dict.cases_unemployed[self.cur_r]),

                line=dict(
                    color='green',
                    width=1
                )))

        else:
            cascades = self.gen_sector_cascades()
            if cascades is not None:
                retval.extend(cascades)
        return retval

    def gen_cascades_fig_data(self):
        ses_dict = self.derived_data_dict[self.cur_ses_id]
        return self.gen_cascades(ses_dict)
