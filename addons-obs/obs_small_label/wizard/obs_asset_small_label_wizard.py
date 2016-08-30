# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd. (<http://acespritech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class asset_small_label_qty(models.Model):
    _name='asset.small.label.qty'

    asset_id = fields.Many2one('account.asset.asset',string='Asset')
    qty =  fields.Float(string='Quantity')
    asset_small_wiz_id = fields.Many2one('obs.asset.small.label.wizard', string='Asset Wizard')


class obs_asset_small_label_wizard(models.Model):
    _name = 'obs.asset.small.label.wizard'

    @api.model
    def default_get(self, fields_list):
        ass_list = []
        res = super(obs_asset_small_label_wizard, self).default_get(fields_list)
        ass_ids = self.env['account.asset.asset'].browse(self._context['active_ids'])
        for ass in ass_ids:
            if ass.asset_code:
                ass_list.append((0, 0, {'asset_id' : ass.id, 'qty': 1}))
        if ass_list:
            res.update({'asset_ids' : ass_list})
        else:
            raise Warning(_('Selected Asset(s) has no Default Code Number!!!.'))
        return res

    asset_ids = fields.One2many('asset.small.label.qty', 'asset_small_wiz_id', string='Asset List')
    barcode_from = fields.Selection([('asset_code', 'Asset Code')], string="Barcode From", default="asset_code")

    @api.multi
    def asset_small_barcode_report_call(self):
        qty = 0.0
        data = self.read()[0]
        datas = {
            'ids': self._ids,
            'model': 'obs.asset.small.label.wizard',
            'form': data,
        }
        for line in self.asset_ids:
            qty += line.qty
        if qty == 0:
            raise Warning(_('Quantity of should be greater Zero(0).'))
        return  self.env['report'].get_action(self, 'obs_small_label.obs_asset_small_label_template',data=datas,)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
