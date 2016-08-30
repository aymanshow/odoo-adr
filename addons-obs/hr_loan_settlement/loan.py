from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime

class account_move(osv.osv):
    _inherit = 'account.move'
    
    _columns = { 
                'loan_id'   : fields.many2one('hr.loan','Loan',help='Loan Record'),
                }
    
class hr_loan(osv.osv):
    _name = "hr.loan"

    def _set_value(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr ,uid ,ids):
            res[line.id] = line.is_exceed
        return res
    
    def _set_depart(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr ,uid ,ids):
            res[line.id] = line.depart_id.id
        return res
    
    _columns = { 
                'name'                 : fields.char('Name',readonly=True,help='Sequence of loan'),
                'employee_id'          : fields.many2one('hr.employee','Employee', required=True,help='Employee Name'),
                'amount'               : fields.float('Amount', required=True,help='Amount of loan'),
                'start_date'           : fields.date('Date', required=True,help='date to Start the loan'),
                'reason'               : fields.text('Reason',help='Reason of loan'),
                'is_exceed'            : fields.boolean('Exceed the Maximum',help='True if the amount exceed the limit for employee'),
                'is_exceed_2'          : fields.function(_set_value,type="boolean",string='Exceed the Maximum', store=True,help=''),
                'payment_method'       : fields.many2one('loan.payments','Payment Method',help='Payment method for loan'),
                'state'                : fields.selection([('draft', 'Draft'),('cancel', 'Cancel'), ('approved', 'Approved')], 'Status'),
                'move_id'              : fields.many2one('account.move','Journal Entry',help='Journal Entry for loan'),
                'move_ids'             : fields.many2many('account.move','account_move_loan_rel','employee_id','loan_id','Journal Entries',help='Journal entries related to this loan'),
                'period_id'            : fields.many2one('account.period','Period',help='Period of loan'),
                'depart_id'            : fields.many2one('hr.department','Department',help='Department of employee'),
                'depart_id_2'          : fields.function(_set_depart,type="many2one",relation='hr.department',string='Department',store=True),
                'loan_line_ids'        : fields.one2many('hr.loan.line','loan_id','Loan Lines',help='When to pay the loan and amount of each date'),
                }
    
    _defaults = {
                'state'                :'draft',
                'start_date'           : lambda *a: time.strftime('%Y-%m-%d'),
                }
    
    def on_change_employee(self ,cr, uid ,ids ,employee_id ,context=None):
        employee = self.pool.get('hr.employee').browse(cr ,uid , employee_id)
        return {'value': {'depart_id': employee.department_id.id ,'depart_id_2': employee.department_id.id}}
    
    
    def unlink(self,cr ,uid, ids, context=None):
        loans = self.browse(cr ,uid ,ids ,context=context)
        for loan in loans:
            if loan.move_ids:
                raise osv.except_osv(_('Error!'),
                        _('You Can not Delete Loan/s that have Journal Entries .'))
                return False
        res = super(hr_loan,self).unlink(cr ,uid, ids, context=context)
        return res
    
    def approve_loan(self ,cr ,uid ,ids ,context=None):
        move_pool = self.pool.get('account.move')
        period_pool = self.pool.get('account.period')
        timenow = time.strftime('%Y-%m-%d')

        loan_slip = self.browse(cr ,uid ,ids)[0]
        line_ids = []
        # get period 
        ctx = dict(context or {}, account_period_prefer_normal=True)
        search_periods = period_pool.find(cr, uid, loan_slip.start_date, context=ctx)
        period_id = search_periods[0]
        
        # prepare account move data
        name = _('Loan for ') + (loan_slip.employee_id.name)
        move = {
            'narration': name,
            'date': timenow,
            'loan_id': loan_slip.id,
            'journal_id': loan_slip.payment_method.journal_id.id,
            'period_id': period_id,
        }
        
        amount = loan_slip.amount
        debit_account_id = loan_slip.payment_method.debit_account_id.id or False
        credit_account_id = loan_slip.payment_method.credit_account_id.id or False
        analytic_account_id = loan_slip.payment_method.analytic_account_id.id or False
        if not loan_slip.payment_method:
            raise except_orm(_('Error!'),
                                _('Please Set payment method'))
            
        if amount <= 0:
            raise except_orm(_('Error!'),
                                _('Please Set Amount'))
            
        if not loan_slip.payment_method.journal_id:
            raise except_orm(_('Error!'),
                                _('Please Set Journal For payment method'))
            
            
        if not credit_account_id or not debit_account_id:
            raise except_orm(_('Error!'),
                                _('Please Set credit/debit account '))
        
        
        if debit_account_id:
            debit_line = (0, 0, {
            'name': 'Loan',
            'date': timenow,
            'partner_id': False,
            'account_id': debit_account_id,
            'journal_id': loan_slip.payment_method.journal_id.id,
            'period_id': period_id,
            'debit': amount,
            'credit': 0.0,
            'analytic_account_id': analytic_account_id,
        })
            line_ids.append(debit_line)

        if credit_account_id:
            credit_line = (0, 0, {
            'name': 'Loan',
            'date': timenow,
            'partner_id': False,
            'account_id': credit_account_id,
            'journal_id': loan_slip.payment_method.journal_id.id,
            'period_id': period_id,
            'debit': 0.0,
            'credit': amount,
            'analytic_account_id': False,
        })
            line_ids.append(credit_line)

            
            
            move.update({'line_id': line_ids})
            move_id = move_pool.create(cr, uid, move, context=context)
            
            move_ids = []
            move_ids.append(move_id)
            for move_rec in loan_slip.move_ids:
                move_ids.append(move_rec.id)
            
            loan_name = loan_slip.name
            if not loan_slip.name:
                loan_name = self.pool.get('ir.sequence').get(cr, uid, 'hr.loan')
                
            self.write(cr, uid, [loan_slip.id], {'move_id': move_id, 'period_id' : period_id, 'move_ids': [(6, 0, move_ids)], 
                                                 'state': 'approved' , 'name': loan_name}, context=context)
            
            move_pool.post(cr, uid, [move_id], context=context)
            
        return True
    
    def create_inverse_entry(self ,cr ,uid ,line_ids ,move_id ):
        move_line_obj = self.pool.get('account.move.line')
        move_obj = self.pool.get('account.move')
        period_pool = self.pool.get('account.period')
        timenow = time.strftime('%Y-%m-%d')
        search_periods = period_pool.find(cr, uid, timenow)
        period_id = search_periods[0]
        
        res = {'move_id':False , 'line_ids': []}
        
        inv_move_id = move_obj.create(cr,uid ,{
                                'journal_id': move_id.journal_id.id,
                                'narration': _('Inverse: ')+move_id.narration,
                                'date': timenow,
                                'ref': move_id.ref,
                                'loan_id': move_id.loan_id.id,
                                'period_id': period_id,
                                 })
        res['move_id'] = inv_move_id
        for line in line_ids:
            analytic_account = False
            if line.analytic_account_id:
                analytic_account = line.analytic_account_id.id
            new_move_line = move_line_obj.create(cr ,uid ,{
                                        'name': line.name,
                                        'date': timenow,
                                        'partner_id': False,
                                        'account_id': line.account_id.id,
                                        'journal_id': line.journal_id.id,
                                        'period_id': period_id,
                                        'debit': line.credit,
                                        'credit': line.debit,
                                        'move_id': inv_move_id,
                                        'analytic_account_id': analytic_account,
            })
            res['line_ids'].append(new_move_line)
        move_obj.post(cr, uid, [inv_move_id])
        return res
    
    def cancel_loan(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        move_obj = self.pool.get('account.move')
        for loan_slip in self.browse(cr, uid, ids, context=context):
            if loan_slip.move_id:
                line_ids = move_line_obj.search(cr ,uid ,[('move_id','=',loan_slip.move_id.id)])
                lines = move_line_obj.browse(cr ,uid ,line_ids)
                data = self.create_inverse_entry(cr, uid, lines, loan_slip.move_id)
                move_ids = []
                move_ids.append(data['move_id'])
                for move_rec in loan_slip.move_ids:
                    move_ids.append(move_rec.id)
                self.write(cr, uid, [loan_slip.id], {'move_ids': [(6, 0, move_ids)],'state': 'cancel'}, context=context)

    def draft_loan(self, cr, uid, ids, context=None):
        for loan_slip in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [loan_slip.id], {'state': 'draft'}, context=context)
        return True
      
    def on_change_amount(self ,cr, uid ,ids ,amount ,employee_id ,start_date ,context=None):
        payslip_obj = self.pool.get('hr.payslip')
        employee = self.pool.get('hr.employee').browse(cr ,uid , employee_id)
        contract_id = payslip_obj.get_contract(cr, uid, employee, start_date, start_date)
        if contract_id:
            contract = self.pool.get('hr.contract').browse(cr ,uid ,contract_id)[0]
            if contract.date_end and contract.date_end < start_date:
                raise osv.except_osv(_('Error!'),
                                _('The Employee Out Of Work'))
            
            employee_salary = contract.wage

            loan_percentage = ((contract.struct_id.loan_percentage) * 0.01)
            
            
            if amount > (employee_salary*loan_percentage):
                warning = {
                        'title': _('Warning!'),
                        'message': _('Amount is Above the Maximum limits with Max. percentage loan '+str(contract.struct_id.loan_percentage))
                    }
                return {'value': {'is_exceed':True ,'is_exceed_2':True}, 'warning': warning}
        return {'value': {'is_exceed':False ,'is_exceed_2':False }}
        
        
    def create(self,cr ,uid ,vals ,context=None):
        employee = self.pool.get('hr.employee').browse(cr ,uid , vals['employee_id'])
        payslip_obj = self.pool.get('hr.payslip')
        contract_id = payslip_obj.get_contract(cr, uid, employee, vals['start_date'], vals['start_date'])
        date = datetime.strptime(vals['start_date'], '%Y-%m-%d').date()
        
        equel = self.check_amount_totals(cr ,uid ,False ,vals ,'create')
            
        if contract_id:
            contract = self.pool.get('hr.contract').browse(cr ,uid ,contract_id)[0]
            if not contract.date_end or contract.date_end > vals['start_date']:
                pass                
            else:
                raise osv.except_osv(_('Error!'),
                                _('The Employee Out Of Work'))
                
            
        res = super(hr_loan,self).create(cr ,uid ,vals ,context=context)
        self.check_previous_loans_payments(cr, uid, [res])
        return res
    
    def check_amount_totals(self ,cr ,uid ,ids ,vals ,type_op):
        if type_op == 'create':
            if vals.get('loan_line_ids',False):
                amount_total = 0.0
                for line in vals['loan_line_ids']:
                    amount_total += line[2]['amount']
                if amount_total != vals['amount']:
                    raise osv.except_osv(_('Error!'),
                        _('Total of Lines not equel to amount'))
        else:
            loan_line_obj = self.pool.get('hr.loan.line')
            current_loan = self.browse(cr ,uid ,ids)[0]
            amount_total = 0.0
            loan_amount = current_loan.amount
            if vals.has_key('amount'):
                loan_amount = vals['amount']
                
            if vals.has_key('loan_line_ids'):
                for line in vals['loan_line_ids']:
                    if type(line[2]) is dict and line[2].get('amount',0):
                        amount_total += line[2]['amount']
                    elif line[0] != 2:
                        amount_total += loan_line_obj.browse(cr ,uid ,line[1]).amount
            else:
                for line in current_loan.loan_line_ids:
                    amount_total += line.amount
            
            if amount_total != loan_amount:
                raise osv.except_osv(_('Error!'),
                    _('Total of Lines not equel to amount'))
        
    def write(self,cr ,uid ,ids ,vals ,context=None):
        if vals.has_key('loan_line_ids') or vals.has_key('amount'):
            equel = self.check_amount_totals(cr ,uid ,ids ,vals ,'write')
            
        if vals.get('start_date',False):
            current_loan = self.browse(cr ,uid ,ids)[0]
            payslip_obj = self.pool.get('hr.payslip')
            contract_id = payslip_obj.get_contract(cr, uid, current_loan.employee_id, vals['start_date'], vals['start_date'])
            date = datetime.strptime(vals['start_date'], '%Y-%m-%d').date()
            if contract_id:
                contract = self.pool.get('hr.contract').browse(cr ,uid ,contract_id)[0]
                if not contract.date_end or contract.date_end > vals['start_date']:
                    pass
                else:
                    raise osv.except_osv(_('Error!'),
                                    _('The Employee Out Of Work'))
                    
        if vals.get('amount',False):
            current_loan = self.browse(cr ,uid ,ids)[0]
            payslip_obj = self.pool.get('hr.payslip')
            contract_id = payslip_obj.get_contract(cr, uid, current_loan.employee_id, current_loan.start_date, current_loan.start_date)
            if contract_id:
                contract = self.pool.get('hr.contract').browse(cr ,uid ,contract_id)[0]
                loan_percentage = ((contract.struct_id.loan_percentage) * 0.01)
                employee_salary = contract.wage
                if vals['amount'] > (employee_salary*loan_percentage):
                    raise except_orm(_('Error!'),
                                _('Amount is Above the Maximum limits with Max. percentage loan '+str(contract.struct_id.loan_percentage)))
                    
        res = super(hr_loan,self).write(cr ,uid ,ids ,vals ,context=context)
        self.check_previous_loans_payments(cr, uid, ids)
        return res  
    
    def check_previous_loans_payments(self ,cr ,uid ,ids):
        current_loan = self.browse(cr ,uid ,ids)[0]
        loan_date = current_loan.start_date
        all_loans = self.search(cr ,uid ,[('employee_id','=',current_loan.employee_id.id),('id','!=',ids[0])])
        if all_loans:
            loan_lines = self.pool.get('hr.loan.line').search(cr ,uid ,[('loan_id','in',all_loans)]) 
            for line in self.pool.get('hr.loan.line').browse(cr ,uid ,loan_lines):
                if loan_date <= line.discount_date:
                    raise osv.except_osv(_('Error!'),
                        _('There is a loan in progress '+ str(line.loan_id.name)))
                
    def open_entries(self, cr, uid, ids, context=None):
        context = dict(context or {}, search_default_loan_id=ids, default_loan_id=ids)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context,
        }  
    
class hr_loan_lines(osv.osv):
    _name = "hr.loan.line"

    _columns = { 
                'loan_id': fields.many2one('hr.loan','Loan'),
                'discount_date'           : fields.date('Date', required=True, help='Date for discount the amount'),
                'amount'               : fields.float('Amount', required=True, help='Amount of each payment'),
                }
    
class hr_payroll_structure_inh(osv.osv):
    _inherit = "hr.payroll.structure"

    _columns = { 
                'loan_percentage'   : fields.integer('Max Loan Percentage (%)', required=True,help='Maximum percentage of loan for each structure'),
                }
     
class hr_payslip_inhe(osv.osv): 
    _inherit = 'hr.payslip'
     
    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        res = super(hr_payslip_inhe,self).onchange_employee_id(cr, uid, ids, date_from, date_to, employee_id=employee_id, contract_id=contract_id, context=context)
        loan_obj = self.pool.get('hr.loan')
        loan_line_obj = self.pool.get('hr.loan.line')
        loan_ids = loan_obj.search(cr ,uid ,[('employee_id','=',employee_id),('state','=','approved'),])
        loan_total = 0.0
        if loan_ids:
            for loan_id in loan_ids:
                line_ids = loan_line_obj.search(cr ,uid ,[('loan_id','=',loan_id),
                                                          ('discount_date','>=',date_from),
                                                          ('discount_date','<=',date_to)])
                if line_ids:
                    for loan in loan_line_obj.browse(cr ,uid ,line_ids):
                        loan_total += loan.amount
            
            vals = {'name': 'Loan', 'code': 'LOAN', 'amount': loan_total, 'contract_id': contract_id}
            res['value']['input_line_ids'].append(vals)
        return res
        
        
class loans_payments(osv.osv):
    _name = "loan.payments"

    _columns = { 
                'name'                 : fields.char('Name', required=True,help='Payment name'),
                'debit_account_id'     : fields.many2one('account.account','Debit Account', required=True,help='Debit account for journal entry'),
                'credit_account_id'    : fields.many2one('account.account','Credit Account', required=True,help='Credit account for journal entry'),
                'journal_id'           : fields.many2one('account.journal','Journal', required=True,help='Journal for journal entry'),
                'analytic_account_id'  : fields.many2one('account.analytic.account','Analytic Account',help='Analytic account for journal entry'),
                }        
    
        
        
        
        
        