# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api
from openerp.tools.safe_eval import safe_eval


class SaleOrderLineProfessional(models.Model):
    _inherit = 'sale.order.line.professional'

    @api.depends('commission.commission_type', 'sale_line.price_subtotal',
                 'commission.amount_base_type')
    def _compute_amount(self):
        for line_professional in self:
            if (line_professional.commission.commission_type == 'formula' and
                not line_professional.sale_line.product_id.commission_free and
                    line_professional.commission):
                line_professional.amount = 0.0
                formula = line_professional.commission.formula
                results = {'line': line_professional.sale_line}
                safe_eval(formula, results, mode="exec", nocopy=True)
                line_professional.amount += float(results['result'])
            else:
                return super(SaleOrderLineProfessional, line_professional)._compute_amount()
