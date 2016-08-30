# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Jose Ernesto Mendez. All Rights Reserved.
#
##############################################################################

from openerp import models, fields, api, _


class HrContract(models.Model):
    _inherit = "hr.contract"

    hr_contract_news_ids = fields.One2many(comodel_name="hr.contract.news", inverse_name="contract_id",
                                           string="Novedades", required=False, )