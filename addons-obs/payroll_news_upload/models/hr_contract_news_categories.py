# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Jose Ernesto Mendez. All Rights Reserved.
#
##############################################################################

from openerp import models, fields, api, _


class HrContractNewsCategories(models.Model):
    _name = 'hr_contract.news.categories'
    _description = 'Categorias de Novedades de Contratos'

    name = fields.Char()
