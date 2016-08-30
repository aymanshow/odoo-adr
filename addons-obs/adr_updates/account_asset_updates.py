# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Open Business Solutions (<http://www.obsdr.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import math
import re
import time
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
import pdb
import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression, orm
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.exceptions import except_orm, Warning, RedirectWarning

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

# class account_invoice_line(osv.osv):
#
#     _inherit = 'account.invoice.line'
#
#     _columns = {
#         'asset_category_id': fields.many2one('account.asset.category', 'Asset Category'),
#     }
#
#     def asset_create(self, cr, uid, lines, context=None):
#         import pdb; pdb.set_trace()
#         context = context or {}
#
#         product_obj = self.pool.get('product.template')
#         asset_obj = self.pool.get('account.asset.asset')
#         asset_asset_obj = self.pool.get('asset.asset')
#         for line in lines:
#             quantity = int(round(line.quantity))
#             if line.asset_category_id:
#                 for i in range(quantity):
#                     taxes = line.invoice_line_tax_id
#                     tax_line_amount = 0
#                     for tax in taxes:
#                         if tax.itbis and (not tax.price_include or not tax.exempt):
#                             tax_line_amount += (line.price_unit * tax.amount)
#                         else:
#                             tax_line_amount += 0
#                     asset_asset_vals = {
#                         'name': line.name,
#                         'vendor_id': line.partner_id.id,
#                         'purchase_date': line.invoice_id.date_invoice,
#                     }
#                     vals = {
#                         'name': line.name,
#                         'code': line.invoice_id.number or False,
#                         'asset_id': asset_asset_obj.create(cr, uid, asset_asset_vals, context=context),
#                         'category_id': line.asset_category_id.id,
#                         'category_parent_id': line.asset_category_id.parent_id.id or False,
#                         'account_analytic_id': line.account_analytic_id.id or False,
#                         'purchase_value': line.price_unit,
#                         'period_id': line.invoice_id.period_id.id,
#                         'partner_id': line.invoice_id.partner_id.id,
#                         'company_id': line.invoice_id.company_id.id,
#                         'currency_id': line.invoice_id.currency_id.id,
#                         'purchase_date': line.invoice_id.date_invoice,
#                         'product_id': line.product_id.id or False,
#                     }
#
#                     changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
#                     vals.update(changed_vals['value'])
#                     asset_id = asset_obj.create(cr, uid, vals, context=context)
#
#                     if line.asset_category_id.open_asset:
#                         asset_obj.validate(cr, uid, [asset_id], context=context)
#
#                     product_id = line.product_id
#                     if not product_id.fixed_asset:
#                         vals = {'fixed_asset': True,
#                                 'asset_category_id': line.asset_category_id.id}
#
#                         product = product_obj.write(cr, uid, product_id.id, vals, context=context)
#
#         return True


class AccountAnalyticAccount(orm.Model):
    
    _inherit = 'account.analytic.account'
    
    _columns = {
        'is_discharge_temp_loc': fields.boolean('Ubicacion de Descargo')
    }

class AssetMove(orm.Model):

    _name = 'account.asset.move'
    _description = 'Movimiento de Activo Fijo'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    READONLY_STATES = {
        'confirmed': [('readonly', True)],
        'audited': [('readonly', True)],
        'received': [('readonly', True)],
        'validated': [('readonly', True)]
    }

    _order = 'referencia desc'
    _columns = {
        'asset_id': fields.many2one('account.asset.asset', 'Activo', required=True,
                                    domain=[('state','not in',['draft','close'])], states=READONLY_STATES,),
        'asset_code': fields.related('asset_id', 'asset_code', string='Codigo', readonly=True, type="char"),
        'partner_id': fields.many2one('res.partner', 'Empleado / Cliente', states=READONLY_STATES, ),
        'sale_customer_id': fields.many2one('res.partner', 'Paciente / Cliente',
                                            domain=[('customer', '=', True),
                                                    ('supplier', '=', False),
                                                    ('employee', '=', False)], states=READONLY_STATES, ),
        'sale_employee_id': fields.many2one('res.partner', 'Funcionario / Empleado',
                                            domain=[('employee', '=', True)], states=READONLY_STATES, ),
        'sale_company_id': fields.many2one('res.company', 'Filial', states=READONLY_STATES, ),
        'origin_company': fields.many2one('res.company', 'Filial Origen', states=READONLY_STATES,),
        'origin_account_analytic_id': fields.many2one('account.analytic.account', 'Departamento Origen',
                                                       domain=[('type','=','normal'),
                                                        ('is_discharge_temp_loc','=',False)],
                                                      states=READONLY_STATES,),
        'destiny_company': fields.many2one('res.company', 'Filial Destino', states=READONLY_STATES,),
        'destiny_account_analytic_id': fields.many2one('account.analytic.account', 'Departamento Destino',
                                                       domain=[('type','=','normal'),
                                                               ('is_discharge_temp_loc','=',False)], states=READONLY_STATES,),
        'destiny_discharge_location': fields.many2one('account.analytic.account', 'Ubicacion de Descargo',
                                                       domain=[('is_discharge_temp_loc','=',True)], states=READONLY_STATES,),
        'origin_reimbusement_location': fields.many2one('account.analytic.account', 'Ubicacion de Descargo',
                                                       domain=[('is_discharge_temp_loc','=',True)], states=READONLY_STATES,),
        'income_account_id': fields.many2one('account.account', "Cuenta de ingreso de venta",
                                             domain=[('type','=','other')], states=READONLY_STATES,),
        'date': fields.date('Fecha', require=True, help="""Fecha cuando se ejecutara el movimiento""",
                            states=READONLY_STATES,),
        'department_id': fields.many2one('hr.department', string='Department',
                                    states={'draft': [('readonly', False)]}),
        'manager_id': fields.many2one('hr.employee', string='Manager',
                                 states={'draft': [('readonly', False)]}),
        'movement_category': fields.selection((('company_change', 'Cambio de Empresa'),
                                               ('department_change', 'Cambio de Departamento'),
                                               ('donation_employee', 'Donacion - Empleados'),
                                               ('donation_patient', 'Donacion - Pacientes'),
                                               ('discharge_temporary', 'Descargo Temporal'),
                                               ('discharge_definitive', 'Descargo Definitivo'),
                                               ('reimbursement', 'Reintegro'),
                                               ('customer_sale', 'Venta a Paciente / Cliente'),
                                               ('employee_sale', 'Venta a Funcionario y/o Empleados'),
                                               ('company_sale', 'Venta a Filial'),), 'Tipo de movimiento',
                                              required=True, help="""The category to wich the movement belongs.""",
                                              states=READONLY_STATES,),
        'state': fields.selection((('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('audited', 'Auditado'),
            ('received', 'Recibido'),
            ('validated', 'Validado'),
            ('cancel', 'Cancel')), 'Estado', required=True),
        'stage': fields.selection((('waiting_confirm', 'Esperando Confirmacion Director Departamento'),
            ('waiting_audit', 'Esperando Auditoria'),
            ('waiting_reception', 'Esperando Recepcion'),
            ('waiting_validation', 'Esperando Validacion'),
            ('validated', 'Validado'),
            ('cancel', 'Cancel')), 'Etapa', required=True),
        'notes': fields.char('Notas', states=READONLY_STATES,),
        'user_id': fields.many2one('res.users', 'Solicitador por:', readonly=True),
        'confirmer': fields.many2one('res.users', 'Confirmado por:', readonly=True),
        'auditor': fields.many2one('res.users', 'Auditado por:', readonly=True),
        'receiver': fields.many2one('res.users', 'Recibido por:', readonly=True),
        'validator': fields.many2one('res.users', 'Validado por:', readonly=True),
        'canceler': fields.many2one('res.users', 'Cancelado por:', readonly=True),
        'referencia': fields.char('Referencia'),
        'invoice_id': fields.many2one('account.invoice', "Factura de venta relacionada")
    }
    _defaults = {
        'state': 'draft',
        'stage': 'waiting_confirm',
        'date': fields.datetime.now,
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def onchange_user_id(self, cr, uid, ids, user_id=False, context=None):

        if user_id:
            employee_obj = self.pool.get('hr.employee')
            employee = employee_obj.search(cr, uid, [('user_id', '=', user_id)], limit=1)
            if employee:
                employee_rec = employee_obj.browse(cr, uid, employee, context)
                self.write(cr, uid, ids, {'manager_id': employee_rec.department_id.manager_id.id,
                                          'department_id': employee_rec.department_id and employee_rec.department_id.id or False})
                return {'value': {'manager_id': employee_rec.department_id.manager_id.id,
                                  'department_id': employee_rec.department_id and employee_rec.department_id.id or False}}

    def create(self, cr, uid, ids, context=None):
        created_id = super(AssetMove, self).create(cr, uid, ids, context)
        ids['referencia'] = self.pool.get('ir.sequence').get(cr, uid, 'account.asset.move')
        self.write(cr, uid, created_id, ids, context)

        return created_id

    def action_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed', 'confirmer': uid, 'stage': 'waiting_audit'})
        return True

    def check_movement_cat(self, cr, uid, ids, context=None):
        """
        @return: True or False
        """
        res = False
        obj_self = self.browse(cr, uid, ids[0], context=context)
        movement_cat = obj_self.movement_category
        if movement_cat in ['donation_employee', 'donation_patient', 'discharge_definitive',
                            'customer_sale', 'employee_sale', 'company_sale']:
            res = True
        return res

    def action_audit(self, cr, uid, ids, context=None):
        obj_self = self.browse(cr, uid, ids[0], context=context)
        movement_cat = obj_self.movement_category
        if movement_cat in ['donation_employee','donation_patient','discharge_definitive',
                            'customer_sale', 'employee_sale', 'company_sale']:
            self.write(cr, uid, ids, {'state': 'received', 'receiver': False, 'auditor': uid, 'stage': 'waiting_validation'})
        else:
            self.write(cr, uid, ids, {'state': 'audited', 'auditor': uid, 'stage': 'waiting_reception'})
        return True

    def action_receive(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'received', 'receiver': uid, 'stage': 'waiting_validation'})
        return True

    def action_validate(self, cr, uid, ids, context=None):
        obj_self = self.browse(cr, uid, ids[0], context=context)
        movement_cat = obj_self.movement_category

        asset_id = obj_self.asset_id.id
        account_asset_obj = self.pool.get('account.asset.asset')

        #if movement_cat == 'company_change' or movement_cat == 'department_change':
        if movement_cat in ['company_change', 'department_change']:
            destiny_company = obj_self.destiny_company.id or obj_self.origin_company.id
            destiny_account_analytic_id = obj_self.destiny_account_analytic_id.id or obj_self.origin_account_analytic_id.id

            for asset in account_asset_obj.browse(cr, uid, asset_id, context):
                vals = {'company_id': destiny_company,
                        'account_analytic_id': destiny_account_analytic_id,
                        }
                asset = account_asset_obj.write(cr, uid, asset_id, vals, context=context)
        
        elif movement_cat in ['reimbursement']:
            destiny_company = obj_self.destiny_company.id or obj_self.origin_company.id
            destiny_account_analytic_id = obj_self.destiny_account_analytic_id.id or obj_self.origin_account_analytic_id.id

            for asset in account_asset_obj.browse(cr, uid, asset_id, context):
                vals = {'company_id': destiny_company,
                        'account_analytic_id': destiny_account_analytic_id,
                        }
                asset = account_asset_obj.write(cr, uid, asset_id, vals, context=context)
                
        elif movement_cat in ['discharge_temporary']:   
            destiny_discharge_location = obj_self.destiny_account_analytic_id.id or obj_self.destiny_discharge_location.id
            for asset in account_asset_obj.browse(cr, uid, asset_id, context):
                vals = {
                        'account_analytic_id': destiny_discharge_location,
                        }
                asset = account_asset_obj.write(cr, uid, asset_id, vals, context=context)

        elif movement_cat in ['customer_sale', 'employee_sale', 'company_sale']:

            context = dict(context or {})
            can_close = False
            asset_obj = self.pool.get('account.asset.asset')
            asset_lines_obj = self.pool.get('account.asset.depreciation.line')
            period_obj = self.pool.get('account.period')
            invoice_obj = self.pool.get('account.invoice')
            invoice_line_obj = self.pool.get('account.invoice.line')
            move_obj = self.pool.get('account.move')
            move_line_obj = self.pool.get('account.move.line')
            currency_obj = self.pool.get('res.currency')
            created_move_ids = []
            created_invoice_ids = []
            asset_ids = []

            depreciation_amount = 0.00

            for asset in account_asset_obj.browse(cr, uid, asset_id, context):
                move_checks = asset_lines_obj.search(cr, uid, [("asset_id", "=", asset_id), ("move_check", "=", True)])
                for move_checks_lines in asset_lines_obj.browse(cr, uid, move_checks):

                    depreciation_amount += move_checks_lines.amount

                depreciation_date = time.strftime('%Y-%m-%d')
                sale_date = time.strftime('%Y-%m-%d')
                period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
                company_currency = asset.company_id.currency_id.id
                current_currency = asset.currency_id.id
                purchase_value = currency_obj.compute(cr, uid, current_currency, company_currency,
                                                      asset.purchase_value, context=context)
                sign = (asset.category_id.journal_id.type == 'purchase' and 1) or -1
                residual_value = abs(purchase_value-depreciation_amount)
                asset_name = asset.name
                reference = obj_self.referencia
                # import pdb; pdb.set_trace()
                invoice_vals = {
                    'partner_id': obj_self.sale_customer_id.id or obj_self.sale_employee_id.id
                                  or obj_self.sale_company_id.partner_id.id,
                    'fiscal_position': obj_self.sale_customer_id.property_account_position.id
                                       or obj_self.sale_employee_id.property_account_position.id
                                       or obj_self.sale_company_id.partner_id.property_account_position.id,
                    'date_invoice': sale_date,
                    'account_id': obj_self.sale_customer_id.property_account_receivable.id
                                       or obj_self.sale_employee_id.property_account_receivable.id
                                       or obj_self.sale_company_id.partner_id.property_account_receivable.id,
                    'period_id': period_ids and period_ids[0] or False,
                    'origin': obj_self.referencia,
                    'type': 'out_invoice',
                    'payment_term': obj_self.sale_customer_id.property_payment_term.id
                                       or obj_self.sale_employee_id.property_payment_term.id
                                       or obj_self.sale_company_id.partner_id.property_payment_term.id or False,

                    }
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)

                invoice_line_obj.create(cr, uid, {'name': asset.name,
                                                  'account_id': obj_self.income_account_id.id,
                                                  'quantity': 1,
                                                  'invoice_id': invoice_id,
                                                  'uos_id': 1,
                                                  'price_unit': residual_value,
                                                  'account_analytic_id': asset.account_analytic_id.id
                                                  })

                move_vals = {
                    'name': asset_name,
                    'date': depreciation_date,
                    'ref': reference,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': asset.category_id.journal_id.id,
                    }
                move_id = move_obj.create(cr, uid, move_vals, context=context)
                journal_id = asset.category_id.journal_id.id
                partner_id = asset.partner_id.id

                #Linea de asiento contable: Credito a Cuenta de Activo por el costo de adquisicion del activo
                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_asset_id.id,
                    'debit': 0.0,
                    'credit': purchase_value,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'amount_currency': company_currency != current_currency and - sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,

                })

                #Linea de asiento contable: Debito a cuenta de amortizacion por el valor de la depreciacion acumulada
                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_depreciation_id.id,
                    'credit': 0.0,
                    'debit': depreciation_amount,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,

                })

                #Linea de asiento contable: Debito a cuenta de gasto de amortizacion  por el valor residual del activo
                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_expense_depreciation_id.id,
                    'credit': 0.0,
                    'debit': residual_value,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,
                    'asset_id': asset.id
                })

                self.write(cr, uid, ids, {'invoice_id': invoice_id})
                created_invoice_ids.append(invoice_id)
                created_move_ids.append(move_id)
                asset_ids.append(asset.id)

            # we re-evaluate the assets to determine whether we can close them
            for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
                if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
                    asset.write(cr, uid, asset_id, {'state': 'close'})

            account_asset_obj.write(cr, uid, asset_id, {'state': 'close'})

        elif movement_cat in ['donation_employee', 'donation_patient', 'discharge_definitive']:
            context = dict(context or {})
            asset_obj = self.pool.get('account.asset.asset')
            asset_lines_obj = self.pool.get('account.asset.depreciation.line')
            period_obj = self.pool.get('account.period')
            move_obj = self.pool.get('account.move')
            move_line_obj = self.pool.get('account.move.line')
            currency_obj = self.pool.get('res.currency')
            created_move_ids = []
            asset_ids = []

            depreciation_amount = 0.00

            for asset in account_asset_obj.browse(cr, uid, asset_id, context):
                move_checks = asset_lines_obj.search(cr, uid, [("asset_id", "=", asset_id), ("move_check", "=", True)])
                for move_checks_lines in asset_lines_obj.browse(cr, uid, move_checks):
                    depreciation_amount += move_checks_lines.amount

                depreciation_date = time.strftime('%Y-%m-%d')
                period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
                company_currency = asset.company_id.currency_id.id
                current_currency = asset.currency_id.id

                purchase_value = currency_obj.compute(cr, uid, current_currency, company_currency,
                                                      asset.purchase_value, context=context)
                sign = (asset.category_id.journal_id.type == 'purchase' and 1) or -1
                asset_name = asset.name
                reference = obj_self.referencia
                residual_value = abs(purchase_value-depreciation_amount)
                move_vals = {
                    'name': asset_name,
                    'date': depreciation_date,
                    'ref': reference,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': asset.category_id.journal_id.id,
                    }
                move_id = move_obj.create(cr, uid, move_vals, context=context)
                journal_id = asset.category_id.journal_id.id
                partner_id = asset.partner_id.id

                #Linea de asiento contable: Credito a Cuenta de Activo por el costo de adquisicion del activo
                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_asset_id.id,
                    'debit': 0.0,
                    'credit': purchase_value,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'amount_currency': company_currency != current_currency and - sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,

                })

                #Linea de asiento contable: Debito a cuenta de amortizacion por el valor de la depreciacion acumulada
                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_depreciation_id.id,
                    'credit': 0.0,
                    'debit': depreciation_amount,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,

                })

                #Linea de asiento contable: Debito a cuenta de gasto de amortizacion  por el valor residual del activo
                move_line_obj.create(cr, uid, {
                    'name': asset_name,
                    'ref': reference,
                    'move_id': move_id,
                    'account_id': asset.category_id.account_expense_depreciation_id.id,
                    'credit': 0.0,
                    'debit': residual_value,
                    'period_id': period_ids and period_ids[0] or False,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency or False,
                    'amount_currency': company_currency != current_currency and sign * asset.amount or 0.0,
                    'analytic_account_id': asset.account_analytic_id.id,
                    'date': depreciation_date,
                    'asset_id': asset.id
                })
                self.write(cr, uid, asset.id, {'move_id': move_id}, context=context)
                created_move_ids.append(move_id)
                asset_ids.append(asset.id)

            # we re-evaluate the assets to determine whether we can close them
            for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
                if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
                    asset.write({'state': 'close'})

            account_asset_obj.write(cr, uid, asset_id, {'state': 'close'}, context=context)

#            return created_move_ids
        self.write(cr, uid, ids, {'state': 'validated', 'validator': uid, 'stage': 'validated'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel',
                                  'stage': 'cancel',
                                  'confirmer': False,
                                  'auditor': False,
                                  'receiver': False,
                                  'validator': False,
                                  'canceler': uid})

        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft',
                                  'stage': 'waiting_confirm',
                                  'confirmer': False,
                                  'auditor': False,
                                  'receiver': False,
                                  'validator': False,
                                  'canceler': uid})
        return True


    def onchange_asset(self, cr, uid, ids, asset_id, context=None):
        """On change method for the asset. Gets the department and company of
        origin of the asset."""
        account_asset_obj = self.pool.get('account.asset.asset')
        company_id = False
        account_analytic_id = False
        income_account_id = False
        if asset_id:
            asset_rec = account_asset_obj.browse(cr, uid, asset_id, context)
            if asset_rec.product_id:
                income_account_id = asset_rec.product_id.categ_id.property_account_income.categ.id \
                                    or asset_rec.product_id.property_account_income.id or False

            company_id = asset_rec.company_id.id
            account_analytic_id = asset_rec.account_analytic_id.id

            self.write(cr, uid, ids, {
                'origin_company': company_id,
                'origin_account_analytic_id': account_analytic_id,
                'income_account_id': income_account_id})
        return {'value': {'origin_company': company_id,
                               'origin_account_analytic_id': account_analytic_id,
                               'income_account_id': income_account_id}}

    @api.multi
    def unlink(self):
        for move in self:
            if move.state not in ('draft', 'cancel'):
                raise Warning(_('No puede eliminar un movimiento que no este en borrador o cancelado.'))
            #elif invoice.internal_number:
            #    raise Warning(_('You cannot delete an invoice after it has been validated (and received a number).
            # You can set it back to "Draft" state and modify its content, then re-confirm it.'))
        return super(AssetMove, self).unlink()


AssetMove()

class StockLocation(osv.osv):
    _inherit = "stock.location"
    _columns = {
        'internal_type': fields.selection(string="Tipo Interno",
                                          selection=[('pasillo', 'Pasillo'),
                                                     ('anaquel', 'Anaquel'),
                                              ('bandeja','Bandeja')], required=False),
    }


class ProductProduct(osv.osv):
    _inherit = "product.product"

    _sql_constraints = [

        ('default_code_uniq', 'unique(default_code)', 'Ya existe un producto con esta referencia interna')
    ]

class ProductTemplate(osv.osv):
    _inherit = "product.template"

    def check_code(self, cr, uid, ids, code=None, context=None):
        """ Se encarga de poner el codigo suministrado a MAYUSCULAS
        y al mismo tiempo elimina los espacion en blanco y los puntos
        al principio del codigo.
        """

        if code:
            new_code = ''

            list_code = list(code)
            while list_code[0] == ' ' or list_code[0] == '.':
                del list_code[0]

            new_code = new_code.join(list_code)

            codigo = 'code_cups' if context == 1 else 'code_simons' if context == 2 else False

            return {'value':{
                codigo: new_code.upper(),
            }}

    _columns = {
        'fixed_asset': fields.boolean(string="Es Activo Fijo"),
        'asset_category_id': fields.many2one('account.asset.category', 'Asset Category',
                                             domain=[('type','=','normal')]),
        'loc_rack': fields.many2one('stock.location', string='Pasillo', domain=[('internal_type','=','pasillo')]),
        'loc_row': fields.many2one('stock.location', string='Anaquel', domain=[('internal_type','=','anaquel')]),
        'loc_case': fields.many2one('stock.location', string='Bandeja', domain=[('internal_type','=','bandeja')]),

        'code_cups': fields.char('Codigo CUPS'),
        'code_simons': fields.char('Codigo SIMONS'),

    }

class AssetAsset(osv.osv):
    _inherit = "asset.asset"

    _defaults = {
        'asset_number': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'asset.asset.number')
    }

class AccountAssetCategory(osv.osv):
    _order = "parent_left"
    _name = 'account.asset.category'
    _inherit = 'account.asset.category'

    def _get_children(self, cr, uid, ids, context=None):

        ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        if ids3:
            ids3 = self._get_children(cr, uid, ids3, context)
        return ids2 + ids3

    def _get_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []
        return result

    def _get_level(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for category in self.browse(cr, uid, ids, context=context):
            level = 0
            parent = category.parent_id
            while parent:
                level += 1
                parent = parent.parent_id
            res[category.id] = level
        return res

    _columns = {
        'type': fields.selection(string="Tipo Interno", selection=[('view', 'View'),
                                                                   ('normal', 'Normal'), ], required=True),
        'parent_id': fields.many2one("account.asset.category", string="Categoria Padre",
                                     required=False, ondelete='cascade', domain=[('type','=','view')]),
        'child_parent_ids': fields.one2many("account.asset.category", "parent_id", string="Hijos", required=False, ),
        'child_id': fields.function(_get_child_ids, type='many2many', relation="account.asset.category",
                                    string="Categoria(s) Hijas"),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'level': fields.function(_get_level, string='Nivel', method=True, type='integer',
                                 store={'account.asset.category': (_get_children, ['level', 'parent_id'], 10), }),

    }

    _defaults = {
        'type': 'normal',
    }


class account_asset(osv.osv):
    _inherit = 'account.asset.asset'

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name','')
            code = context.get('display_asset_code', True) and d.get('asset_code',False) or False
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)

        # partner_id = context.get('partner_id', False)
        # if partner_id:
        #     partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id, context=context).commercial_partner_id.id]
        # else:
        #     partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for asset in self.browse(cr, SUPERUSER_ID, ids, context=context):
            # variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = asset.name
            # sellers = []
            # if partner_ids:
            #     sellers = filter(lambda x: x.name.id in partner_ids, product.seller_ids)
            # if sellers:
            #     for s in sellers:
            #         seller_variant = s.product_name and (
            #             variant and "%s (%s)" % (s.product_name, variant) or s.product_name
            #             ) or False
            #         mydict = {
            #                   'id': product.id,
            #                   'name': seller_variant or name,
            #                   'default_code': s.product_code or product.default_code,
            #                   }
            #         result.append(_name_get(mydict))
            # else:
            mydict = {
                      'id': asset.id,
                      'name': name,
                      'asset_code': asset.asset_code,
                      }
            result.append(_name_get(mydict))
        return result

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            ids = []
            if operator in positive_operators:
                ids = self.search(cr, user, [('asset_code','=',name)]+ args, limit=limit, context=context)
                # if not ids:
                #     ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
            if not ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = self.search(cr, user, args + [('asset_code', operator, name)], limit=limit, context=context)
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(ids)) if limit else False
                    ids += self.search(cr, user, args + [('name', operator, name), ('id', 'not in', ids)], limit=limit2, context=context)
            elif not ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                ids = self.search(cr, user, args + ['&', ('asset_code', operator, name), ('name', operator, name)], limit=limit, context=context)
            if not ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('asset_code','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        res = {'value':{}}
        asset_categ_obj = self.pool.get('account.asset.category')
        if category_id:
            category_obj = asset_categ_obj.browse(cr, uid, category_id, context=context)
            res['value'] = {
                            'method': category_obj.method,
                            'method_number': category_obj.method_number,
                            'method_time': category_obj.method_time,
                            'method_period': category_obj.method_period,
                            'method_progress_factor': category_obj.method_progress_factor,
                            'method_end': category_obj.method_end,
                            'prorata': category_obj.prorata,
                            'category_parent_id': category_obj.parent_id
            }
        return res
    '''
    def onchange_asset_category(self,cr, uid, ids, category_id, context=None):
        account_asset_cat_obj = self.pool.get('account.asset.category')
        parent_id = False
        if category_id:
            category_id_rec = account_asset_cat_obj.browse(cr, uid, category_id, context)
            parent_id = category_id_rec.parent_id.id
            self.write(cr, uid, ids, {
                'category_parent_id': parent_id
            })
        return {'value': {'category_parent_id': parent_id}}
    '''
    
    def get_period(self, cr, uid, id, context=None):
        """Retrieves the period corresponding to the passed depreciation
        line and returns its id."""
        period_obj = self.pool.get('account.period')
        depreciation_obj = self.pool.get('account.asset.depreciation.line')
        depre_date = depreciation_obj.browse(cr, uid, id,
                                             context).depreciation_date.split('-')
        period_id = period_obj.search(cr, uid,
                                      [('code', '=', '{0}/{1}'.format(depre_date[1], depre_date[0]))],
                                      limit=1)
        try:
            return period_id[0]
        except IndexError, e:
            return False

    def prepare_account_move(self, cr, uid, depreciation_line_id, period_id, context=None):
        """Setup values to create a new account move based in asset depreciation line

        Args:
            depreciation_line_id; int
            period_id; int

        Return:
            dictionary
            """
        asset_line_obj = self.pool.get('account.asset.depreciation.line')
        asset_line = asset_line_obj.browse(cr, uid, depreciation_line_id, context)
        asset_name = asset_line.name.encode('utf-8')
        res = {
            'name': asset_name,
            'period_id': period_id,
            'state': 'posted',
            'ref': asset_name,
            'date': date.today().isoformat(),
            'journal_id': asset_line.asset_id.category_id.journal_id.id,
            'company_id': asset_line.asset_id.company_id.id
        }
        return res

    def prepare_move_line(self, cr, uid, line_id, move_id, period_id,
                          move_type, context=None):
        """Returns the values to create an account move line.

        Args:
            line_id; depreciation line id
            move_id; parent account.move id
            type; string; debit or credit

        Returns:
            {field: value}
        """
        line_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        line = line_obj.browse(cr, uid, line_id, context)
        company_currency = line.asset_id.company_id.currency_id.id
        asset_currency = line.asset_id.currency_id.id
        amount = currency_obj.compute(cr, uid, asset_currency, company_currency,
                                      line.amount, context)
        sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
        amount_currency = (company_currency != asset_currency and - sign *
                           line.amount or 0.0)
        if move_type == 'debit':
            debit, credit = amount, 0.0
            account = line.asset_id.category_id.account_depreciation_id.id
            asset = None
        else:
            debit, credit = 0.0, amount
            account = line.asset_id.category_id.account_expense_depreciation_id.id
            asset = line.asset_id.id
        values = {
            'name': line.asset_id.name.encode('utf-8'),
            'partner_id': line.asset_id.partner_id.id,
            #LOV Python
            'debit': debit and credit or credit,
            'credit': debit and credit or debit,
            'move_id': move_id,
            'ref': line.name.encode('utf-8'),
            'account_id': account,
            'journal_id': line.asset_id.category_id.journal_id.id,
            'currency_id': company_currency != asset_currency and asset_currency or False,
            'date': date.today().isoformat(),
            'amount_currency': amount_currency,
            'period_id': period_id,
            'asset_id': asset,
            'company_id': line.asset_id.company_id.id,
        }
        return values

    def get_asset_ids(self, cr, context=None):
        """Retrieve the assets using SQL for a better performance."""
        query = """SELECT id from {0} WHERE active = True and state like 'open'"""
        query = query.format(self._table)
        cr.execute(query)
        ids = [asset[0] for asset in cr.fetchall() if asset]
        return ids

    def run_asset_entry(self, cr, uid, context=None):
        """Method that checks all lines in the model account asset
        deprecated and if the date is equal or greater than today it
        creates the account entry with the status settled.

        Args:
            cr, uid, ids, context

        Return:
            List of created account moves
        """

        logging.getLogger(self._name).info("Starting run_asset_entry cron job.")
        account_move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        asset_lines_obj = self.pool.get('account.asset.depreciation.line')
        ids = self.get_asset_ids(cr)

        counter = 0
        for asset in ids:

            asset = self.read(cr, uid, asset, context=context)

            for asset_line in asset.get('depreciation_line_ids'):

                today = date.today()
                asset_name = asset.get('name').encode('utf-8')
                asset_line = asset_lines_obj.read(cr, uid, asset_line)

                if asset_line.get('depreciation_date') <= today.isoformat() and not asset_line.get('move_check'):
                    period_id = self.get_period(cr, uid, asset_line.get('id'))
                
                    if not period_id:
                        company_name = asset.get('company_id')
                        logging.getLogger(self._name).error(
                            """No period found for the date {0}
                            and company {1}""".format(asset_line.get('depreciation_date'), company_name[1]))
                        break
                    try:
                        values = self.prepare_account_move(cr, uid, asset_line.get('id'), period_id, context)
                        created_id = account_move_obj.create(cr, uid, values, context)
                        logging.getLogger(self._name).info("""account.move created for {0}""".format(asset_name))
                    except:
                        logging.getLogger(self._name).error("Error creating account move {0}".format(asset_name))
                        raise orm.except_orm('Error', "Failure creating the account move object.")
                    try:
                        debit_values = self.prepare_move_line(cr, uid, asset_line.get('id'), created_id, period_id, 'debit')
                        credit_values = self.prepare_move_line(cr, uid, asset_line.get('id'), created_id, period_id, 'credit')
                        move_line_obj.create(cr, uid, debit_values, context)
                        move_line_obj.create(cr, uid, credit_values, context)
                        asset_lines_obj.write(cr, uid, asset_line.get('id'), {'move_check': True, 'move_id': created_id})
                        logging.getLogger(self._name).info("""account.move.line created for {0}""".format(asset_name))
                    except:
                        logging.getLogger('account.asset.asset').error(
                            """ERROR creating the entries of
                            account move from {0}.""".format(__name__))
                        raise orm.except_orm('Error', 'Failure creating the'
                            ' account move lines.')
                else:
                    logging.getLogger(self._name).info("Este activo ya esta asentado!")

    _columns = {
        'asset_code': fields.char('Codigo', size=32, store=True, readonly=True, copy=False),
        'category_id': fields.many2one('account.asset.category', 'Asset Category', required=True,
                                       change_default=True, readonly=True, states={'draft':[('readonly',False)]},
                                       domain=[('type','=','normal')]),
        'category_parent_id': fields.many2one("account.asset.category", string="Categoria Padre del Activo",
                                              required=False, readonly=True, states={'draft':[('readonly',False)]},
                                              domain=[('type','=','view')] ),
        'account_analytic_id': fields.many2one("account.analytic.account", string="Cuenta analitica",
                                               required=True, domain=[('type','=','normal')]),
        'asset_move_ids': fields.one2many('account.asset.move', 'asset_id','Movimientos'),
        'asignado': fields.many2one("hr.employee", "Asignado a"),
        'localizacion': fields.many2one("localizaciones", "Localizado"),
        'area': fields.many2one("areas", "Area"),
        'discharge_temporary': fields.boolean('Descargado Temporamente', readonly=True),
        'discharge_definitive': fields.boolean('Descargado Definitivamente', readonly=True),
        'product_id': fields.many2one("product.template", "Producto")
         
    }

    #_defaults = {
    #    'asset_code': 'xxxxx'
    #}

    def create(self, cr, uid, ids, context=None):
        """Sobrescribir el metodo crear para introducir el codigo del activo
        despues de guardar"""

        created_id = super(account_asset, self).create(cr, uid, ids, context)

        ids['asset_code'] = self.pool.get('ir.sequence').get(cr, uid, 'asset.number')

        self.write(cr, uid, created_id, ids, context)

        return created_id

class UpdateStockInventoryLineProductUoM(orm.Model):

    _inherit = 'stock.inventory'

    def UpdateStockInventoryLineProductUoM(self, cr, uid, ids, context=None):

        inv_obj = self.pool.get('stock.inventory')
        inv_line_obj = self.pool.get('stock.inventory.line')
        product_tmp_obj = self.pool.get('product.product')

        inv = inv_obj.search(cr, uid, [('state', '=', 'confirm')], context=context)

        for inventory in inv:

            inv_lines = inv_line_obj.search(cr, uid, [('inventory_id', '=', inventory)], context=context)
            inv_line = inv_line_obj.browse(cr, uid, inv_lines, context=context)

            for line in inv_line:
                product_tmp = product_tmp_obj.search(cr, uid, [('id', '=', line.product_id.id)], context=context)
                product = product_tmp_obj.browse(cr, uid, product_tmp, context=context)

                if product:
                    if line.product_uom_id.id != product.uom_id.id:
                        print True
                        inv_line_obj.write(cr, uid, line.id, {'product_uom_id': product.uom_id.id})
