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

from openerp import api, models, fields


PAYS_PER_YEAR = {
    'annually': 1,
    'semi-annually': 2,
    'fortnightly': 24,
    'quaterly': 4,
    'bi-monthly': 6,
    'monthly': 12,
    'semi-monthly': 24,
    'bi-weekly': 26,
    'weekly': 52,
    'daily': 365,
}


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    news_line_ids = fields.One2many(
        'hr.payslip.news.line',
        'payslip_id',
        'Novedades',
        readonly=True, states={'draft': [('readonly', False)]},
    )
    pays_per_year = fields.Integer(
        compute='_get_pays_per_year',
        string='Number of pays per year', readonly=True,
        store=True,
        help="Field required to compute news based on an annual "
        "amount."
    )

    @api.depends('contract_id')
    def _get_pays_per_year(self):
        self.pays_per_year = PAYS_PER_YEAR.get(
            self.contract_id.schedule_pay, False)

    @api.multi
    def _search_news(self):
        """
        Search employee news to be added on the payslip

        This method is meant to be inherited in other modules
        in order to add news from other sources.
        """
        self.ensure_one()
        return self.contract_id.hr_contract_news_ids

    @api.multi
    def button_compute_news(self):
        self.compute_news()

    @api.one
    def compute_news(self):
        """
        Compute the employee news on the payslip.

        This method can be called from inside a salary rule.

        Exemple
        -------
        payslip.compute_news()

        This is required when the news are based on the value
        of one or more salary rules.

        The module hr_employee_benefit_percent implements that
        functionnality.
        """
        for news_line in self.news_line_ids:
            if news_line.source == 'contract':
                news_line.unlink()

        news = self._search_news()

        # Compute the amounts for each employee benefit
        news.compute_amounts(self)

        # If the method is called from a salary rule.
        # It is important to call refresh() so that the record set
        # will contain the news computed above.
        self.refresh()
