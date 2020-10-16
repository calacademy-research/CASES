import dash
import plotly.graph_objects as go
from fig_utils import FigUtilsMixin

class CascadesFig(FigUtilsMixin):
    def __init__(self,app,derived_data_dict,data_files,cur_r,cur_ses_id):
        self.derived_data_dict = derived_data_dict
        self.app = app
        self.cur_r = cur_r
        self.cur_ses_id = cur_ses_id
        self.data_files = data_files
        app.callback(
            dash.dependencies.Output("r-cascades-graph", "figure"),
            [dash.dependencies.Input('ses-pulldown', 'value'),
             dash.dependencies.Input('r-slider', 'value'),
             dash.dependencies.Input('r-input', 'value')])(self.update_cascades_fig)

    # callback
    def update_cascades_fig(self,new_ses_id, r_slider, r_input):

        self.update_ses_and_r(new_ses_id, r_slider, r_input)

        cascades_fig = go.Figure(data=self.gen_cascades_fig_data(self.cur_r, self.derived_data_dict[self.cur_ses_id]))
        cascades_fig.update_layout(self.gen_cascades_fig_layout())

        return cascades_fig

    def gen_cascades_fig_layout(self):
        title = self.data_files[self.cur_ses_id][0]

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

    def gen_cascades_fig_data(self,r_value, ses_dict):
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
                    color='black',
                    width=1
                )
            )
        ]

        return data
