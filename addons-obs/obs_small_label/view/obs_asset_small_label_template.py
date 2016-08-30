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

from openerp import models, api, _
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from base64 import b64encode
from reportlab.graphics import renderPM
from reportlab.lib import units
from datetime import date


class obs_asset_small_label_template(models.AbstractModel):
    _name = 'report.obs_small_label.obs_asset_small_label_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('obs_small_label.obs_asset_small_label_template')
        docargs = {
            'doc_ids': self.env["obs.asset.small.label.wizard"].browse(data["ids"]),
            'doc_model': report.model,
            'docs': self,
            'get_barcode_data' : self._get_barcode_data,
            'data': data,
        }
        return report_obj.render('obs_small_label.obs_asset_small_label_template', docargs)

    def get_barcode(self, value, width, barWidth = 0.05 * units.inch, fontSize = 12, humanReadable = True):
        # El valor por default de fontSize=60
        barcode = createBarcodeDrawing('Code128', value = value, barWidth = barWidth, fontSize = fontSize, humanReadable = humanReadable)
        drawing_width = width
        barcode_scale = drawing_width / barcode.width
        drawing_height = barcode.height * barcode_scale

        drawing = Drawing(drawing_width, drawing_height)
        drawing.scale(barcode_scale, barcode_scale)
        drawing.add(barcode, name='barcode')
        barcode_encode = b64encode(renderPM.drawToString(drawing, fmt = 'PNG'))
        # Maneja el Codigo de Barras
        barcode_str = '<img style="width:140px;height:20px;"  src="data:image/png;base64,{0} : ">'.format(barcode_encode)
        return barcode_str

    def _get_barcode_data(self, data):
        asset_ids = data['form']['asset_ids']
        asset_list = []
        ass_obj = self.env['asset.small.label.qty']
        asset_obj = self.env['account.asset.asset']
        barcode_number = ''

        for ass in ass_obj.browse(asset_ids):
            for asset in asset_obj.browse(ass.asset_id.id):
                asset_data ={}
                if asset.asset_code and data['form']['barcode_from'] == 'asset_code':
                    barcode_number = asset.asset_code

                else:
                    continue
                barcode_str = self.get_barcode(value = barcode_number, width = 1500)

                for qty in range(int(ass.qty)):
                    special = {
                        u'á': 'a', u'Á': 'A',
                        u'é': 'e', u'É': 'E',
                        u'í': 'i', u'Í': 'I',
                        u'ó': 'o', u'Ó': 'O',
                        u'ú': 'u', u'Ú': 'U',
                        u'ñ': 'n', u'Ñ': 'N',
                    }

                    name = asset.name
                    # Si el nombre contienes unos de los caracteres especiales
                    # lo remplaza con su semejante sin asento.
                    for letter in special.keys():
                        if letter in name:
                            name = name.replace(letter, special[letter])

                    asset_data.update({'asset_code' : barcode_str,
                                        # 'name' : str(asset.name),
                                        'name' : str(name),
                                        'asset_code_name': asset.asset_code})
                    asset_list.append(asset_data)

        return asset_list

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
