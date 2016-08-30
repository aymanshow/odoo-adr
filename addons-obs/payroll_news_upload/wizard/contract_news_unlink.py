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


class ContractNewsUnlink(models.TransientModel):
    _name = 'contract.news.unlink.wizard'
    #_inherit = 'hr.payslip.run'

    contract_news_concepts_ids = fields.Many2many(comodel_name="hr_contract.news.concepts",
                                                  relation="", column1="", column2="", string="", )
    contract_type_id = fields.Many2one(comodel_name="hr.contract.type", string="Tipo de contrato", required=False, )

    @api.multi
    def do_mass_unlink(self, args):
        self.ensure_one()

        if not self.contract_type_id:
            raise exceptions.Warning(_("Debe seleccionar un tipo de contrato!"))
        elif not self.contract_news_concepts_ids:
            raise exceptions.Warning(_("Debe seleccionar al menos una novedad!"))

        values = {}
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        contract_news_obj = self.env['hr.contract.news']
        type_id = self.contract_type_id.id

        for item in self.contract_news_concepts_ids:
            contract_new = contract_news_obj.search([('contract_id.type_id', '=', type_id),
                        ('hr_contract_news_concepts_id', '=', item.id)])
            contract_new.unlink()

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'contract.news.upload.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            }