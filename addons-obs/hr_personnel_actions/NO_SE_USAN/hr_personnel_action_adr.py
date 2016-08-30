# -*- coding: utf-8 -*-
"""
Created on Mon Noc 23 3:42:00 2015

@author: Ramon Caraballo.
"""
import datetime

from openerp.osv import osv, fields


class HrEmployee(osv.osv):
    """Class that inherits from hr.employee and extends the model with 4 fields."""
    _name='hr.employee'
    _inherit='hr.employee'
    _columns = {
    'salary_scale_category':fields.selection((('1','1'),('2','2'),('3','3'),
                                                ('4','4'),('5','5'),('6','6'),
                                                ('7','7'),('8','8'),('9','9'),
                                                ('10','10'),('11','11'),
                                                ('12','12'),('13','13'),
                                                ('14','14'),('15','15'),
                                                ('16','16'),('17','17'),
                                                ('18','18'),('19','19'),
                                                ('20','20'),('21','21'),
                                                ('22','22'),('23','23'),
                                                ('24','24'),('25','25')), 'Salary Scale Category'),

    'salary_scale_level':fields.selection((('1','1'),('2','2'),('3','3'),
                                           ('4','4'),('5','5'),
                                           ('6','6')), 'Salary Scale Level'),

    #'personnel_actions_ids':fields.one2many('hr.personnel.action',
    #                                        'employee_id',
    #                                        'Personnel actions'),

    'transfer_to':fields.selection((('1','UAPA Santiago'),
                                    ('2','UAPA Santo Domingo'),
                                    ('3','UAPA Nagua'),
                                    ('4','CEGES Santo Domingo'),
                                    ('5','CEGES Santiago')), 'Transfererido a '),

    'on_vacation':fields.boolean('On vacation'),
    'on_licence':fields.boolean('On licence'),
    'proposed_misconduct':fields.text('Amonestacion'),
    'proposed_misconduct_level':fields.selection((('1','1'),('2','2'),
                                                  ('3','3')), 'Nivel falta cometida'),

    }

HrEmployee()


class HrContract(osv.osv):
    """Class extends the hr.contract model with 1 field."""
    _name="hr.contract"
    _inherit="hr.contract"
    _columns = {
        'diff_scale':fields.float('Diff. Scale', size=16),
        }

HrContract()


class HrPersonnelAction(osv.osv):
    """Create a new model that stores all personnel actions.

    Inherit: hr_personnel_action
    """
    _name='hr.personnel.action'
    _description="Hr Personnel Action"

    def get_wage(self, cr, uid, employee_id, context=None):
        hr_contract_obj = self.pool.get('hr.contract')
        hr_obj = self.pool.get('hr.employee')

        if employee_id:
            hr_cont_id = hr_contract_obj.search(cr, uid, [('employee_id','=',employee_id)], order='id', context = None)

            emp_cont = hr_contract_obj.browse(cr, uid, hr_cont_id[-1], context=None)
            return {'value': {'proposed_wage':emp_cont.wage}}
        else:
            return {}

    def calc_actual_total(self, cr, uid, ids, field_name, args, context=None):
        """Calculates the sum of the wage and the diff_scale

        Returns: Dictionary{id:value}"""

        result = {}
        for record in self.browse(cr, uid, ids, context=None):
            result[record.id] = record.actual_diff_scale + record.actual_wage
        return result

    def calc_proposed_total(self, cr, uid, ids, field_name, args, context=None):
        """Calculates the sum of the wage and the diff_scale

        Returns: Dictionary{id:value}"""
        result = {}
        records = self.browse(cr, uid, ids, context=None)
        for record in records:
            result [record.id] = record.proposed_wage + record.proposed_diff_scale
        return result

    def calc_employee_leave_total(self, cr, uid, ids, field_name, args, context=None):
        """Calculates the sum of the 3 fields of employee benefits.

        Returns Dictionary{id:value}"""
        result = {}
        records = self.browse(cr, uid, ids, context=None)
        for record in records:
            result[record.id] = record.severance + record.forewarning + record.christmas_salary
        return result

    def calc_number_of_days(self, cr, uid, ids, from_date, to_date, context=None):
        """Calculates the time beetwen two dates.

        Arguments:
        from_date -- start date, type string
        to_date -- end date, type string

        Returns: integer"""
        to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')
        from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.date(to_date.year, to_date.month, to_date.day)
        from_date = datetime.date(from_date.year, from_date.month, from_date.day)
        days = to_date - from_date
        num_of_days = str(days)[:-14]

        return int(num_of_days)

    def get_actions_ids(self, cr, uid, context=None):
        actions_ids = self.search(cr, uid, [('states','=','approved')], context=None)
        return actions_ids

    def run_personnel_actions(self, cr, uid, ids=None, context=None):

        """Runs a determined action on the date set in the field effective_date.
        Returns None"""

        #If the code is called from the form, ids is the id of the record active.
        #If is called from the cron job, this function get all records ids.

        if not ids:
            ids = self.get_actions_ids(cr, uid, context=None)
            ret = {}
        for contract in self.read(cr, uid, ids, ['contract_id'], context=context):
            ret = contract
        #This variables holds the objects we are going to be using in each action.
        hr_obj = self.pool.get('hr.employee')
        hr_cont_obj = self.pool.get('hr.contract')
        hr_holiday = self.pool.get('hr.holidays')
        hr_pay_obj = self.pool.get('hr.payslip')
        hr_payslip_obj = self.pool.get('hr.payslip.input')

        #List with all the records for the object hr.personnel.action
        #actions_ids = self.search(cr, uid, [('states','=','approved')], context=None)
        #Object that access all the records. actions_ids is the list with all my ids.
        actions = self.browse(cr, uid, ids, context=None)

        #Loop for traversing all records in the hr.personnel.action table and if the status is for approved and the date is today, run them.
        for action in actions:
            #These variables hold the ids of the contract and payroll associated to the employee.
            hr_cont_id = hr_cont_obj.search(cr, uid, [('employee_id', '=', action.employee_id.id)],
                                            order='id', context=None)
            hr_pay_id = hr_pay_obj.search(cr, uid, [('employee_id', '=', action.employee_id.id)],
                                          order='id', context=None)

            #This converts the date of the record to a format that can be evaluated.
            effective_date = datetime.datetime.strptime(action.effective_date, '%Y-%m-%d')
            effective_date = datetime.date(effective_date.year, effective_date.month, effective_date.day)

            #If the function is called from the button and the date is not the correct, raise exception.
            if ids and effective_date != datetime.date.today():
                raise osv.except_osv('Error', 'This employee action is not scheduled for applying today.')
            #If the record is set up to be applied today is applied.
            if effective_date == datetime.date.today():
                    if action.action_requested_type == 'designacion':
                        if action.action_designation_requested == '1':
                            pass
                        elif action.action_designation_requested == '2':
                            pass
                        elif action.action_designation_requested == '3':
                            pass
                        elif action.action_designation_requested == '4':
                            pass
                        elif action.action_designation_requested == '5':
                            pass
                        elif action.action_designation_requested == '6':
                            pass
                        elif action.action_designation_requested == '7':
                            pass
                        elif action.action_designation_requested == '8':
                            pass
                        elif action.action_designation_requested == '9':
                            pass
                        elif action.action_designation_requested == '10':
                            pass
                        elif action.action_designation_requested == '11':
                            pass
                        elif action.action_designation_requested == '12':
                            pass

                    elif action.action_requested_type == 'cambios':
                        if action.action_changes_requested == '1':
                            hr_obj.write(cr, uid, action.employee_id.id, {'job_id':action.proposed_ocupation.id,
                                                                          'salary_scale_category':action.proposed_salary_scale_category,
                                                                          'salary_scale_level':action.proposed_salary_scale_level}, context=None)
                            hr_cont_obj.write(cr, uid, ret['contract_id'][0],{'working_hours':action.proposed_orderly_turn.id,
                                                                              'wage':action.proposed_total}, context=None)
                        elif action.action_changes_requested == '2':
                            pass
                        elif action.action_changes_requested == '3':
                            pass
                        elif action.action_changes_requested == '4':
                            pass
                        elif action.action_changes_requested == '5':
                            pass

                    elif action.action_requested_type == 'salidas':
                        if action.action_out_requested == '1':
                            pass
                        elif action.action_out_requested == '2':
                            pass
                        elif action.action_out_requested == '3':
                            pass
                        elif action.action_out_requested == '4':
                            pass
                        elif action.action_out_requested == '5':
                            pass
                        elif action.action_out_requested == '6':
                            pass
                        elif action.action_out_requested == '7':
                            pass
                        elif action.action_out_requested == '8':
                            pass
                        elif action.action_out_requested == '9':
                            pass
                        elif action.action_out_requested == '10':
                            pass
                        elif action.action_out_requested == '11':
                            pass

                    elif action.action_requested_type == 'vacation_and_licenses':
                        if action.action_others_requested == '1':
                            pass
                        elif action.action_others_requested == '2':
                            pass
                        elif action.action_others_requested == '3':
                            pass
                        elif action.action_others_requested == '4':
                            pass
                        elif action.action_others_requested == '5':
                            pass
                        elif action.action_others_requested == '6':
                            pass
                        elif action.action_others_requested == '7':
                            pass
                        elif action.action_others_requested == '8':
                            pass
                        elif action.action_others_requested == '9':
                            pass
                        elif action.action_others_requested == '10':
                            pass
                        elif action.action_others_requested == '11':
                            pass
                        elif action.action_others_requested == '12':
                            pass


    _columns={
        'origin_employee_id':fields.many2one('hr.employee', 'Petitioner', required=True, domain=[('manager','=',True)]),
        'origin_department_id':fields.many2one('hr.department', 'Area'),
        'origin_company_id':fields.many2one('res.company', 'Recinto'),
        'origin_address':fields.char('Address', size=128),
        'origin_state_id':fields.many2one('res.country.state', 'State'),
        'action_requested_type': fields.selection((('designacion','Designacion'),
                                                  ('cambios','Cambios'),
                                                  ('salidas','Salidas'),
                                                  ('vacation_and_licenses','Vacaciones y Licencias')
                                                  ), 'Tipo de Requerimiento', required=True),


        'action_designation_requested':fields.selection((('1','Extencion de Contrato'),
                                                         ('2','Extencion de Nombramiento'),
                                                         ('3','Inicio de Pension'),
                                                         ('4','Nombramiento Fijo'),
                                                         ('5','Nombramiento Interino'),
                                                         ('6','Nombramiento por Contrato'),
                                                         ('7','Nombramiento Probatorio'),
                                                         ('8','Nombramiento Temporero'),
                                                         ('9','Reingreso'),
                                                         ('10','Pasantia'),
                                                         ('11','Voluntarios'),
                                                         ('12','Entrenamiento')), 'Designacion', required=True),
        'action_changes_requested':fields.selection((('1','Promacion'),
                                                     ('2','Promocion y Transferencia'),
                                                     ('3','Reajuste de Sueldo'),
                                                     ('4','Reclasificacion'),
                                                     ('5','Transferencia')), 'Cambios', required=True),
        'action_out_requested':fields.selection((('1','Abandono de Cargo'),
                                                 ('2','Desahucio'),
                                                 ('3','Despido'),
                                                 ('4','Dimision'),
                                                 ('5','Fallecimiento'),
                                                 ('6','Pensionando'),
                                                 ('7','Renuncia'),
                                                 ('8','Rescision de Nombramiento'),
                                                 ('9','Finalizacion de Pasantia'),
                                                 ('10','Finalizacion de Voluntario'),
                                                 ('11','Finalicacion de Entrenamiento')), 'Salidas', required=True),
        'action_others_requested':fields.selection((('1','Asueto'),
                                                    ('2','Licencia por alumbramiento Conyuge'),
                                                    ('3','Licencia por Enfermedad'),
                                                    ('4','Licencia por Fallecimiento de Familiar (Directo)'),
                                                    ('5','Licencia por Fallecimiento de Familiar (Indirecto)'),
                                                    ('6','Licencia por Maternidad'),
                                                    ('7','Licencia por Matrimonio'),
                                                    ('8','Licencia sin disfrute de sueldo'),
                                                    ('9','Tardanza'),
                                                    ('10','Tarde de Cumpleaños'),
                                                    ('11','Vacaciones'),
                                                    ('12','Permiso')), 'Vacaciones y Licencias', required=True),

        'effective_date':fields.date('Effective date', required=True),
        'employee_id':fields.many2one('hr.employee', 'Petitioned', required=True),
        'contract_id': fields.many2one('hr.contract', 'Contracts', required=True),
        'actual_employee_code':fields.char('Code', size=32, readonly=True),
        'actual_identification_id':fields.char('Identification No.', size=32, readonly=True),
        'actual_dependency':fields.many2one('hr.department', 'Dependency', readonly=True),
        'actual_ocupation':fields.many2one('hr.job', 'Ocupation', readonly=True),
        'actual_parent_id':fields.many2one('hr.employee', 'Inmediate Superior'),
        #'actual_coach_id':fields.many2one('hr.employee', 'Coach'),
        'actual_orderly_turn':fields.many2one('resource.calendar', 'Actual work schedule'),
        'actual_salary_scale_category':fields.selection((('1','1'),
                                                         ('2','2'),
                                                         ('3','3'),
                                                         ('4','4'),
                                                         ('5','5'),
                                                         ('6','6'),
                                                         ('7','7'),
                                                         ('8','8'),
                                                         ('9','9'),
                                                         ('10','10'),
                                                         ('11','11'),
                                                         ('12','12'),
                                                         ('13','13'),
                                                         ('14','14'),
                                                         ('15','15'),
                                                         ('16','16'),
                                                         ('17','17'),
                                                         ('18','18'),
                                                         ('19','19'),
                                                         ('20','20'),
                                                         ('21','21'),
                                                         ('22','22'),
                                                         ('23','23'),
                                                         ('24','24'),
                                                         ('25','25')), 'Salary Scale Category'),
        'actual_salary_scale_level':fields.selection((('1','1'),
                                                      ('2','2'),
                                                      ('3','3'),
                                                      ('4','4'),
                                                      ('5','5'),
                                                      ('6','6')), 'Salary Scale Level'),
        'actual_wage':fields.float('Wage', digits=(16,2)),
        'actual_diff_scale':fields.float('Diff. scale', digits=(16,2)),
        #'actual_total':fields.function(calc_actual_total, string='Actual Total', type='float'),
        'observations':fields.text('Observations'),
        'states':fields.selection((('draft', 'Draft'),
                                   ('confirmed','Confirmed'),
                                   ('approved','Approved'),
                                   ('cancelled','Cancelled'),
                                   ('applied', 'Applied')),'Status'),
        #'start_leave':fields.date('Start licence'),
        'end_of_leave':fields.date('End of licence'),
        'days_of_vacations':fields.integer('Cantidad de dias'),
        'proposed_dependency':fields.many2one('hr.department', 'Dependency'),
        'proposed_ocupation':fields.many2one('hr.job', 'Ocupation'),
        'proposed_parent_id':fields.many2one('hr.employee', 'Director'),
        'proposed_coach_id':fields.many2one('hr.employee', 'Coach'),
        'proposed_orderly_turn':fields.many2one('resource.calendar', 'Proposed work schedule'),
        'proposed_wage':fields.float('Wage', digits=(16, 2), readonly=True),
        'proposed_salary_scale_category':fields.selection((('1','1'),
                                                           ('2','2'),
                                                           ('3','3'),
                                                           ('4','4'),
                                                           ('5','5'),
                                                           ('6','6'),
                                                           ('7','7'),
                                                           ('8','8'),
                                                           ('9','9'),
                                                           ('10','10'),
                                                           ('11','11'),
                                                           ('12','12'),
                                                           ('13','13'),
                                                           ('14','14'),
                                                           ('15','15'),
                                                           ('16','16'),
                                                           ('17','17'),
                                                           ('18','18'),
                                                           ('19','19'),
                                                           ('20','20'),
                                                           ('21','21'),
                                                           ('22','22'),
                                                           ('23','23'),
                                                           ('24','24'),
                                                           ('25','25')), 'Salary Scale Category'),
        'proposed_salary_scale_level':fields.selection((('1','1'),
                                                        ('2','2'),
                                                        ('3','3'),
                                                        ('4','4'),
                                                        ('5','5'),
                                                        ('6','6')), 'Salary Scale Level'),
        'proposed_diff_scale':fields.float('Diff. Scale', digits=(16,2)),

        'proposed_bonus':fields.float('Bonus', digits=(16, 2)),
        'proposed_end_new_contract':fields.date('End of contract'),
        'proposed_salary_cut':fields.float('Salary reduction', digits=(16, 2)),
        'proposed_misconduct':fields.text('Amonestacion'),
        'proposed_misconduct_level':fields.selection((('1','1'),
                                                      ('2','2'),
                                                      ('3','3')), 'Nivel falta cometida'),
        'proposed_salary':fields.many2one('hr.contract', 'Estructura Salarial', required=True),
        'date_start':fields.date('Duracion'),
        'proposed_transfer':fields.selection((
            ('1','UAPA Santiago'),
            ('2','UAPA Santo Domingo'),
            ('3','UAPA Nagua'),
            ('4','CEGES Santo Domingo'),
            ('5','CEGES Santiago')), 'Transferencia entre recintos'),
        #From here on the fields are for information only regarding salary compensation in case of employee leave.
        #This may change on another stage of the proyect.
        'days_severance':fields.integer('Days of severance',size=12),
        'severance':fields.float('Severance', digits=(16, 2)),
        'days_forewarning':fields.integer('Days of forewarning', size=12),
        'forewarning':fields.float('Forewarning', digits=(16,2)),
        'months_worked':fields.integer('Months worked', size=12),
        'monthly_salary':fields.float('Monthly Salary', digits=(16,2)),
        'christmas_salary':fields.float('Salario de navidad', digits=(16, 2)),
        'average_daily_salary':fields.float('Average daily salary', digits=(16, 2)),
        'vacations_days':fields.integer('Vacations days', size=12),
        'vacations':fields.float('Vacations', digits=(16,2)),
        # la siguiente linea hace referencia a una funcion que no esta en el codigo. La COMMENTE.
        #'employee_benefits_total':fields.function(calc_employee_leave_total, string='Total Benefits', type='float'),
        'severance_days':fields.integer('Dias de cesantia', size=12),
        'severange_total':fields.float('Monto cesantia', digits=(16,2)),
        'days_worked':fields.integer('Dias trabajados', size=12),
        'total_worked':fields.float('Monto dias trabajados', digits=(16,2)),

    }

    _defaults = {'states':'draft'}

    def period_test_contract(self, cr, uid, ids, employee_id, context=None):
        if employee_id:
            hr_contract_obj = self.pool.get('hr.contract')
            hr_contract_obj.create(cr, uid,{'name':'Contrato de Prueba','employee_id': employee_id, 'type_id':2, 'company_id':1, 'wage':self.proposed_salary, 'date_start':self.date_start})


HrPersonnelAction()
