# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import models, fields, _
import openerp.addons.decimal_precision as dp


class HrPayslipNewsLine(models.Model):
    """Pay Slip Employee Benefit Line"""

    _name = 'hr.payslip.news.line'
    _description = _(__doc__)

    payslip_id = fields.Many2one(
        'hr.payslip',
        'Payslip',
        required=True,
        ondelete='cascade',
    )

    hr_contract_news_concepts_id = fields.Many2one(
        comodel_name="hr_contract.news.concepts",
        string="Novedad",
        required=True, )

    amount = fields.Float(
        string="Importe",
        required=False,
        digits_compute=dp.get_precision('Payroll'))

    source = fields.Selection(
        [
            ('contract', 'Desde Contrato'),
            ('manual', 'Agregada Manualmente'),
        ],
        readonly=True,
        required=True,
        string='Origen',
        type='char',
        default='manual',
    )
    reference = fields.Char('Referencia')
