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

from openerp.osv import osv,fields
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

class stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"
    _columns = {
    'internal_req_type_id': fields.many2one('stock.picking.type', 'IR Type'),
    }
    
    def create_sequences_and_picking_types(self, cr, uid, warehouse, context=None):
        super(stock_warehouse,self).create_sequences_and_picking_types(cr, uid, warehouse, context=None)
        int_seq_id = seq_obj = self.pool.get('ir.sequence').create(cr, SUPERUSER_ID, values={'name': warehouse.name + _(' Sequence IR'), 'prefix': warehouse.code + '/IR/', 'padding': 5}, context=context)
        picking_type_obj = self.pool.get('stock.picking.type')
        #choose the next available color for the picking types of this warehouse
        color = 0
        available_colors = [c%9 for c in range(3, 12)]
        all_used_colors = self.pool.get('stock.picking.type').search_read(cr, uid, [('warehouse_id', '=', warehouse.id), ('color', '!=', False)], ['color'], order='color', limit=1)
        max_sequence = self.pool.get('stock.picking.type').search_read(cr, uid, [], ['sequence'], order='sequence desc')
        max_sequence = max_sequence and max_sequence[0]['sequence'] or 0
        color = all_used_colors and all_used_colors[0]['color']
        int_type_id = picking_type_obj.create(cr, uid, vals={
            'name': _('Internal Requisition'),
            'warehouse_id': warehouse.id,
            'code': 'internal',
            'sequence_id': int_seq_id,
            'default_location_src_id': warehouse.lot_stock_id.id,
            'default_location_dest_id': warehouse.lot_stock_id.id,
            'active': True,
            'sequence': max_sequence + 2,
            'color': color}, context=context)
        super(stock_warehouse, self).write(cr, uid, warehouse.id, {'internal_req_type_id':int_type_id}, context=context)
        return True
    
class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
        'departamento': fields.many2one('hr.department', 'Departamento'),

    }

    def _create_backorder(self, cr, uid, picking, backorder_moves=[], context=None):
        """ Move all non-done lines into a new backorder picking.
         If the key 'do_only_split' is given in the context,
         then move all lines not in context.get('split', []) instead of all non-done lines.
        """
        if not backorder_moves:
            backorder_moves = picking.move_lines
        backorder_move_ids = [x.id for x in backorder_moves if x.state not in ('done', 'cancel')]
        if 'do_only_split' in context and context['do_only_split']:
            backorder_move_ids = [x.id for x in backorder_moves if x.id not in context.get('split', [])]
        
        if backorder_move_ids:
            backorder_id = self.copy(cr, uid, picking.id, {
                'name': '/',
                'move_lines': [],
                'pack_operation_ids': [],
                'backorder_id': picking.id,
                'internal_requisition_id': picking.internal_requisition_id.id,
                'departamento': picking.internal_requisition_id.department_id.id,
            })
            backorder = self.browse(cr, uid, backorder_id, context=context)
            self.message_post(cr, uid, picking.id, body=_("Back order <em>%s</em> <b>created</b>.") % (backorder.name), context=context)
            move_obj = self.pool.get("stock.move")
            move_obj.write(cr, uid, backorder_move_ids, {'picking_id': backorder_id}, context=context)
            picking.internal_requisition_id.write({'delivery_ids': [(4, backorder_id)]})

            self.write(cr, uid, [picking.id], {'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
            self.action_confirm(cr, uid, [backorder_id], context=context)
            
            return backorder_id
        return False


class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def action_done(self, cr, uid, ids, context=None):
        """ Process completely the moves given as ids and if all moves are done, it will finish the picking.
        """
        context = context or {}
        picking_obj = self.pool.get("stock.picking")
        quant_obj = self.pool.get("stock.quant")
        todo = [move.id for move in self.browse(cr, uid, ids, context=context) if move.state == "draft"]
        if todo:
            ids = self.action_confirm(cr, uid, todo, context=context)
        pickings = set()
        procurement_ids = set()
        # Search operations that are linked to the moves
        operations = set()
        move_qty = {}
        for move in self.browse(cr, uid, ids, context=context):
            move_qty[move.id] = move.product_qty
            for link in move.linked_move_operation_ids:
                operations.add(link.operation_id)

        # Sort operations according to entire packages first, then package + lot, package only, lot only
        operations = list(operations)
        operations.sort(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.lot_id and -1 or 0))

        for ops in operations:
            if ops.picking_id:
                pickings.add(ops.picking_id.id)
            main_domain = [('qty', '>', 0)]
            for record in ops.linked_move_operation_ids:
                move = record.move_id
                self.check_tracking(cr, uid, move, not ops.product_id and ops.package_id.id or ops.lot_id.id, context=context)
                prefered_domain = [('reservation_id', '=', move.id)]
                fallback_domain = [('reservation_id', '=', False)]
                fallback_domain2 = ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]
                prefered_domain_list = [prefered_domain] + [fallback_domain] + [fallback_domain2]
                dom = main_domain + self.pool.get('stock.move.operation.link').get_specific_domain(cr, uid, record, context=context)
                quants = quant_obj.quants_get_prefered_domain(cr, uid, ops.location_id, move.product_id, record.qty, domain=dom, prefered_domain_list=prefered_domain_list,
                                                          restrict_lot_id=move.restrict_lot_id.id, restrict_partner_id=move.restrict_partner_id.id, context=context)
                if ops.product_id:
                    # If a product is given, the result is always put immediately in the result package (if it is False, they are without package)
                    quant_dest_package_id = ops.result_package_id.id
                    ctx = context
                else:
                    # When a pack is moved entirely, the quants should not be written anything for the destination package
                    quant_dest_package_id = False
                    ctx = context.copy()
                    ctx['entire_pack'] = True
                quant_obj.quants_move(cr, uid, quants, move, ops.location_dest_id, location_from=ops.location_id, lot_id=ops.lot_id.id, owner_id=ops.owner_id.id, src_package_id=ops.package_id.id, dest_package_id=quant_dest_package_id, context=ctx)

                # Handle pack in pack
                if not ops.product_id and ops.package_id and ops.result_package_id.id != ops.package_id.parent_id.id:
                    self.pool.get('stock.quant.package').write(cr, SUPERUSER_ID, [ops.package_id.id], {'parent_id': ops.result_package_id.id}, context=context)
                if not move_qty.get(move.id):
                    raise osv.except_osv(_("Error"), _("The roundings of your Unit of Measures %s on the move vs. %s on the product don't allow to do these operations or you are not transferring the picking at once. ") % (move.product_uom.name, move.product_id.uom_id.name))
                move_qty[move.id] -= record.qty
        # Check for remaining qtys and unreserve/check move_dest_id in
        move_dest_ids = set()
        for move in self.browse(cr, uid, ids, context=context):
            move_qty_cmp = float_compare(move_qty[move.id], 0, precision_rounding=move.product_id.uom_id.rounding)
            if move_qty_cmp > 0:  # (=In case no pack operations in picking)
                main_domain = [('qty', '>', 0)]
                prefered_domain = [('reservation_id', '=', move.id)]
                fallback_domain = [('reservation_id', '=', False)]
                fallback_domain2 = ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]
                prefered_domain_list = [prefered_domain] + [fallback_domain] + [fallback_domain2]
                self.check_tracking(cr, uid, move, move.restrict_lot_id.id, context=context)
                qty = move_qty[move.id]
                quants = quant_obj.quants_get_prefered_domain(cr, uid, move.location_id, move.product_id, qty, domain=main_domain, prefered_domain_list=prefered_domain_list, restrict_lot_id=move.restrict_lot_id.id, restrict_partner_id=move.restrict_partner_id.id, context=context)
                quant_obj.quants_move(cr, uid, quants, move, move.location_dest_id, lot_id=move.restrict_lot_id.id, owner_id=move.restrict_partner_id.id, context=context)

            # If the move has a destination, add it to the list to reserve
            if move.move_dest_id and move.move_dest_id.state in ('waiting', 'confirmed'):
                move_dest_ids.add(move.move_dest_id.id)

            if move.procurement_id:
                procurement_ids.add(move.procurement_id.id)

            # unreserve the quants and make them available for other operations/moves
            quant_obj.quants_unreserve(cr, uid, move, context=context)
        # Check the packages have been placed in the correct locations
        self._check_package_from_moves(cr, uid, ids, context=context)
        # set the move as done
        self.write(cr, uid, ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
        self.pool.get('procurement.order').check(cr, uid, list(procurement_ids), context=context)
        # assign destination moves
        if move_dest_ids:
            self.action_assign(cr, uid, list(move_dest_ids), context=context)
        # check picking state to set the date_done is needed
        import pdb; pdb.set_trace()
        done_picking = []
        for picking in picking_obj.browse(cr, uid, list(pickings), context=context):
            if picking.state == 'done' and picking.date_done:
                if picking.internal_requisition_id:
                    picking.internal_requisition_id.action_accounting()
            if picking.state == 'done' and not picking.date_done:
                done_picking.append(picking.id)
                if picking.internal_requisition_id:
                    picking.internal_requisition_id.action_accounting()
        if done_picking:
            picking_obj.write(cr, uid, done_picking, {'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
        return True

class stock_return_picking(osv.osv):

    _inherit = 'stock.return.picking'

    def _create_returns(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.line')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        returned_lines = 0

        # Cancel assignment of existing chained assigned moves
        moves_to_unreserve = []
        for move in pick.move_lines:
            to_check_moves = [move.move_dest_id] if move.move_dest_id.id else []
            while to_check_moves:
                current_move = to_check_moves.pop()
                if current_move.state not in ('done', 'cancel') and current_move.reserved_quant_ids:
                    moves_to_unreserve.append(current_move.id)
                split_move_ids = move_obj.search(cr, uid, [('split_from', '=', current_move.id)], context=context)
                if split_move_ids:
                    to_check_moves += move_obj.browse(cr, uid, split_move_ids, context=context)

        if moves_to_unreserve:
            move_obj.do_unreserve(cr, uid, moves_to_unreserve, context=context)
            #break the link between moves in order to be able to fix them later if needed
            move_obj.write(cr, uid, moves_to_unreserve, {'move_orig_ids': False}, context=context)

        #Create new picking for returned products
        pick_type_id = pick.picking_type_id.return_picking_type_id and pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
        new_picking = pick_obj.copy(cr, uid, pick.id, {
            'move_lines': [],
            'picking_type_id': pick_type_id,
            'state': 'draft',
            'origin': pick.name,
        }, context=context)

        # Revierte el asiento contable
        pick.internal_requisition_id.accounting_entry_return()

        for data_get in data_obj.browse(cr, uid, data['product_return_moves'], context=context):
            move = data_get.move_id
            if not move:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity

            if new_qty:
                # The return of a return should be linked with the original's destination move if it was not cancelled
                if move.origin_returned_move_id.move_dest_id.id and move.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = move.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False

                returned_lines += 1
                move_obj.copy(cr, uid, move.id, {
                    'product_id': data_get.product_id.id,
                    'product_uom_qty': new_qty,
                    'product_uos_qty': new_qty * move.product_uos_qty / move.product_uom_qty,
                    'picking_id': new_picking,
                    'state': 'draft',
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': move.location_id.id,
                    'origin_returned_move_id': move.id,
                    'procure_method': 'make_to_stock',
                    'restrict_lot_id': data_get.lot_id.id,
                    'move_dest_id': move_dest_id,
                })



        # Elimina El asiento contable para regresar el valor de presupuesto
        # cuando se revierte el traslado de la mercancia.
        #journal_obj = self.pool.get('account.move')
        #jo_id = journal_obj.search(cr,uid,[('ref','=', str(pick.origin))])

        #journal_obj.unlink(cr, uid, jo_id[0])


        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        pick_obj.action_confirm(cr, uid, [new_picking], context=context)
        pick_obj.action_assign(cr, uid, [new_picking], context)
        return new_picking, pick_type_id


    def create_returns(self, cr, uid, ids, context=None):
        """Modifica la funcion original create_retunrs para ponder
        cambiarle el stage a la requisicion interna cuando se le da a retornar
        """
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id)

        #----------------------------------------------------------------------
        rid = pick.internal_requisition_id.id

        print rid
        req_obj = self.pool.get('internal.requisition')
        req = req_obj.browse(cr, uid, rid)
        print 'la requisicion es', req
        req_obj.write(cr, uid, rid, {'stage': 'delivery'})

        #----------------------------------------------------------------------

        super(stock_return_picking, self).create_returns(cr, uid, ids,context)


class internal_requisition(osv.osv):
    _inherit = 'internal.requisition'

    def revertir(self, cr, uid, ids, context=None):

        if context is None: context = {}

        pick_id = self.pool.get('stock.picking').search(cr, uid,
                                [('internal_requisition_id','=', ids)])

        if context.get('active_model') != self._name:
            context.update(active_id=pick_id[0], active_model=self._name, )

        vals = {'name':("Return lines"),
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'stock.return.picking',
                'res_id': '',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': context
            }

        return vals
