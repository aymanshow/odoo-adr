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

from openerp import models, fields, api


class CheckReportConfig(models.Model):
    _name = "check.report.config"

    name = fields.Char("Nombre", required=True)

    header = fields.Float(string="Margen superior de la coletilla")

    header_date = fields.Float(string="Margen superior de la fecha de la coletilla")
    header_date_left = fields.Float(string="Margen izquierdo de la fecha de la coletilla")
    
    header_concept = fields.Float(string="Margen superior del concepto de la coletilla")
    header_concept_left = fields.Float(string="Margen izquierdo del concepto de la coletilla")

    header_amount = fields.Float(string="Margen superior del monto de la coletilla")
    header_amount_left = fields.Float(string="Margen izquierdo del monto de la coletilla")

    body_top = fields.Float(string="Margen superior del cuerpo del cheque")

    name_top = fields.Float(string="Margen superior del nombre")
    name_left = fields.Float(string="Margen izquierdo del nombre")

    date_top = fields.Float(string="Margen superior de la fecha")
    date_left = fields.Float(string="Margen izquierdo de la fecha")

    amount_top = fields.Float(string="Margen superior del monto")
    amount_left = fields.Float(string="Margen izquierdo del monto")

    amount_letter_top = fields.Float(string="Margen superior monto en letras")
    amount_letter_left = fields.Float(string="Margen izquierdo monto en letras")

    check_header_top = fields.Float("Margen superior de la Cabecera")
    check_header = fields.Html("Cabecera del cheque")

    check_accounting_footer_top = fields.Float("Margen superior del pie contable")
    account_footer_left = fields.Float("Margen izquierdo de la cuenta contable")
    sub_account_footer_left = fields.Float("Margen izquierdo de la sub cuenta contable")
    description_footer_left = fields.Float("Margen izquierdo de la descripcion contable")
    aux_footer_left = fields.Float("Margen izquierdo del auxiliar contable")
    debit_footer_left = fields.Float("Margen izquierdo del debito contable")
    credit_footer_left = fields.Float("Margen izquierdo del credito contable")

    check_footer_top = fields.Float("Margen superior del pie")
    check_footer = fields.Html("Pie del cheque")


