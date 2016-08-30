# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Jose Ernesto Mendez. All Rights Reserved.
#
##############################################################################

from openerp import models, fields, api, _


class HrContractNewsConcepts(models.Model):
    _name = 'hr_contract.news.concepts'
    _description = 'Categorias de Novedades de Contratos'

    active = fields.Boolean('Activo', default=True)
    code = fields.Char(string='Codigo', size=8, required=False)
    name = fields.Char(string="Nombre", size=64, required=True)
    description = fields.Text(
        'Descripcion',
        help="Una breve explicacion acerca de esta novedad."
    )

    contract_new_category_id = fields.Many2one(comodel_name="hr_contract.news.categories",
                                               string="Categoria Novedad", required=True, )
    salary_rule_ids = fields.Many2many('hr.salary.rule', 'salary_rule_contract_news_rel',
                                       'news_id', 'salary_rule_id', 'Reglas Salariales',
    )

