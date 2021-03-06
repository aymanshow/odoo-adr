# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013-2015 Camptocamp SA
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
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _
from openerp.addons.sale_transport_multi_address.model.sale_order import (
    SaleOrder as base_sale_order
)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    LO_STATES = base_sale_order.LO_STATES

    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        # Added state
        ('accepted', 'Cost Estimate Accepted'),
        ('cancel', 'Cancelled'),
        ('waiting_date', 'Waiting Schedule'),
        ('progress', 'Sales Order'),
        ('manual', 'Sale to Invoice'),
        ('shipping_except', 'Shipping Exception'),
        ('invoice_except', 'Invoice Exception'),
        ('done', 'Done'),
        ], 'Status', readonly=True, copy=False,
        help="Gives the status of the quotation or sales order.\nThe exception"
             " status is automatically set when a cancel operation occurs in "
             "the invoice validation (Invoice Exception) or in the picking "
             "list process (Shipping Exception).\nThe 'Waiting Schedule' "
             "status is set when the invoice is confirmed but waiting for the "
             "scheduler to run on the order date.",
        select=True)

    # incoterm is overridden to add states
    incoterm = fields.Many2one(
        'stock.incoterms',
        'Incoterm',
        states=LO_STATES,
        help="International Commercial Terms are a series of predefined "
        "commercial terms used in international transactions.")

    # also carrier is overridden to add states
    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Delivery Method",
        states=LO_STATES,
        help="Complete this field if you plan to invoice the shipping based "
        "on picking.")

    @api.model
    def get_order_type_selection(self):
        """ Extendable selection list """
        return [('standard', 'Standard'),
                ('cost_estimate_only', 'Cost Estimate Only')]

    @api.model
    def _get_order_type_selection(self):
        return self.get_order_type_selection()

    order_type = fields.Selection(
        selection=_get_order_type_selection,
        string='Type',
        states=LO_STATES,
        default='standard')

    incoterm_address = fields.Char(
        'Incoterm Place',
        states=LO_STATES,
        help="Incoterm Place of Delivery. "
             "International Commercial Terms are a series of "
             "predefined commercial terms used in "
             "international transactions.")
    delivery_time = fields.Char('Delivery time', states=LO_STATES)
    currency_id = fields.Many2one(
        related='pricelist_id.currency_id',
        co_model='res.currency',
        string='Currency',
        states=LO_STATES)
    remark = fields.Text('Remarks / Description', states=LO_STATES)
    delivery_remark = fields.Text('Delivery Remarks', states=LO_STATES)

    # Set states on base fields
    origin = fields.Char(states=LO_STATES)
    client_order_ref = fields.Char(states=LO_STATES)
    user_id = fields.Many2one(states=LO_STATES)
    note = fields.Text(states=LO_STATES)
    payment_term = fields.Many2one(states=LO_STATES)
    fiscal_position = fields.Many2one(states=LO_STATES)
    company_id = fields.Many2one(states=LO_STATES)
    section_id = fields.Many2one(states=LO_STATES)
    procurement_group_id = fields.Many2one(states=LO_STATES)

    # redefine consignee_id with required=False
    # we have a constraint to make it
    # required only if is cost_estimate_only
    consignee_id = fields.Many2one(
        'res.partner',
        string='Consignee',
        required=False,
        help="The person to whom the shipment is to be delivered.")

    @api.one
    @api.constrains('order_type', 'consignee_id')
    def _check_consignee(self):
        if self.order_type != 'cost_estimate_only' and not self.consignee_id:
            raise exceptions.Warning(_('If this is not only for Cost Estimate,'
                                       ' you must provide a Consignee'))

    @api.multi
    def action_quotation_send(self):
        """ In case of Cost Estimate only, register an option to set the
        Cost Estimate immediatly to `done` when the users sends his mail.

        Nevertheless, if he launches the wizard but cancel it, we won't
        trigger the transition to `done`

        We pass this in order to avoid to browse in `mail.compose.message`

        """
        res = super(SaleOrder, self).action_quotation_send()
        if self.order_type == 'cost_estimate_only':
            res['context'].update(mark_cost_estimate_as_done=True)
        return res

    @api.multi
    def action_accepted(self):
        self.write({'state': 'accepted'})


class mail_compose_message(models.Model):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self):
        """ When sending mail for a Cost Estimate Only
        Send a signal to set the Cost Estimate to `done`

        """
        context = self.env.context
        if (context.get('default_model') == 'sale.order' and
                'default_res_id' in context and
                'mark_cost_estimate_as_done' in context):
            res_id = context.get('default_res_id')
            sale_order = self.env['sale.order'].browse(res_id)
            sale_order.signal_workflow('cost_estimate_only_sent')
        return super(mail_compose_message, self).send_mail()
