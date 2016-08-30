# import pdb

from openerp.osv import osv, fields


class Localizaciones(osv.osv):
    _name = "localizaciones"

    _columns = {
        'name': fields.char("Nombre"),
    }

Localizaciones()



class Areas(osv.osv):
    _name = "areas"

    _columns = {
        'name': fields.char("Nombre"),
    }

Areas()
