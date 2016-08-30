# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.professionals.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.order_line:
                record.commission_total += sum(x.amount for x in line.professionals)

    commission_total = fields.Float(
        string="Commissions", compute="_compute_commission_total",
        store=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _default_professionals(self):
        professionals = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for professional in partner.professionals:
                vals = {
                    'professional': professional.id,
                    'commission': professional.commission.id,
                }
                vals['display_name'] = self.env['sale.order.line.professional']\
                    .new(vals).display_name
                professionals.append(vals)
        return [(0, 0, x) for x in professionals]

    professionals = fields.One2many(
        string="Professionals & commissions",
        comodel_name='sale.order.line.professional', inverse_name='sale_line',
        copy=True, readonly=True, default=_default_professionals)
    commission_free = fields.Boolean(
        string="Comm. free", related="product_id.commission_free",
        store=True, readonly=True)

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            line, account_id=account_id)
        vals['professionals'] = [
            (0, 0, {'professional': x.professional.id,
                    'commission': x.commission.id}) for x in line.professionals]
        return vals


class SaleOrderLineProfessional(models.Model):
    _name = "sale.order.line.professional"
    _rec_name = "professional"

    sale_line = fields.Many2one(
        comodel_name="sale.order.line", required=True, ondelete="cascade")
    professional = fields.Many2one(
        comodel_name="res.partner", required=True, ondelete="restrict",
        domain="[('professional', '=', True')]")
    commission = fields.Many2one(
        comodel_name="sale.commission", required=True, ondelete="restrict")
    amount = fields.Float(compute="_compute_amount", store=True)

    _sql_constraints = [
        ('unique_professional', 'UNIQUE(sale_line, professional)',
         'You can only add one time each professional.')
    ]

    @api.onchange('professional')
    def onchange_professional(self):
        self.commission = self.professional.commission

    @api.depends('sale_line.price_subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = 0.0
            if (not line.sale_line.product_id.commission_free and
                    line.commission):
                if line.commission.amount_base_type == 'net_amount':
                    subtotal = (line.sale_line.price_subtotal -
                                (line.sale_line.product_id.standard_price *
                                 line.sale_line.product_uom_qty))
                else:
                    subtotal = line.sale_line.price_subtotal
                if line.commission.commission_type == 'fixed':
                    line.amount = subtotal * (line.commission.fix_qty / 100.0)
                else:
                    line.amount = line.commission.calculate_section(subtotal)
