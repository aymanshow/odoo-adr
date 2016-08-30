from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class ResPartner(models.Model):
    #_name = 'new_module.new_module'
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string="Es Paciente?",  )
    nss_number = fields.Char(string="NSS", required=False, )
    is_insurance = fields.Boolean(string="Es Aseguradora?",  )
    insurance_id = fields.Many2one(comodel_name="res.partner", string="Aseguradora", required=False, )
    record_name = fields.Char(string="Expediente", required=False, )
    state = fields.Selection(string="", selection=[('contributivo', 'Contributivo'),
                                                   ('subsidiado', 'Subsidiado'), ], required=False, )

