from openerp.osv import osv, fields


class localizaciones(osv.osv):
    _name = 'localizaciones'

    _columns = {
        'name': fields.char('Localizacion', required=True),
    }

localizaciones()


class areas(osv.osv):
    _name = 'areas'

    _columns = {
        'name': fields.char('Area', required=True),
        'localizacion': fields.many2one('localizaciones', 'Localizacion', required=True)
    }

areas()
