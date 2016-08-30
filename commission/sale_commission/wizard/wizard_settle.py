# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, exceptions, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class SaleCommissionMakeSettle(models.TransientModel):
    _name = "sale.commission.make.settle"

    date_to = fields.Date('Up to', required=True, default=fields.Date.today())
    professionals = fields.Many2many(comodel_name='res.partner',
                              domain="[('professional', '=', True)]")

    def _get_period_start(self, professional, date_to):
        if isinstance(date_to, basestring):
            date_to = fields.Date.from_string(date_to)
        if professional.settlement == 'monthly':
            return date(month=date_to.month, year=date_to.year, day=1)
        elif professional.settlement == 'quaterly':
            # Get first month of the date quarter
            month = ((date_to.month - 1) // 3 + 1) * 3
            return date(month=month, year=date_to.year, day=1)
        elif professional.settlement == 'semi':
            if date_to.month > 6:
                return date(month=7, year=date_to.year, day=1)
            else:
                return date(month=1, year=date_to.year, day=1)
        elif professional.settlement == 'annual':
            return date(month=1, year=date_to.year, day=1)
        else:
            raise exceptions.Warning(_("Settlement period not valid."))

    def _get_next_period_date(self, professional, current_date):
        if isinstance(current_date, basestring):
            current_date = fields.Date.from_string(current_date)
        if professional.settlement == 'monthly':
            return current_date + relativedelta(months=1)
        elif professional.settlement == 'quaterly':
            return current_date + relativedelta(months=3)
        elif professional.settlement == 'semi':
            return current_date + relativedelta(months=6)
        elif professional.settlement == 'annual':
            return current_date + relativedelta(years=1)
        else:
            raise exceptions.Warning(_("Settlement period not valid."))

    @api.multi
    def action_settle(self):
        self.ensure_one()
        professional_line_obj = self.env['account.invoice.line.professional']
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']
        settlement_ids = []
        if not self.professionals:
            self.professionals = self.env['res.partner'].search(
                [('professional', '=', True)])
        date_to = fields.Date.from_string(self.date_to)
        for professional in self.professionals:
            date_to_professional = self._get_period_start(professional, date_to)
            # Get non settled invoices
            professional_lines = professional_line_obj.search(
                [('invoice_date', '<', date_to_professional),
                 ('professional', '=', professional.id),
                 ('settled', '=', False)], order='invoice_date')
            if professional_lines:
                pos = 0
                sett_to = fields.Date.to_string(date(year=1900, month=1,
                                                     day=1))
                while pos < len(professional_lines):
                    if (professional.commission.invoice_state == 'paid' and
                            professional_lines[pos].invoice.state != 'paid'):
                        pos += 1
                        continue
                    if professional_lines[pos].invoice_date > sett_to:
                        sett_from = self._get_period_start(
                            professional, professional_lines[pos].invoice_date)
                        sett_to = fields.Date.to_string(
                            self._get_next_period_date(professional, sett_from) -
                            timedelta(days=1))
                        sett_from = fields.Date.to_string(sett_from)
                        settlement = settlement_obj.create(
                            {'professional': professional.id,
                             'date_from': sett_from,
                             'date_to': sett_to})
                        settlement_ids.append(settlement.id)
                    settlement_line_obj.create(
                        {'settlement': settlement.id,
                         'professional_line': [(6, 0, [professional_lines[pos].id])]})
                    pos += 1

        # go to results
        if len(settlement_ids):
            return {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }

        else:
            raise exceptions.Warning(_("No hay facturas pendientes a liquidar para este/os profesional/es."))
            #return {'type': 'ir.actions.act_window_close'}
