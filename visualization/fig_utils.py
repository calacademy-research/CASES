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
class FigUtilsMixin:

    def update_ses_and_r(self,new_ses_id, new_sector_ids,r_slider, r_input,sectors_enabled):
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

        self.sector_mode = sectors_enabled



