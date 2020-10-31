import dash
import plotly.graph_objects as go
from fig_utils import FigUtilsMixin


class CascadesFig(FigUtilsMixin):
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
             dash.dependencies.Input('r-input', 'value')])(self.update_cascades_fig)

    # initial call
    def generate_initial_figure(self, cur_r, cur_ses_id, cur_sector_ids):
        self.cur_sector_ids = cur_sector_ids
        self.cur_r = cur_r
        self.cur_ses_id = cur_ses_id
        fig = go.Figure(data=self.gen_cascades_fig_data(),
                        layout=self.gen_cascades_fig_layout())

        return fig

    # callback
    def update_cascades_fig(self, new_ses_id, new_sector_ids,r_slider, r_input):
        self.update_ses_and_r(new_ses_id, new_sector_ids, r_slider, r_input)

        cascades_fig = go.Figure(data=self.gen_cascades_fig_data())
        cascades_fig.update_layout(self.gen_cascades_fig_layout())

        return cascades_fig

    def gen_cascades_fig_layout(self):
        # title = self.data_files[self.cur_ses_id][0]
        cur_ses_dict = self.derived_data_dict[self.cur_ses_id]

        layout = go.Layout(
            {
                'yaxis': dict(
                    range=[cur_ses_dict.pop_min, cur_ses_dict.pop_max],

                ),
                'scene': dict(
                    yaxis_title='No. Employed',
                    xaxis_title='Days',
                    aspectmode='manual',
                    xaxis=dict(
                        autorange=False,

                    ),
                    yaxis=dict(
                        autorange=False,
                        range=[cur_ses_dict.pop_min, cur_ses_dict.pop_max],
                    )),

                'uirevision': 'true',
                # 'legend_title': f"Legend Title{cur_r}",
                'legend': dict(
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0
                ),
                'width': 400,
                'height': 400
            }
        )

        return layout

    def gen_cascades_fig_data(self):
        ses_dict = self.derived_data_dict[self.cur_ses_id]
        data = [go.Scatter(
            mode='lines',
            name="removed",
            x=self.derived_data_dict[self.cur_ses_id].day_list,
            y=list(ses_dict.cases_removed[self.cur_r]),
            line=dict(
                color='black',
                width=1
            )
        ),
            go.Scatter(
                mode='lines',
                name="Unemployed",
                x=self.derived_data_dict[self.cur_ses_id].day_list,
                y=list(ses_dict.cases_unemployed[self.cur_r]),

                line=dict(
                    color='green',
                    width=1
                )
            )
        ]

        return data
