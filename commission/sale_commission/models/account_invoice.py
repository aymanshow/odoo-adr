# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoice(models.Model):
    """Invoice inherit to add salesman"""
    _inherit = "account.invoice"

    @api.depends('invoice_line.professionals.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.invoice_line:
                record.commission_total += sum(x.amount for x in line.professionals)

    commission_total = fields.Float(
        string="Commissions", compute="_compute_commission_total",
        store=True)

    @api.multi
    def action_cancel(self):
        """Put settlements associated to the invoices in exception."""
        settlements = self.env['sale.commission.settlement'].search(
            [('invoice', 'in', self.ids)])
        settlements.write({'state': 'except_invoice'})
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def invoice_validate(self):
        """Put settlements associated to the invoices again in invoice."""
        settlements = self.env['sale.commission.settlement'].search(
            [('invoice', 'in', self.ids)])
        settlements.write({'state': 'invoiced'})
        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def _refund_cleanup_lines(self, lines):
        """ugly function to map all fields of account.invoice.line
        when creates refund invoice"""
        res = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        if lines and lines[0]._name != 'account.invoice.line':
            return res
        for i, line in enumerate(lines):
            vals = res[i][2]
            professionals = super(AccountInvoice, self)._refund_cleanup_lines(
                line['professionals'])
            # Remove old reference to source invoice
            for professional in professionals:
                professional_vals = professional[2]
                del professional_vals['invoice']
                del professional_vals['invoice_line']
            vals['professionals'] = professionals
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

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
                vals['display_name'] = self.env['account.invoice.line.professional']\
                    .new(vals).display_name
                professionals.append(vals)
        return [(0, 0, x) for x in professionals]

    professionals = fields.One2many(
        comodel_name="account.invoice.line.professional",
        inverse_name="invoice_line", string="Professionals & commissions",
        help="Professionals/Commissions related to the invoice line.",
        default=_default_professionals, copy=True)
    commission_free = fields.Boolean(
        string="Comm. free", related="product_id.commission_free",
        store=True, readonly=True)


class AccountInvoiceLineProfessional(models.Model):
    _name = "account.invoice.line.professional"

    invoice_line = fields.Many2one(
        comodel_name="account.invoice.line",
        ondelete="cascade",
        required=True, copy=False)
    invoice = fields.Many2one(
        string="Invoice", comodel_name="account.invoice",
        related="invoice_line.invoice_id",
        store=True)
    invoice_date = fields.Date(
        string="Invoice date",
        related="invoice.date_invoice",
        store=True, readonly=True)
    product = fields.Many2one(
        comodel_name='product.product',
        related="invoice_line.product_id")
    professional = fields.Many2one(
        comodel_name="res.partner",
        domain="[('professional', '=', True)]",
        ondelete="restrict",
        required=True)
    commission = fields.Many2one(
        comodel_name="sale.commission", ondelete="restrict", required=True)
    amount = fields.Float(
        string="Amount settled", compute="_compute_amount", store=True)
    professional_line = fields.Many2many(
        comodel_name='sale.commission.settlement.line',
        relation='settlement_professional_line_rel',
        column1='professional_line_id', column2='settlement_id',
        copy=False)
    settled = fields.Boolean(
        compute="_compute_settled",
        store=True, copy=False)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = "%s: %s" % (record.professional.name, record.commission.name)
            res.append((record.id, name))
        return res

    @api.depends('professional', 'commission')
    def _compute_display_name(self):
        return super(AccountInvoiceLineProfessional, self)._compute_display_name()

    @api.onchange('professional')
    def onchange_professional(self):
        self.commission = self.professional.commission

    @api.depends('invoice_line.price_subtotal')
    def _compute_amount(self):
        for line in self:
            line.amount = 0.0
            if (not line.invoice_line.product_id.commission_free and
                    line.commission):
                if line.commission.amount_base_type == 'net_amount':
                    subtotal = (line.invoice_line.price_subtotal -
                                (line.invoice_line.product_id.standard_price *
                                 line.invoice_line.quantity))
                else:
                    subtotal = line.invoice_line.price_subtotal
                if line.commission.commission_type == 'fixed':
                    line.amount = subtotal * (line.commission.fix_qty / 100.0)
                else:
                    line.amount = line.commission.calculate_section(subtotal)
                # Refunds commissions are negative
                if line.invoice.type in ('out_refund', 'in_refund'):
                    line.amount = -line.amount

    @api.depends('professional_line', 'professional_line.settlement.state', 'invoice',
                 'invoice.state')
    def _compute_settled(self):
        # Count lines of not open or paid invoices as settled for not
        # being included in settlements
        for line in self:
            line.settled = (line.invoice.state not in ('open', 'paid') or
                            any(x.settlement.state != 'cancel'
                                for x in line.professional_line))

    _sql_constraints = [
        ('unique_professional', 'UNIQUE(invoice_line, professional)',
         'You can only add one time each professional.')
    ]
