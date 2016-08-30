# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Jose Ernesto Mendez. All Rights Reserved.
#
##############################################################################

from openerp import models, fields, api, _
from openerp import exceptions # will be used in the code
import logging
_logger = logging.getLogger(__name__)
import base64
import csv
import cStringIO
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta


class ContractNewsUpload(models.TransientModel):
    _name = 'contract.news.upload.wizard'
    #_inherit = 'hr.payslip.run'

    data = fields.Binary('Cargar plantilla', required=False)
    template = fields.Binary("Descargar plantilla", readonly=True)
    template_name = fields.Char(u"Nombre de Reporte", size=40, readonly=True)
    delimeter = fields.Char('Delimitador', default=',',
                            help='Default delimeter is ","')
    contract_news_concepts_ids = fields.Many2many(comodel_name="hr_contract.news.concepts",
                                                  relation="", column1="", column2="", string="", )
    contract_type_id = fields.Many2one(comodel_name="hr.contract.type", string="Tipo de contrato", required=False, )

    @api.multi
    def do_generate_template(self):
        path = '/tmp/news_template.csv'
        f = open(path, 'w')
        header_str = ""
        header_str += "Codigo Empleado,"
        header_str += "Importe descuento,"
        header_str += "Aplicar en,"
        header_str += "Tipo de frecuencia,"
        header_str += "Numero de veces,"
        header_str += "Fecha inicial,"

        f.write(header_str + '\n')

        f.close()

        f = open(path, 'rb')
        template = base64.b64encode(f.read())
        template_name = 'news_template.csv'
        self.write({'template': template, 'template_name': template_name})
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'contract.news.upload.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def do_mass_update(self, args):
        self.ensure_one()

        if not self.data:
            raise exceptions.Warning(_("Debe seleccionar un archivo!"))
        elif not self.contract_type_id:
            raise exceptions.Warning(_("Debe seleccionar un tipo de contrato!"))
        elif not self.contract_news_concepts_ids:
            raise exceptions.Warning(_("Debe seleccionar una novedad!"))

        if len(self.contract_news_concepts_ids) > 1:
            raise exceptions.Warning(_("Imposible cargar mas de una novedad por archivo!"))
        # Decode the file data
        data = base64.b64decode(self.data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]
        if not isinstance(keys, list) or ('Codigo Empleado' not in keys or
                                          'Importe descuento' not in keys or
                                          'Aplicar en' not in keys or
                                          'Tipo de frecuencia' not in keys):
            raise exceptions.Warning(
                _("No se han encontrado las claves 'Codigo Empleado', "
                  "'Importe descuento', 'Aplicar en' y 'Tipo de frecuencia' "
                  "en el documento! Por favor revise"))
        del reader_info[0]
        values = {}
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        contract_news_obj = self.env['hr.contract.news']
        type_id = self.contract_type_id.id
        for i in range(len(reader_info)):
            val = {}
            field = reader_info[i]
            values = dict(zip(keys, field))
            employee = employee_obj.search([('employee_code', '=', values['Codigo Empleado'])])
            if employee:
                contract = contract_obj.search([('employee_id', '=', employee.id),('type_id', '=', type_id)])
                if contract:
                    contract_news = contract_news_obj.search([('contract_id', '=', contract.id),
                        ('hr_contract_news_concepts_id', '=', self.contract_news_concepts_ids.id)])
                    if contract_news and values['Tipo de frecuencia'] == 'fixed':
                        raise exceptions.Warning(_("Imposible aplicar un descuento tipo 'Fijo' mas de una "
                                                 "vez en el contrato %s de %s" % (contract.name,
                                                                                  contract.employee_id.name)))
                        # val['amount'] = (contract_news.amount + float(values['Importe descuento']))
                        # contract_news.write(val)
                    # elif contract_news and values['Tipo de frecuencia'] == 'variable':
                    #     raise exceptions.Warning(_("Imposible aplicar un descuento tipo 'Variable' mas de una"
                    #                                "vez a un mismo contrato "))
                    else:
                        val['contract_id'] = contract[0].id
                        val['hr_contract_news_concepts_id'] = self.contract_news_concepts_ids.id
                        val['amount'] = values['Importe descuento']
                        val['apply_on'] = values['Aplicar en']
                        val['frecuency_type'] = values['Tipo de frecuencia']
                        val['frecuency_number'] = int(values['Numero de veces']) or 0
                        val['end_date'] = False
                        end_date = False

                        if values['Tipo de frecuencia'] == 'variable':
                            start_date = datetime.datetime.strptime(values['Fecha inicial'], '%d-%m-%Y').date() or False
                            frequency_number = (int(values['Numero de veces'])-1) or 0
                            val['start_date'] = start_date
                            if values['Aplicar en'] == '1' or values['Aplicar en'] == '2':
                                end_date = start_date + relativedelta(months=+frequency_number)
                            elif values['Aplicar en'] == '3':
                                end_date = start_date + (relativedelta(months=+(frequency_number/2))
                                                         + relativedelta(days=+15))
                            val['end_date'] = end_date

                        contract_news_obj.create(val)

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'contract.news.upload.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            }