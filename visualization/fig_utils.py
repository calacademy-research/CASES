import dash
from array import array
class FigUtilsMixin:

    def update_ses_and_r(self,new_ses_id, new_sector_ids,r_slider, r_input):
        self.cur_r
        self.cur_ses_id
        ctx = dash.callback_context
        triggered_item = ctx.triggered[0]['prop_id']
        # 'r-slider.value' 'r-input.value'
        if triggered_item == 'r-input.value':
            self.cur_r = float(r_input)
        if triggered_item == 'r-slider.value':
            self.cur_r = float(r_slider)
        if isinstance(new_ses_id, int):
            self.cur_ses_id = new_ses_id
        if isinstance(new_sector_ids, list):
            self.cur_sector_ids = new_sector_ids