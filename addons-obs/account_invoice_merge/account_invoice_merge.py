# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Author: Naresh Soni
#    Copyright 2015 Cozy Business Solutions Pvt.Ltd
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

import base64
import csv

from openerp import models, fields, api, _, exceptions
from openerp.exceptions import except_orm

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    insurance = fields.Boolean(string='Insurance Company ?')

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    related_patient_id = fields.Many2one('res.partner', string='Related Patient ')
    invoice_include = fields.Boolean(string='Invoice Included')
    insurance = fields.Boolean('Insurance')
    related_invoice_id = fields.Many2one('account.invoice', string='Parent Invoice')
    related_invoices = fields.One2many('account.invoice', 'related_invoice_id', string='Related Invoices')

    report = fields.Binary(string="Reporte", sixe=64, readonly=True)
    report_name = fields.Char(string="Nombre de Reporte", readonly=True)


    @api.multi
    def invoice_validate(self):
        super(account_invoice,self).invoice_validate()
        for invoice in self:
            if invoice.residual == 0:
                invoice.write({'residual': invoice.amount_total})
    
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']
        obj_sequence = self.env['ir.sequence']
        
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            
            if inv.insurance:
                if inv.journal_id.sequence_id:
                    c = {'fiscalyear_id': inv.period_id.fiscalyear_id.id}
                    new_name = obj_sequence.with_context(c).next_by_id(inv.journal_id.sequence_id.id)
                    inv.write({'number': new_name})
                continue
                
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            # if self.env['res.users'].has_group('account.group_supplier_inv_check_total'):
            #     if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
            #         raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True

    @api.multi
    def action_number(self):
        #TODO: not correct fix but required a fresh values before reading it.
        self.write({})

        for inv in self:
            self.write({'internal_number': inv.number})

            if inv.type in ('in_invoice', 'in_refund'):
                if not inv.reference:
                    ref = inv.number
                else:
                    ref = inv.reference
            else:
                ref = inv.number
            
            if inv.move_id:
                self._cr.execute(""" UPDATE account_move SET ref=%s
                               WHERE id=%s AND (ref IS NULL OR ref = '')""",
                            (ref, inv.move_id.id))
                self._cr.execute(""" UPDATE account_move_line SET ref=%s
                               WHERE move_id=%s AND (ref IS NULL OR ref = '')""",
                            (ref, inv.move_id.id))
                self._cr.execute(""" UPDATE account_analytic_line SET ref=%s
                               FROM account_move_line
                               WHERE account_move_line.move_id = %s AND
                                     account_analytic_line.move_id = account_move_line.id""",
                            (ref, inv.move_id.id))
            self.invalidate_cache()

        return True
    
    @api.multi
    def action_get_moves(self):
        self.ensure_one()
        
        AccountMoveLine = self.env['account.move.line']
        AccountVoucher = self.env['account.voucher']
        AccountJournal = self.env['account.journal']
        
        ctx = {}
        
        invoice_ids = self.related_invoices.ids
        
        partner_id = self.partner_id.id
        # Get default journal
        res = AccountVoucher._make_journal_search('bank')
        journal_id = res and res[0]
        journal = AccountJournal.browse(journal_id)
        
        #Get company currency
        currency_id = self.env.user.company_id.currency_id.id
        
        #Current date
        date = fields.Date.today()
        
        # Payment type
        ttype = 'receipt'
        lines = [] 
        
        #getting all move lines
        res = AccountVoucher.with_context({'date': date, 'type': 'receipt'}).recompute_voucher_lines(partner_id, journal_id, 0.0, currency_id, ttype, date)
        
        # gettting account from 
        account_id = journal.default_debit_account_id.id
        
        for line in res['value']['line_cr_ids']:
            if line.get('move_line_id'):
                moveline = AccountMoveLine.browse(line['move_line_id'])
                if moveline.invoice.id in invoice_ids: 
                    lines.append((0,0, line)) 
            
        voucher = AccountVoucher.create({
            'partner_id': partner_id, 
            'account_id': account_id, 
            'journal_id': journal_id, 
            'type':'receipt',
            'line_cr_ids': lines,
        })
        ctx.update({'date': date, 'type': 'receipt', 'partner_id': partner_id, 'default_type': 'receipt'})
        form_view = self.env.ref('account_voucher.view_vendor_receipt_form', False)
        
        return {
            'name': _('Customer Payments'),
            'view_type':'form',
            'view_mode':'form',
            'res_model':'account.voucher',
            'views': [(form_view.id,'form')],
            'type':'ir.actions.act_window',
            'domain': "[('id','in',["+','.join(map(str,[voucher.id]))+"])]",
            'context': ctx,
        }
    
    @api.multi
    def export_to_csv(self):
        path = '/tmp/facturaRelated.csv'
        f = open(path,'wb')
        writer = csv.writer(f)
        writer.writerow(
            ('Fecha', 'Parent Invoice', 'Cliente', 'Paciente Relacionado',
             'Ref/#Autorizacion', 'Documento Origen', 'Cantidad',
             'Servicio', 'Monto', 'Cobertura', 'Total')
        )

        for inv in self.related_invoices:

            line = inv.invoice_line

            writer.writerow([
                inv.date_invoice, inv.related_invoice_id.name, inv.partner_id.name,
                inv.related_patient_id.name, inv.name, inv.origin, line.quantity,
                line.name, line.price_unit, line.discount, inv.amount_total]
            )

        f.close()

        f = open(path, 'rb')
        report = base64.b64encode(f.read())
        f.close()
        report_name = 'facturas.csv'
        self.write({'report': report, 'report_name': report_name})
        return True

class generate_insurance_invoice(models.TransientModel):
    _name = 'generate.insurance.invoice'
    
    insurance_company_id = fields.Many2one('res.partner', string='Insurance Company', domain=[('insurance', '=', True)])
    
    @api.multi
    def create_invoice(self):

        self.ensure_one()
        ids = self.env.context['active_ids']
        if len(ids) < 2:
                raise exceptions.Warning(
                    _('Please select multiple invoice to merge in the list '
                      'view.'))
        AccountInvoice = self.env['account.invoice']
        
        invoice_desc = ''
        total_qty = 0.0
        total_price = 0.0
        price_unit = 0.0
        account_id = False

        # invoices = AccountInvoice.search([('partner_id', '=', self.insurance_company_id.id), ('state', '!=', 'cancel'),
        #                                   ('invoice_include', '=', False), ('id', 'in', ids)],
        #                                  order='date_invoice')
        invoices = AccountInvoice.browse(ids)
        
        if invoices:
            for d in invoices:
                if d['state'] != 'open':
                    raise exceptions.Warning(
                        _('At least one of the selected invoices is %s!') %
                        d['state'])
                if d['partner_id'] != self.insurance_company_id:
                    raise exceptions.Warning(
                        _('Una o mas facturas seleccionadas no pertenecen a la aseguradora seleccionada!'))
                if d['invoice_include'] == True:
                    raise exceptions.Warning(
                        _('La factura # %s ya ha sido agrupada previamente!') %
                        d['number'])
                if d['company_id'] != invoices[0]['company_id']:
                    raise exceptions.Warning(
                        _('Not all invoices are at the same company!'))
                if d['partner_id'] != invoices[0]['partner_id']:
                    raise exceptions.Warning(
                        _('Not all invoices are for the same partner!'))
                if d['type'] != invoices[0]['type']:
                    raise exceptions.Warning(
                        _('Not all invoices are of the same type!'))
                if d['currency_id'] != invoices[0]['currency_id']:
                    raise exceptions.Warning(
                        _('Not all invoices are at the same currency!'))

            invoice_desc += 'Insurance Services From ' + str(invoices[0].date_invoice) + ' To ' + str(invoices[-1].date_invoice)
         
        related_invoices = []
        for invoice in invoices:
            related_invoices.append(invoice.id)
            for line in invoice.invoice_line:
                total_qty += line.quantity
                total_price += line.price_subtotal
            invoice.write({'invoice_include': True})
        
        if total_qty > 0.0 and total_price > 0.0:
            price_unit = (total_price / total_qty)

        invoice_line_vals = {
            'name': invoice_desc,
            'quantity': total_qty,
            'price_unit': price_unit,
            'account_id': invoices[0].account_id.id,
        }

        if invoices:
            print total_price, 'total'
            invoice_vals = {
                'name': invoices[0].name,
                # 'origin': invoices[0].origin,
                'type': 'out_invoice',
                'reference': invoices[0].reference,
                'account_id': invoices[0].account_id.id,
                'partner_id': self.insurance_company_id.id,
                'journal_id': invoices[0].journal_id.id,
                'invoice_line': [(0, 0, invoice_line_vals)],
                'currency_id': invoices[0].currency_id.id,
                # 'comment': invoices[0].comment,
                'payment_term': invoices[0].payment_term.id,
                'fiscal_position': invoices[0].fiscal_position.id,
                'date_invoice': invoices[0].date_invoice,
                'company_id': invoices[0].company_id.id,
                'user_id': invoices[0].user_id.id,
                'insurance': True,
                'related_invoices': [(6,0,related_invoices)]
            }
            AccountInvoice.create(invoice_vals)
        return True

