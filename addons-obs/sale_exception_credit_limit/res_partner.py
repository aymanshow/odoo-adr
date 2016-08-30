# -*- coding: utf-8 -*-
from openerp import models, api, fields

class sale_order(models.Model):
    _inherit = "res.partner"

    @api.one
    def _check_available_credit(self):
        self.ensure_one()
        # We sum fensure_one()rom all the sale orders that are aproved, the sale order
        # lines that are not yet invoiced
        domain = [('order_id.partner_id', '=', self.id),
                  ('invoiced', '=', False),
                  ('order_id.state', 'not in', ['draft', 'cancel', 'sent'])]
        order_lines = self.env['sale.order.line'].search(domain)
        none_invoiced_amount = sum(order_lines.mapped('price_subtotal'))

        # We sum from all the invoices that are in draft the total amount
        domain = [
            ('partner_id', '=', self.id), ('state', '=', 'draft')]
        draft_invoices = self.env['account.invoice'].search(domain)
        draft_invoices_amount = sum(draft_invoices.mapped('amount_total'))

        self.available_credit = self.credit_limit - \
            self.credit - \
            none_invoiced_amount - draft_invoices_amount

    available_credit = fields.Float(string="Crédito Disponible", compute="_check_available_credit",
                             readonly=True, store=False, required=False, )