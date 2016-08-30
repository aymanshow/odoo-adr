# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# © 2016 Davide Corio - Abstract
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestCommissionFormula(TransactionCase):

    def setUp(self):
        super(TestCommissionFormula, self).setUp()
        self.professional = self.env.ref('sale_commission_formula.professional1')
        self.commission = self.env.ref(
            'sale_commission_formula.commission_5perc10extra')
        self.sale_order = self.env.ref('sale_commission_formula.sale_order_1')
        self.sale_order_line = self.env.ref(
            'sale_commission_formula.sale_order_line_1')
        self.professional_commissions = {
            'professional': self.professional.id, 'commission': self.commission.id}

    def test_sale_order_commission(self):
        # we test the '5% + 10% extra' we should return 41.25 since
        # the order total amount is 750.00.
        self.sale_order_line.professionals = [(0, 0, self.professional_commissions)]
        self.assertEqual(41.25, self.sale_order.commission_total)

    def test_invoice_commission(self):
        # we confirm the sale order and create the corresponding invoice
        self.sale_order.action_button_confirm()
        invoice_id = self.sale_order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        # we add the commissions on the first invoice line
        invoice_line = invoice.invoice_line[0]
        invoice_line.professionals = [(0, 0, self.professional_commissions)]
        # we test the '5% + 10% extra' commissions on the invoice too
        self.assertEqual(41.25, invoice.commission_total)
