# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 test (<http://www.test.com>)
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

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class requisition(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(requisition, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_reqstate':self._get_reqstate,
            'get_state':self._get_state
        })

    def _get_reqstate(self, state):
       orig_state = dict([('draft','New'),('confirm','Confirmed'),('cancel','Cancelled'),('done','Done'),('approve','Approved'),
         ('waiting','Waiting Availability'),('delivery','Delivery Order Generated'),('ready','Ready to Process')])
       return orig_state.get(state)

    def _get_state(self, state):
        orig_state = dict([('draft', 'New'),('confirmed', 'Waiting Availability'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Cancelled')])
        return orig_state.get(state)

report_sxw.report_sxw('report.internal.requisition','internal.requisition','addons/internal_requisition/report/internal_requisition.rml',parser=requisition)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

