# -*- coding: utf-8 -*-
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import logging
_logger = logging.getLogger(__name__)


class ValidateInvoiceFromADRCRM(models.Model):

    _inherit = 'account.invoice'

    @api.model
    def ValidateInvoiceFromADRCRM(self):
        invoices = self.env['account.invoice'].search([('external_source', '=', True),
                                                       ('state', '=', 'draft'),
                                                       ('external_source_state', '=', 'closed')])
        found = False
        if invoices:
            found = True
            _logger.info('Starting invoice validation ..... !')
            for inv in invoices:
                inv.button_reset_taxes()
                inv.action_date_assign()
                inv.action_move_create()
                inv.action_number()
                inv.invoice_validate()
                self.write({'processed': True})
                _logger.info('''Invoice number %s validated! ''', inv.number)
            _logger.info('''Invoice validation process finished sucessfully! ''')

        if not found:
            _logger.info('No invoices found to process..... !')



# class AccountBankStatement(models.Model):
#
#     _inherit = 'account.bank.statement'
#
#     login = fields.Char(string="Login", related="user_id.login",
#                         states={'confirm': [('readonly', True)]}, required=False, store=True)
