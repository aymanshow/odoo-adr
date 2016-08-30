# -*- coding: utf-8 -*-
"""
@author: Ernesto Mendez
"""

import logging
import time
from datetime import datetime
from dateutil import relativedelta
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

class res_partner(orm.Model):
    _inherit = 'res.partner'
    _columns = {
        'phone2': fields.char('Telefono 2', size=64, required=False),
        'extension': fields.char('Extension', size=64, required=False),
        'property_account_payable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Payable",
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the payable account for the current partner",
            required=False),
        'property_account_receivable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Receivable",
            domain="[('type', '=', 'receivable')]",
            help="This account will be used instead of the default one as the receivable account for the current partner",
            required=False),
        'ars': fields.boolean('ARS'),
        # 'empleado': fields.boolean('Empleado',default=True),
        'estudiante':fields.boolean('Estudiante'),
        'expediente': fields.char('Expediente'),
    }
    def create(self, cr, uid, ids, context=None):

        if 'employee' in ids:
            # Si es Empleado le asigna Tarifa Empleados ADR (DOP) al campo
            # property_account_receivable
            ids['property_product_pricelist'] = 10

        return super(res_partner, self).create(cr, uid, ids, context)

class hr_recruitment_career(orm.Model):
    _name='hr.recruitment.career'
    _description = 'Carreras Profesionales'

    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        'sequence': fields.integer('Secuencia', size=2, required=True),
        }
hr_recruitment_career()

class hr_employee_emergency_contact(orm.Model):
    _name='hr.employee.emergency.contact'
    _description = 'Contacto de Emergencia'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleado', readonly=True),
        'name': fields.char('Nombre', size=64, required=True),
        'emergency_contact_phone': fields.char('Telefono', size=32)
    }
hr_employee_emergency_contact()

class hr_employee_ars(orm.Model):
    _name='hr.employee.ars'
    _description = 'Aseguradoras de Riesgos de Salud'

    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        'sequence': fields.integer('Secuencia', size=3, required=True)
    }

hr_employee_ars()


class hr_employee_family(orm.Model):
    _name="hr.employee.family"
    _description = 'Informacion Familiar'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleador'),
        'name': fields.char("Nombre", size=64, required=True),
        'relationship': fields.selection((('father', 'Padre'), ('mother', 'Madre'), ('daughter/son', 'Hijo/Hija'), ('other', 'Otro')), 'Parentesco'),
        'date_of_birth': fields.date('Fecha de Nacimiento', required=True, select=True),
        'gender': fields.selection((('male', 'Masculino'), ('female', 'Femenino')), 'Genero')
    }

hr_employee_family()

class ProffesionalFormation(orm.Model):

    _name = 'hr.employee.formation'
    _description = 'Formacion Profesional'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleado'),
        'career_id': fields.many2one('hr.recruitment.career', 'Carrera'),
        'date_start': fields.date('Fecha de inicio'),
        'date_end': fields.date('Fecha de finalizacion'),
        'specialization': fields.char('Especializacion', size=128),
        'degree_id': fields.many2one('hr.recruitment.degree', 'Grado')
    }

class ProffesionalDegree(orm.Model):

    _name = 'hr.recruitment.degree'
    _description = 'Grados'
    _columns = {
        'name': fields.char('Grado', size=16, required=True),
        'sequence': fields.integer('Secuencia', size=16)
    }

ProffesionalDegree()

class hr_employee(orm.Model):
    _name='hr.employee'
    _inherit='hr.employee'

    _columns = {
        'partner_phone':fields.char('Telefono Personal', size=32),
        'emergency_contact':fields.one2many('hr.employee.emergency.contact', 'employee_id', 'Contactos de Emergencia'),
        'family_info_ids':fields.one2many('hr.employee.family', 'employee_id', 'Informacion Familiar'),
        'nss_id':fields.char('NSS', size=32),
        'hr_employee_ars_id':fields.many2one('hr.employee.ars', 'ARS Afiliado', required=False),
        'employee_code':fields.char('Codigo', size=32, required=True, readonly=True),
        'formation_ids': fields.one2many('hr.employee.formation', 'employee_id', 'Formacion', ondelete="cascade"),
        'on_vacation': fields.boolean('On Vacation'),
        'street':fields.char('Direccion'),
        'street2':fields.char('Direccion 2'),
        'city':fields.char('Ciudad'),
        'state_id':fields.many2one('res.country.state', 'Estado'),
        'contry_id':fields.many2one('res.country', 'Pais'),
        'marital': fields.selection((('single','Soltero(a)'),('married','Casado(a)'),('widower','Viudo(a)'),
                                     ('divorced','Divorciado(a)'),('unionlibre', 'Union Libre')))

    }

    _defaults = {
        'employee_code':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'employee.number')
    }

    def create(self, cr, uid, ids, context=None):
        """Overwritten to the create method of employee so that it creates a res_partner record as well."""

        partner_obj = self.pool.get('res.partner')
        values = ids
        created_id = super(hr_employee, self).create(cr, uid, values, context)
        values['employee_code'] = self.pool.get('ir.sequence').get(cr, uid, 'employee.number')
        created_partner_id = partner_obj.create(cr, uid, {'name': values.get('name'),
                                     'display_name': values.get('name_related'),
                                     'lang': 'es_DO',
                                     'active': True,
                                     'email': values.get('work_email'),
                                     'phone': values.get('work_phone'),
                                     'employee': True,
                                     'tz': 'America/Santo_Domingo',
                                     'notification_email_send': 'comment',
                                     'company_id': values.get('company_id'),
                                     'street': values.get('street'),
                                     'street2': values.get('street2'),
                                     'city': values.get('city'),
                                     'state_id': values.get('state_id'),
                                     'contry_id': values.get('contry_id'),}, context)
        self.write(cr, uid, created_id, {'address_home_id': created_partner_id}, context)
        return created_id

hr_employee()

class hr_contract(orm.Model):
    _name='hr.contract'
    _inherit='hr.contract'

    def _get_contract_years(self, cr, uid, ids, name, arg, context=None):

        res = {}

        for contract in self.browse(cr, uid, ids, context=context):
            today = datetime.today()
            dt = datetime.strptime(contract.date_start, '%Y-%m-%d')
            dt1 = today - dt
            dt2 = dt1.days
            res[contract.id] = (dt2/365)
        return res

    def _get_contract_days(self, cr, uid, ids, name, arg, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            today = datetime.today()
            dt = datetime.strptime(contract.date_start, '%Y-%m-%d')
            dt1 = today - dt
            dt2 = dt1.days
            res[contract.id] = dt2
        return res

    _columns = {
        'schedule_pay': fields.selection([
            ('fortnightly', 'Quincenal'),
            ('monthly', 'Mensual'),
            ('quarterly', 'Trimestral'),
            ('semi-annually', 'Semestral'),
            ('annually', 'Anual'),
            ('weekly', 'Semanal'),
            ('bi-weekly', 'Bi-semanal'),
            ('bi-monthly', 'Bi-mensual'),
            ], 'Scheduled Pay', select=True),
        'company_id': fields.many2one('res.company', 'Compañia', required=True),
        'contract_years': fields.function(_get_contract_years, store=True, type='integer', digits_compute=dp.get_precision('Payroll'), string='Años en el trabajo'),
        'contract_days': fields.function(_get_contract_days, store=True, type='integer', digits_compute=dp.get_precision('Payroll'), string='Dias en el trabajo'),
        }
