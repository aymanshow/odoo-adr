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

from openerp import api, fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    employee_news_ids = fields.Many2many(
        'hr_contract.news.concepts',
        'salary_rule_contract_news_rel',
        'salary_rule_id', 'news_id', 'Salary Rules',
    )

    @api.multi
    def sum_news(self, payslip, **kwargs):
        """
        Method used to sum the employee news computed on the payslip

        Because there are many possible parameters and that the module
        needs to be inherited easily, arguments are passed through kwargs

        :param codes: The type of new over which to sum
        :type codes: list of string or single string

        :param employer: If True, sum over the employer contribution.
        If False, sum over the employee contribution

        Exemple
        -------
        payslip.compute_news(payslip, employer=True)
        Will return the employer contribution for the pay period
        """
        self.ensure_one()

        news = self._filter_news(payslip, **kwargs)

        res = sum(new.amount for new in news)

        return res

    @api.multi
    @api.returns('hr.payslip.news.line')
    def _filter_news(self, payslip, codes=False, **kwargs):
        """ Filter the new records on the payslip
        :rtype: record set of hr.payslip.new.line
        """
        self.ensure_one()

        news = payslip.news_line_ids

        if codes:
            if isinstance(codes, str):
                codes = [codes]

            return news.filtered(
                lambda b: b.hr_contract_news_concepts_id.code in codes)

        # If the salary rule is linked to no new category,
        # by default it accepts every categories.
        if self.employee_news_ids:
            return news.filtered(
                lambda b: b.hr_contract_news_concepts_id in self.employee_news_ids)

        return news
