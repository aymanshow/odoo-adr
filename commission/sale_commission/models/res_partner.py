# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Avanzosc (<http://www.avanzosc.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class ResPartner(models.Model):
    """Add some fields related to commissions"""
    _inherit = "res.partner"

    professionals = fields.Many2many(
        comodel_name="res.partner", relation="partner_professional_rel",
        column1="partner_id", column2="professional_id",
        domain="[('professional', '=', True)]")
    # Fields for the partner when it acts as an professional
    professional = fields.Boolean(
        string="Creditor/Professional",
        help="Check this field if the partner is a creditor or an professional.")
    professional_type = fields.Selection(
        selection=[("professional", "External professional")], string="Type", required=True,
        default="professional")
    commission = fields.Many2one(
        string="Commission", comodel_name="sale.commission",
        help="This is the default commission used in the sales where this "
             "professional is assigned. It can be changed on each operation if "
             "needed.")
    settlement = fields.Selection(
        selection=[("monthly", "Monthly"),
                   ("quaterly", "Quarterly"),
                   ("semi", "Semi-annual"),
                   ("annual", "Annual")],
        string="Settlement period", default="monthly", required=True)
    settlements = fields.One2many(
        comodel_name="sale.commission.settlement", inverse_name="professional",
        readonly=True)

    @api.onchange('professional_type')
    def onchange_professional_type(self):
        if self.professional_type == 'professional' and self.professional:
            self.supplier = True
