# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import netsvc
import time

from osv import osv,fields
from tools.translate import _
import decimal_precision as dp

class stock_return_picking_memory(osv.osv_memory):
    """ 
    To manage fuel picking """

    _name = "fuel.return.picking.memory"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True),
        'quantity' : fields.float("Quantity", digits_compute=dp.get_precision('Product UoM'), required=True),
        'wizard_id' : fields.many2one('fuel.return.picking', string="Wizard"),
        'move_id' : fields.many2one('stock.move', "Move"),
    }


class stock_return_picking(osv.osv_memory):
    """
    To manage fule picking """

    _name = 'fuel.return.picking'
    _description = 'Return Picking'
    _columns = {
        'product_return_moves' : fields.one2many('fuel.return.picking.memory', 'wizard_id', 'Moves'),
#        'invoice_state': fields.selection([('2binvoiced', 'To be refunded/invoiced'), ('none', 'No invoicing')], 'Invoicing',required=True),
     }

    def default_get(self, cr, uid, fields, context=None):
        """
         To get default values for the object.

         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary with default values for all field in ``fields``
        """
        result1 = []
        if context is None:
            context = {}
        res = super(stock_return_picking, self).default_get(cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('fuel.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        if pick:
            """if 'invoice_state' in fields:
                if pick.invoice_state=='invoiced':
                    res.update({'invoice_state': '2binvoiced'})
                else:
                    res.update({'invoice_state': 'none'})"""
            return_history = self.get_return_history(cr, uid, record_id, context)       
            for line in pick.move_lines:
                qty = line.product_qty - return_history[line.id]
                if qty > 0:
                    result1.append({'product_id': line.product_id.id, 'quantity': qty,'move_id':line.id})
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': result1})
        return res

    def view_init(self, cr, uid, fields_list, context=None):
        """
        Creates view dynamically and adding fields at runtime.
        @param fields_list: field of object
        @return: New arch of view with new columns.
        """
        if context is None:
            context = {}
        res = super(stock_return_picking, self).view_init(cr, uid, fields_list, context=context)
        record_id = context and context.get('active_id', False)
        if record_id:
            pick_obj = self.pool.get('fuel.picking')
            pick = pick_obj.browse(cr, uid, record_id, context=context)
            if pick.state not in ['done','confirmed','assigned']:
                raise osv.except_osv(_('Warning !'), _("You may only return pickings that are Confirmed, Available or Done!"))
            valid_lines = 0
            return_history = self.get_return_history(cr, uid, record_id, context)
            for m  in pick.move_lines:
                if (return_history.get(m.id) is not None) and (m.product_qty * m.product_uom.factor > return_history[m.id]):
                        valid_lines += 1
            if not valid_lines:
                raise osv.except_osv(_('Warning !'), _("There are no products to return (only lines in Done state and not fully returned yet can be returned)!"))
        return res
    
    def get_return_history(self, cr, uid, pick_id, context=None):
        """ 
        Get  return_history.

        @param pick_id: Picking id
        @return: A dictionary which of values.
        """
        pick_obj = self.pool.get('fuel.picking')
        pick = pick_obj.browse(cr, uid, pick_id, context=context)
        return_history = {}
        for m  in pick.move_lines:
            if m.state == 'done':
                return_history[m.id] = 0
                for rec in m.move_history_ids2:
                    # only take into account 'product return' moves, ignoring any other
                    # kind of upstream moves, such as internal procurements, etc.
                    # a valid return move will be the exact opposite of ours:
                    #     (src location, dest location) <=> (dest location, src location))
                    if rec.location_dest_id.id == m.location_id.id \
                        and rec.location_id.id == m.location_dest_id.id:
                        return_history[m.id] += (rec.product_qty * rec.product_uom.factor)
        return return_history

    def create_returns(self, cr, uid, ids, context=None):
        """ 
        Creates return picking.

        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {} 
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('fuel.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('fuel.return.picking.memory')
        wf_service = netsvc.LocalService("workflow")
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        new_picking = None
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = True
        returned_lines = 0
        
#        Create new picking for returned products
        if pick.type=='out':
            new_type = 'in'
        elif pick.type=='in':
            new_type = 'out'
        else:
            new_type = 'internal'
        seq_obj_name = 'fuel.picking.' + new_type
        new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        new_picking = pick_obj.copy(cr, uid, pick.id, {'name':'%s-%s-return' % (new_pick_name, pick.name),
                'move_lines':[], 'state':'draft', 'type':new_type,
                'date':date_cur,})
        
        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            new_location = move.location_dest_id.id
            returned_qty = move.product_qty
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty

            if returned_qty != new_qty:
                set_invoice_state_to_none = False
            if new_qty:
                returned_lines += 1
                new_move=move_obj.copy(cr, uid, move.id, {
                    'product_qty': new_qty,
                    'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id,
                        new_qty, move.product_uos.id),
                    'fuel_picking_id':new_picking, 'state':'draft',
                    'location_id':new_location, 'location_dest_id':move.location_id.id,
                    'date':date_cur,})
                move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move)]})
        if not returned_lines:
            raise osv.except_osv(_('Warning !'), _("Please specify at least one non-zero quantity!"))

        if set_invoice_state_to_none:
            pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'})
        wf_service.trg_validate(uid, 'fuel.picking', new_picking, 'draft', cr)
        pick_obj.force_assign(cr, uid, [new_picking], context)
        # Update view id in context, lp:702939
        view_list = {
                'out': 'view_fuel_picking_tree',
                'in': 'view_fuel_picking_tree',
                'internal': 'vpicktree',
            }
        data_obj = self.pool.get('ir.model.data')
        res = data_obj.get_object_reference(cr, uid, 'fuel_management', view_list.get(new_type, 'vpicktree'))
        context.update({'view_id': res and res[1] or False})
        return {
            'domain': "[('id', 'in', ["+str(new_picking)+"])]",
            'name': 'Fuel Picking List',
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'fuel.picking',
            'type':'ir.actions.act_window',
            'context':context,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

