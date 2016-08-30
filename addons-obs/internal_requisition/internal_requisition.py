
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Open Business Solutions (<http://www.obsdr.com>)
#    Author: Naresh Soni
#    Copyright 2015 Cozy Business Solutions Pvt.Ltd(<http://www.cozybizs.com>)
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
import time
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
import pdb

class res_company(models.Model):
    _inherit = 'res.company'

    ir_journal_id = fields.Many2one('account.journal', 'Expense Journal', required=False,
                                 domain="[('type','=','purchase')]",
                                 help='Journal related to stock Accounting Entries')

class internal_requisition(models.Model):
    _name = 'internal.requisition'
    _description = 'Internal Requisition'
    _inherit = 'mail.thread'

    @api.model
    def _get_default_warehouse(self):
        company_id = self.env['res.users']._get_company()
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        return warehouse_ids
    
    @api.depends('delivery_ids', 'delivery_ids.state')
    def get_need_rfq(self):
        need_rfq = False
        for do in self.delivery_ids:
            if do.state == 'confirmed':
                need_rfq = True
            elif do.state == 'partially_available':
                need_rfq = True
        self.need_rfq = need_rfq

    AVAILABLE_PRIORITIES = [
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
    ]

    name = fields.Char(string='Requisition Reference', readonly=True)
    date_start = fields.Date(string='Requisition Date', readonly=True,
                             states={'draft': [('readonly', False)]},
                             required=True, default=fields.Date.context_today)
    date_end = fields.Date(string='Requisition Deadline', readonly=True, copy=False,
                           states={'draft': [('readonly', False)]}, help='Last date for the product to be needed')
    date_done = fields.Datetime('Completed on', readonly=True, copy=False,
                                help="Date of Completion of Internal Requisition")
    user_id = fields.Many2one('res.users', string='Requester', readonly=True,
                              states={'draft': [('readonly', False)]}, required=True, default=lambda self: self.env.uid)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, required=True,
                                    states={'draft': [('readonly', False)]},
                                    help='Please configure department stock location on your department to delivery product from internal stock.')
    manager_id = fields.Many2one('hr.employee', string='Manager', readonly=True, required=True,
                                 states={'draft': [('readonly', False)]})
    warehouse_id = fields.Many2one('stock.warehouse',
                                   string='Warehouse',
                                   help="This warehouse's stock location will be used  to issue this internal requisition",
                                   required=False, readonly=True,
                                   default=_get_default_warehouse)
    description = fields.Text(string='Description', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id.id)
    line_ids = fields.One2many('internal.requisition.line', 'internal_requisition_id',
                               string='Products internally Requested', readonly=True,
                               states={'draft': [('readonly', False)]})
    location_id = fields.Many2one('stock.location', string='Source Location',
                                  help="This is the location from where the goods will be dispatched to the user",
                                  required=False, select=True)
    location_dest_id = fields.Many2one('stock.location', string='Destination Location',
                                       help="This is the location where the good will be received (i.e the user's department location)",
                                       required=False, select=True)
    purchase_ids = fields.One2many('purchase.order', 'internal_requisition_id',
                                   string='Purchase Orders', readonly=True, copy=False,)
    delivery_ids = fields.Many2many('stock.picking', 'stock_picking_internal_requisition_rel',
                                    'internal_requisition_id', 'picking_id', 'Pickings', copy=False)
    budget_ids = fields.Many2many('crossovered.budget', 'crossovered_budget_rel', 'internal_req_id',
                                  'budget_id', string='Budgets')
    need_rfq = fields.Boolean(compute='get_need_rfq', store=True,
                              string='Need RFQ', copy=False, help="If ticked that means you need RFQ for this request")
    journal_id = fields.Many2one('account.journal', 'Expense Journal', required=False, readonly=True,
                                 default=lambda self: self.env.user.company_id.ir_journal_id.id,
                                 domain="[('type','=','purchase')]", help='Journal related to stock Accounting Entries')
    state = fields.Selection([
                       ('draft', 'New'),
                       ('confirm', 'Confirmada'),
                       ('cancel', 'Cancelled'),
                       ('validate', 'Validada'),
                       ('approve_request', 'Aprobacion Solicitada'),
                       ('approve', 'Aprobada'),
                       ('recibido', 'Recibido'),
                       ('revertir', 'Revertir Transferencia'),
                       ('done', 'Done'), ], string='State', default='draft', required=True, readonly=True)
    stage = fields.Selection([
                        ('waiting_user_request', 'Esperando Confirmacion del Usuario'),
                        ('waiting_manager_validation', 'Esperando Validacion del Gerente'),
                        ('waiting_dir_ejec_approve_request', 'Esperando Solicitud de Aprobacion a Dir. Ejecutiva'),
                        ('waiting_dir_ejec_approval','Esperando Aprobacion Direccion Ejecutiva'),
                        ('delivery', 'Internal Order Generated - by Warehouse Department'),
                        ('accounting', 'To be Accounted - by Accounting Department'),
                        ('waiting', 'Waiting Availability - by Warehouse / Pucharse Departments'),
                        ('ready', 'Ready to Process - by Warehouse Department'),
                        ('to_be_receipt', 'Para ser recibido - por el Departamento y/o Usuario Solicitante'),
                        ('recibido', 'Recibido por el Departamento y/o Usuario Solicitante'),
                        ('cancel','Cancelado'),
                        ], string='Stage', default='waiting_user_request', required=True, readonly=True)
    po_created = fields.Boolean('PO created')

    priority = fields.Selection(string="Prioridad", selection=AVAILABLE_PRIORITIES, required=False, default='1')

    
    @api.one
    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'name':'',
            'state': 'draft',
            'budget_ids':False,
            'purchase_ids':False,
            'delivery_ids':False,
            })
        return super(internal_requisition, self).copy(default)
    
    @api.multi
    def onchange_user_id(self, user=False):
        if user:
            employee_obj = self.env['hr.employee']
            employee = employee_obj.search([('user_id', '=', user)], limit=1)
            if employee:
                return {'value':{'manager_id':employee.parent_id.id,
                                 'department_id':employee.department_id and employee.department_id.id or False,
                                 'location_dest_id':employee.department_id and employee.department_id.location_id.id or False}}
        return {}
    
    @api.onchange('department_id')
    def onchange_department_id(self):
        budget_ids = []
        if self.department_id:
            analytic_account_obj = self.env['account.analytic.account']
            budget_line_obj = self.env['crossovered.budget.lines']
            analytic_ids = analytic_account_obj.search([('department_id', '=', self.department_id.id)])
            if analytic_ids:
                budget_lines = budget_line_obj.search([('analytic_account_id', 'in', analytic_ids.ids),('crossovered_budget_id.state','=','validate')])
                for budget_line in budget_lines:
                    if budget_line.crossovered_budget_id.id not in budget_ids:
                        budget_ids.append(budget_line.crossovered_budget_id.id)
        self.budget_ids = [[6, 0, budget_ids]]
    
    @api.multi
    def confirm(self):
        seq_no = self.env['ir.sequence'].get('internal.requisition')
        for intreq in self:
            if not intreq.line_ids:
                raise Warning(_('Error !'), _('You should at least have one product line to confirm this Requisition !'))
            intreq.line_ids.action_confirm1()
        return self.write({'state':'confirm', 'name': seq_no, 'stage': 'waiting_manager_validation' })
    
    @api.multi
    def cancel(self):
        for intreq in self:
            intreq.line_ids.action_cancel()
        return self.write({'state':'cancel'})
    
    @api.multi
    def action_accounting(self):
        #import pdb; pdb.set_trace()
        for intreq in self:
            intreq.line_ids.action_accounting()
        self.accounting_entry()
        return self.write({'stage':'to_be_receipt'})

    
    def test_lines_done(self, picks):
        for pick in picks:
                if pick.state != 'done':
                    return False
        return True
    
    @api.multi
    def create_DO(self):
        #pdb.set_trace()
        for req in self:
            if not req.department_id:
                raise Warning(_('Error !'), _('Please Define a Department !'))
            location_id = req.warehouse_id.lot_stock_id.id
            output_id = req.department_id.location_id.id
            journals = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
            if not output_id:
                raise Warning(_('Error !'), _("Please Define an Input location for Department '%s' !") % (req.department_id.name))
            date_planned = (datetime.strptime(time.strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT) - \
                        timedelta(days=req.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            
            move_ids = []
            move_obj = self.env['stock.move']
            type_obj = self.env['stock.picking.type']
            pick_type = type_obj.search([('code', 'in', ['outgoing','incoming']), ('name','ilike','Requisicion Interna'),('warehouse_id', '=', req.warehouse_id.id)], limit=1)
            ir_seq_name = self.env['ir.sequence'].get_id(pick_type.sequence_id.id, 'id')
            for line in req.line_ids:
                if line.product_id.product_tmpl_id.property_account_expense:
                    expense_account_id = line.product_id.product_tmpl_id.property_account_expense.id or False
                else:
                    if line.product_id.categ_id.property_account_expense_categ:
                        expense_account_id = line.product_id.categ_id.property_account_expense_categ.id or False
                prod_name = line.product_id.name_get()
                vals = {
                    'name': prod_name and prod_name[0][1],
                    'product_id': line.product_id.id,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.product_uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': output_id,
                    'tracking_id': False,
                    'state': 'draft',
                    'expense_account_id':expense_account_id,
                    'company_id': req.company_id.id,
                    'price_unit': line.price_unit,
                    'internal_requisition_line_id': line.id,
                    'departamento': self.department_id.id,
                }
                
                move_ids.append(int(move_obj.create(vals)))
            if len(move_ids):
                vals_pick = {
                    'name':ir_seq_name,
                    'origin':req.name,
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'picking_type_id': pick_type and pick_type.id or False,
                    'journal_id': journals and journals.id or False,
                    'company_id': req.company_id.id,
                    'move_lines': [(6, 0, move_ids)],
                    'internal_requisition_id': req.id,
                    'state':'draft',
                    'departamento': self.department_id.id,
                }
                picking_id = self.env['stock.picking'].create(vals_pick)
                self.write({'delivery_ids': [(6, 0, [picking_id.id])]})
                picking_id.action_confirm()
                picking_id.action_assign()
        return True
    
    @api.multi
    def process(self):
        self.create_DO()
        state = 'approve'
        self.write({'state':state, 'stage':'delivery'})
        return True

    @api.multi
    def recibido(self):
        return self.write({'state': 'recibido', 'stage': 'recibido'})

    @api.multi
    def revertir(self):
        pass

    @api.multi
    def done(self):
        count = True
        for intreq in self:
            for do in intreq.delivery_ids:
                if do.state != 'done':
                    count = False
        count = count and self.test_lines_done(self.delivery_ids)
        if count:
            self.write({'state':'done', 'date_done':time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
    @api.multi
    def reset(self):
        for intreq in self:
            intreq.line_ids.action_draft()
        self.write({'state':'draft'})
        return True
    
    @api.one
    def check_budget(self, raise_warning=False):
        #pdb.set_trace()
        if self.budget_ids:
            if self.department_id.budget_limit:
                return True
            analytic_ids = self.env['account.analytic.account'].search([('department_id', '=', self.department_id.id)])
            budget_lines = self.env['crossovered.budget.lines'].search([('analytic_account_id', 'in', analytic_ids.ids)])
            planned = 0.0
            actual = 0.0
            for budget_line in budget_lines:
                planned +=  budget_line.planned_amount
                actual += budget_line.practical_amount
            order_total = 0.0
            for line in self.line_ids:
                order_total += line.amount_total
            if actual > planned or order_total > planned:
                if raise_warning:
                    raise Warning(_('Warning !'),_('There is an insufficient Budget for %s !'%(self.department_id.name)))
                return False
        else:
            if raise_warning:
                raise Warning(_('Warning !'),_('No budget Found for %s  Department !'%(self.department_id.name)))
            return False
        return True

    @api.one
    def receipt(self):
        self.write({'state':'done'})
        return True

    @api.one
    def approve(self):
        self.check_budget()
        self.process()
        return True

    @api.one
    def approve_request(self):
        self.check_budget()
        #self.check_budget(raise_warning=True)
        #self.process()
        #self.perform_approve()
        self.write({'state':'approve_request', 'stage': 'waiting_dir_ejec_approval'})
        return True

    @api.one
    def perform_approve(self):
        self.line_ids.action_approve()
        #self.process()
        self.write({'state':'approve_request'})
        return True

    @api.one
    def perform_approve_with_budget(self):
        self.line_ids.action_approve()
        self.process()
        #self.write({'state':'approve'})
        return True

    @api.one
    def validate(self):
        res = self.check_budget()
        if res[0]:
            return self.perform_approve_with_budget()
        else:
            #return self.perform_approve()
            self.line_ids.action_validate()
            self.write({'state':'validate', 'stage': 'waiting_dir_ejec_approve_request'})
        return True
    
    @api.multi
    #TODO (Revisar esto, entradas contables inversas)
    def accounting_entry(self):
        move_pool = self.env['account.move']
        period_pool = self.env['account.period']
        for requisition in self:
            if not requisition.journal_id:
                raise Warning(_('Error !'), _('Please Define an Expense Journal !'))
            
            analytic_account_id = False
            if requisition.budget_ids:
                cross_budget_line = requisition.budget_ids[0].crossovered_budget_line and requisition.budget_ids[0].crossovered_budget_line[0] or False
                if cross_budget_line.analytic_account_id:
                    analytic_account_id = cross_budget_line.analytic_account_id.id 
                    
            timenow = time.strftime('%Y-%m-%d')
            period_id = period_pool.find(timenow)[0]
            acc_move = {
                'narration': requisition.name,
                'date': timenow,
                'ref': requisition.name,
                'journal_id': requisition.journal_id.id,
                'period_id': period_id.id,
                'state':'posted',
            }
            final_list = []
            for line in requisition.line_ids:
                credit_account_id = False
                if line.product_id.product_tmpl_id.property_account_expense:
                    credit_account_id = line.product_id.product_tmpl_id.property_stock_account_output.id or False
                else:
                    if line.product_id.categ_id.property_account_expense_categ:
                        credit_account_id = line.product_id.categ_id.property_stock_account_output_categ.id or False

                if line.product_id.product_tmpl_id.property_stock_account_output:
                    debit_account_id = line.product_id.product_tmpl_id.property_account_expense.id or False
                else:
                    if line.product_id.categ_id.property_stock_account_output_categ:
                        debit_account_id = line.product_id.categ_id.property_account_expense_categ.id or False
                        
                if not debit_account_id:
                    raise Warning(_('Error !'), _('Please define an Internal Issues Account for line with product (%s) !') % (line.product_id.name))
                if not credit_account_id:
                    raise Warning(_('Error !'), _('Please Define an Inventory Account for line with product (%s) !') % (line.product_id.name))
                reference_amount = line.product_id.price_get('standard_price')[line.product_id.id]
                credit_line = (0, 0, {
                        'name': _('IR for %s') % (line.product_id.name),
                        'date': timenow,
                        'account_id': credit_account_id,
                        'journal_id':  requisition.journal_id.id,
                        'period_id': period_id.id,
                        'debit': 0.0,
                        'analytic_account_id': analytic_account_id,
                        'credit':reference_amount * line.product_qty,
                    })
                debit_line = (0, 0, {
                    'name': _('IR for %s') % (line.product_id.name),
                    'date': timenow,
                    'account_id': debit_account_id,
                    'journal_id': requisition.journal_id.id,
                    'period_id': period_id.id,
                    'debit': reference_amount * line.product_qty,
                    'analytic_account_id': analytic_account_id,
                    'credit': 0.0,
                })
                final_list += [credit_line, debit_line]
            acc_move.update(line_id=final_list)
            
            move_id = move_pool.create(acc_move)
            if requisition.journal_id.entry_posted:
                move_id.post()
            requisition.done()
            requisition.line_ids.action_done()
        return True

    @api.multi
    #TODO (Revisar esto, entradas contables inversas)
    def accounting_entry_return(self):
        move_pool = self.env['account.move']
        period_pool = self.env['account.period']
        print 'entro'
        for requisition in self:
            if not requisition.journal_id:
                raise Warning(_('Error !'), _('Please Define an Expense Journal !'))

            analytic_account_id = False
            if requisition.budget_ids:
                cross_budget_line = requisition.budget_ids[0].crossovered_budget_line and requisition.budget_ids[0].crossovered_budget_line[0] or False
                if cross_budget_line.analytic_account_id:
                    analytic_account_id = cross_budget_line.analytic_account_id.id

            timenow = time.strftime('%Y-%m-%d')
            period_id = period_pool.find(timenow)[0]
            acc_move = {
                'narration': requisition.name,
                'date': timenow,
                'ref': requisition.name,
                'journal_id': requisition.journal_id.id,
                'period_id': period_id.id,
            }
            final_list = []
            for line in requisition.line_ids:
                credit_account_id = False
                if line.product_id.product_tmpl_id.property_account_expense:
                    credit_account_id = line.product_id.product_tmpl_id.property_stock_account_output.id or False
                else:
                    if line.product_id.categ_id.property_account_expense_categ:
                        credit_account_id = line.product_id.categ_id.property_stock_account_output_categ.id or False

                if line.product_id.product_tmpl_id.property_stock_account_output:
                    debit_account_id = line.product_id.product_tmpl_id.property_account_expense.id or False
                else:
                    if line.product_id.categ_id.property_stock_account_output_categ:
                        debit_account_id = line.product_id.categ_id.property_account_expense_categ.id or False

                if not debit_account_id:
                    raise Warning(_('Error !'), _('Please define an Internal Issues Account for line with product (%s) !') % (line.product_id.name))
                if not credit_account_id:
                    raise Warning(_('Error !'), _('Please Define an Inventory Account for line with product (%s) !') % (line.product_id.name))
                reference_amount = line.product_id.price_get('standard_price')[line.product_id.id]

                credit_line = (0, 0, {
                        'name': _('IR for %s') % (line.product_id.name),
                        'date': timenow,
                        'account_id': debit_account_id,
                        'journal_id':  requisition.journal_id.id,
                        'period_id': period_id.id,
                        'debit': 0.0,
                        'analytic_account_id': analytic_account_id,
                        'credit':reference_amount * line.product_qty,
                    })
                debit_line = (0, 0, {
                    'name': _('IR for %s') % (line.product_id.name),
                    'date': timenow,
                    'account_id': credit_account_id,
                    'journal_id': requisition.journal_id.id,
                    'period_id': period_id.id,
                    'debit': reference_amount * line.product_qty,
                    'analytic_account_id': analytic_account_id,
                    'credit': 0.0,
                })
                final_list += [credit_line, debit_line]
            acc_move.update(line_id=final_list)

            move_id = move_pool.create(acc_move)
            if requisition.journal_id.entry_posted:
                move_id.post()
            requisition.done()
            requisition.line_ids.action_done()
        return True


class internal_requisition_line(models.Model):
    _name = 'internal.requisition.line'
    _description = 'Internal Requisition Line'
    _rec_name = 'product_id'
    
    
    @api.one
    @api.depends('price_unit', 'product_qty')
    def _amount_total(self):
        self.amount_total = self.price_unit * self.product_qty
        
    product_id = fields.Many2one('product.product', 'Product',
                                 domain="[('type','!=','service'),('categ_id.available_for_ir','=',True)]",
                                 required=True)
    product_uom_id = fields.Many2one('product.uom', 'Product UoM', readonly=False)
    product_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoM'), default=1.0)
    internal_requisition_id = fields.Many2one('internal.requisition', 'Internal Requisition', ondelete='cascade')
    note = fields.Text('Notes')
    price_unit = fields.Float('Unit Price', digits=dp.get_precision('Account'))
    state = fields.Selection([('draft', 'New'),
                              ('confirm1', 'Confirmed'),
                              ('valid', 'Validated'),
                              ('accounting', 'To be Accounted'),
                              ('approve', 'Approved by Department'),
                              ('confirmed', 'Waiting Availability'),
                              ('assigned', 'Available'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')], 'State', readonly=True, select=True, default='draft')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env['res.company']._company_default_get('internal.requisition.line'))
    purchase_ids = fields.One2many('purchase.order', 'internal_requisition_line_id', 'Purchase Orders', readonly=True)
    amount_total = fields.Float(compute='_amount_total', readonly=True, digits=dp.get_precision('Account'), string='Total')
    

    po_created = fields.Boolean('PO created')

    @api.multi
    def onchange_product_id(self, prod_id=False):
        if not prod_id:
            return {}
        product = self.env['product.product'].browse(prod_id)
        return {'value': {
            'product_uom_id': product.uom_id.id,
            'product_qty': 1.00,
            'price_unit':product.product_tmpl_id.standard_price
        }}
    
    @api.multi
    def action_cancel(self):
        return self.write({'state':'cancel'})
    
    @api.multi
    def action_done(self):
        return self.write({'state':'done'})
    
    @api.multi
    def action_accounting(self):
        return self.write({'state':'accounting'})
    
    @api.multi
    def action_approve(self):
        return self.write({'state': 'approve'})
    
    @api.multi
    def action_confirm1(self):
        return self.write({'state': 'confirm1'})
    
    @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirmed'})
    
    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def force_assign(self):
        return self.write({'state': 'assigned'})
    
    @api.multi
    def action_validate(self):
        return self.write({'state': 'valid'})
    
    @api.multi
    def cancel_assign(self):
        return self.write({'state': 'confirmed'})

class hr_department(models.Model):
    _inherit = 'hr.department'

    location_id = fields.Many2one('stock.location', 'Department Stock Location',
                                  help='Select internal stock location for internal requisition deliveries from warehouse.')
    budget_limit = fields.Boolean('Allow to pass Budget Limit')
    
class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    internal_requisition_id = fields.Many2one('internal.requisition', 'Internal Requisition', ondelete='cascade')
    journal_id = fields.Many2one('account.journal', 'Expense Journal', required=False, domain="[('type','=','purchase')]",
                                 help='Journal related to stock Accounting Entries')
    po_created = fields.Boolean('PO created')
    
    @api.multi
    def action_done(self):
        for rec in self:
            if rec.internal_requisition_id:
                return self.write({'stage': 'accounting'})#, 'name':rec.temp_name})
        return super(stock_picking, self).action_done()

    @api.multi
    def action_cancel(self):

        id = self.internal_requisition_id.id

        requisition = self.env['internal.requisition'].search([['id','=',id]])
        requisition.write({'state': 'cancel'})

        return super(stock_picking, self).action_cancel()

class product_category(models.Model):
    _inherit = 'product.category'
    available_for_ir = fields.Boolean(help="Marcar si los productos en esta categoria estaran disponible para Requisiciones Internas", string="Disponible para Requisicion Interna",)

class stock_move(models.Model):
    _inherit = 'stock.move'
    picking_type_code = fields.Selection(related='picking_type_id.code', string='Picking Type Code')
    po_created = fields.Boolean('PO created')
    internal_requisition_line_id = fields.Many2one('internal.requisition.line', 'Internal Requisition Line')

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    internal_requisition_line_id = fields.Many2one('internal.requisition.line', 'Internal Requisition line', ondelete='cascade')
    internal_requisition_id = fields.Many2one('internal.requisition', 'Internal Requisition', ondelete='cascade')

