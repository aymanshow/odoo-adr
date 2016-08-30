#-*- coding: utf-8 -*-

from openerp.osv import orm, fields
import pdb

class AccountVoucher(orm.Model):

    _inherit = 'account.voucher'
    _description = 'Secuencia de Registros'

    _columns = {
        'name': fields.text('Memoria', required=True),
        'voucher_number': fields.char('Number'),
        'state':fields.selection(
            [('draft','Draft'),
             ('cancel','Cancelled'),
             ('proforma','Pro-forma'),
             ('posted','Posted'),
                ('delivered', 'Entregado'),
             ('refunded', 'Reintegrado')
            ], 'Status', readonly=True, track_visibility='onchange', copy=False,
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                        \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Cancelled\' status is used when user cancel voucher.'),
    }

    def deliver_voucher(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,
            {'state': 'delivered'}
        )

    def reintegrate_voucher(self, cr, uid, ids, context=None):
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            # refresh to make sure you don't unlink an already removed move
            voucher.refresh()
            for line in voucher.move_ids:
                # refresh to make sure you don't unreconcile an already unreconciled entry
                line.refresh()
                if line.reconcile_id:
                    move_lines = [move_line.id for move_line in line.reconcile_id.line_id]
                    move_lines.remove(line.id)
                    reconcile_pool.unlink(cr, uid, [line.reconcile_id.id])
                    if len(move_lines) >= 2:
                        move_line_pool.reconcile_partial(cr, uid, move_lines, 'auto',context=context)
            if voucher.move_id:
                move_pool.button_cancel(cr, uid, [voucher.move_id.id])
                move_pool.unlink(cr, uid, [voucher.move_id.id])
        res = {
            'state':'refunded',
            'move_id':False,
        }
        self.write(cr, uid, ids, res)
        return True

    def create(self, cr, uid, vals, context=None):

        if not vals:
            vals ={}
        journal = vals.get('journal_id',False)

        if journal:
            ir_sequence = self.pool.get('account.journal').browse(cr, uid, journal).internal_sequence_id.code
            seq = self.pool.get('ir.sequence').get(cr, uid, ir_sequence)
            vals.update({
                     'voucher_number': str(seq)
                 })
            return super(AccountVoucher, self).create(cr, uid, vals, context)

AccountVoucher()
