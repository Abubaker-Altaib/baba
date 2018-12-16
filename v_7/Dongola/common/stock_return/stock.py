# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import netsvc
import time

class stock_return_reason(osv.osv):
    _name = 'stock.return.reason'
    _description = 'Stock Return Reason'
    _order = 'code'
    
    _columns = {
        'code': fields.char('Code', size=12),
        'name': fields.char('Name', size=64, required=True),
        'active':fields.boolean('Active'),
    }
    _defaults = {
       'active':1,
    }


class StockPicking(osv.osv):
    _inherit = 'stock.picking'
    
    _columns = {

        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
    }

class StockPickingIn(osv.osv):
    _inherit = 'stock.picking.in'

    _columns = {    
 
        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
    }

class StockPickingOut(osv.osv):
    _inherit = 'stock.picking.out'
    _columns = {    
    
        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
       } 
  
class stock_return_picking(osv.osv):
    _inherit = 'stock.return.picking'
    _order = 'date desc, id desc'

    def _get_return_type(self, cr, uid, context=None):
        if not context:
            context = {}
        
        type = context.get('default_type', False)
        if type == 'in':
            return 'supplier'
        elif type == 'out':
            return 'customer'
        return 'none'

        return new_id
    _columns = {
        'name': fields.char('Reference', size=64, select=True, readonly=True),
        'date': fields.date('Date',required=True),
        'return_type': fields.selection([
               ('none', 'Normal'),
               ('customer', 'Return from Customer'),
               ('supplier', 'Return to Supplier')], 'Type', required=True),
        'note':        fields.text('Notes'),
        'picking_id': fields.many2one('stock.picking', 'Picking',required=True),
        'return_picking_id': fields.many2one('stock.picking', 'Return Picking',readonly=True),
        'return_reason_id': fields.many2one('stock.return.reason', 'Return Reason'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('complete', 'Complete'),
            ('confirm', 'Confirm'),
            ('except_picking', 'Picking Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange'),
        'product_return_moves' : fields.one2many('stock.return.picking.memory', 'wizard_id', 'Products'),
    }
    _defaults = {
        'return_type': lambda self, cr, uid, context: self._get_return_type(cr, uid, context=context),
        'name': '/',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
    }

    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(stock_return_picking, self).create(cr, user, vals, context)
        return new_id

    def unlink(self, cr, uid, ids, context=None):
        return_picking = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in return_picking:
            if s['state'] == 'draft':
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('can not be able to delete a return picking.'))

        # automatically sending subflow.delete upon deletion
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'stock.return.picking', id, 'return_cancel', cr)

        return super(stock_return_picking, self).unlink(cr, uid, unlink_ids, context=context)

    def default_get(self, cr, uid, fields, context=None):
        fields1=fields
        if 'invoice_state' in fields:
            fields1.remove('invoice_state')
        res = super(stock_return_picking, self).default_get(cr, uid, fields1, context)
        record_id = context and context.get('active_id', False) or []
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        print 
        if pick:
            res.update({'picking_id': pick.id})
            if 'invoice_state' in fields:
                if pick.invoice_state=='invoiced':
                    res.update({'invoice_state': '2binvoiced'})
                else:
                    res.update({'invoice_state': 'none'})
            result1 = []
            return_history = self.get_return_history(cr, uid, record_id, context)       
            for line in pick.move_lines:
                if line.state in ('cancel') or line.scrapped:
                    continue
                qty = line.product_qty - return_history.get(line.id, 0)
                if qty > 0:
                    result1.append({'product_id': line.product_id.id, 'quantity': qty, 'move_id':line.id})
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': result1})
        return res

    def complete_returns(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
			if not rec.product_return_moves:
				raise osv.except_osv(_('Error!'),_('You cannot complete return picking without products.'))
        self.write(cr, uid, ids, {'state': 'complete'})
        return True 

    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.return_picking_id.state not in ('draft','cancel'):
                raise osv.except_osv(
                    _('Unable to cancel this return.'),
                    _('First cancel all return picking related to this return.'))
            wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
        for (id, name) in self.name_get(cr, uid, ids):
            wf_service.trg_validate(uid, 'stock.return.picking', id, 'return_cancel', cr)
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'draft','return_picking_id':False})
        wf_service = netsvc.LocalService("workflow")
        for rec_id in ids:
            wf_service.trg_create(uid, 'stock.return.picking', rec_id, cr)
        return True

    def create_returns(self, cr, uid, ids, context=None):
        """ 
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {} 
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.memory')
        act_obj = self.pool.get('ir.actions.act_window')
        model_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        for rec in self.browse(cr, uid,  ids, context=context):
		    pick = rec.picking_id
		    data = self.read(cr, uid, ids[0], context=context)
		    date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
		    set_invoice_state_to_none = False#True LY by default 
		    returned_lines = 0
		    return_type = 'customer'
		    
		    # Create new picking for returned products
		    if pick.type == 'out':
		        new_type = 'in'
		    elif pick.type == 'in':
		        new_type = 'out'
		    else:
		        new_type = 'internal'
		    seq_obj_name = 'stock.picking.' + new_type
		    new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
		    new_picking_vals = {'name': _('%s-%s-return') % (new_pick_name, pick.name),
		                        'move_lines': [],
		                        'state':'draft',
		                        'type': new_type,
		                        'return': data['return_type'],
		                        'note': data['note'],
		                        'return_reason_id': data['return_reason_id'] and data['return_reason_id'][0],
		                        'date':date_cur,
		                        'invoice_state': data['invoice_state'], }
		    new_picking = pick_obj.copy(cr, uid, pick.id, new_picking_vals)
		    
		    val_id = data['product_return_moves']
		    for v in val_id:
		        data_get = data_obj.browse(cr, uid, v, context=context)
		        mov_id = data_get.move_id.id
		        new_qty = data_get.quantity
		        move = move_obj.browse(cr, uid, mov_id, context=context)
		        if move.state in ('cancel') or move.scrapped:
		            continue
		        new_location = move.location_dest_id.id
		        returned_qty = move.product_qty
		        for rec in move.move_history_ids2:
		            returned_qty -= rec.product_qty

		        #if  data['invoice_state'] == 'none':#returned_qty == new_qty #!= new_qty:
		        #    set_invoice_state_to_none = True#LY False
		        if new_qty:
		            returned_lines += 1
		            new_move_vals = {'product_qty': new_qty,
		                            'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
		                            'picking_id': new_picking,
		                            'state': 'draft',
		                            'location_id': new_location,
		                            'location_dest_id': move.location_id.id,
		                            'date': date_cur,
		                            'note': data['note'],
		                            'return_reason_id': data['return_reason_id'] and data['return_reason_id'][0], }
		            new_move = move_obj.copy(cr, uid, move.id, new_move_vals)
		            move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4, new_move)]}, context=context)
		    if not returned_lines:
		        raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

		    #LY make it can be invoiced
		    if data['invoice_state'] == 'none':#returned_qty == new_qty #!= new_qty:
		        set_invoice_state_to_none = True#LY False
		    if set_invoice_state_to_none:
		        pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'}, context=context)
		    wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
		    pick_obj.force_assign(cr, uid, [new_picking], context)
		    self.write(cr, uid, ids, {'state': 'confirm','return_picking_id':new_picking})
        return new_picking

class stock_return_picking_memory(osv.osv):
    _inherit = "stock.return.picking.memory"

    _sql_constraints = [

        ('quantity_gt_zero', 'CHECK (quantity>=0)', 'The product  quantity should be greater than zero!')
    ]

    def _check_quantity(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid,  ids, context=context):
            returned_qty= rec.move_id.product_qty
            for h in rec.move_id.move_history_ids2:
		        returned_qty -= h.product_qty
            if rec.wizard_id.state =='draft' and rec.quantity > returned_qty: 
                return False
        return True

    _constraints = [
        (_check_quantity, 'Error! Please provide proper Quantity ', ['quantity']),
    ]
