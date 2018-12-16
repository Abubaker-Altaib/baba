# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp import netsvc
import time

from openerp.osv import osv,fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
                'transfered': fields.boolean('Transfered'),

    }
class stock_transfer_picking_memory(osv.osv_memory):
    _name = "stock.transfer.picking.memory"
    _rec_name = 'product_id'

    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True),
        'quantity' : fields.float("Quantity", digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'wizard_id' : fields.many2one('stock.transfer.picking', string="Wizard"),
        'move_id' : fields.many2one('stock.move', "Move"),
        'prodlot_id': fields.related('move_id', 'prodlot_id', type='many2one', relation='stock.production.lot', string='Serial Number', readonly=True),

    }

stock_transfer_picking_memory()


class stock_transfer_picking(osv.osv_memory):
    _name = 'stock.transfer.picking'
    _description = 'transfer Picking'
    _columns = {
        'product_transfer_moves' : fields.one2many('stock.transfer.picking.memory', 'wizard_id', 'Moves'),
        'location_id' : fields.many2one('stock.location', "Detestation Location", required=True, domain=[('usage','=','internal')]),
        
    }

    def default_get(self, cr, uid, fields, context=None):
      
        result1 = []
        if context is None:
            context = {}
        if context and context.get('active_ids', False):
            if len(context.get('active_ids')) > 1:
                raise osv.except_osv(_('Warning!'), _("You may only transfer one picking at a time!"))
        res = super(stock_transfer_picking, self).default_get(cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        if pick:
            transfer_history = self.get_transfer_history(cr, uid, record_id, context)       
            for line in pick.move_lines:
                qty = line.product_qty - transfer_history.get(line.id, 0)
                if qty > 0:
                    result1.append({'product_id': line.product_id.id, 'quantity': qty,'move_id':line.id, 'prodlot_id': line.prodlot_id and line.prodlot_id.id or False})
            if 'product_transfer_moves' in fields:
                res.update({'product_transfer_moves': result1})
        return res

    def view_init(self, cr, uid, fields_list, context=None):

        if context is None:
            context = {}
        res = super(stock_transfer_picking, self).view_init(cr, uid, fields_list, context=context)
        record_id = context and context.get('active_id', False)
        if record_id:
            pick_obj = self.pool.get('stock.picking')
            pick = pick_obj.browse(cr, uid, record_id, context=context)
            if pick.state not in ['done','confirmed','assigned']:
                raise osv.except_osv(_('Warning!'), _("You may only transfer pickings that are Confirmed, Available or Done!"))
            valid_lines = 0
            transfer_history = self.get_transfer_history(cr, uid, record_id, context)
            for m  in pick.move_lines:
                if m.state == 'done' and m.product_qty * m.product_uom.factor > transfer_history.get(m.id, 0):
                    valid_lines += 1
            if not valid_lines:
                raise osv.except_osv(_('Warning!'), _("No products to transfer (only lines in Done state and not fully transfered yet can be transfered)!"))
        return res
    
    def get_transfer_history(self, cr, uid, pick_id, context=None):

        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, pick_id, context=context)
        transfer_history = {}
        for m  in pick.move_lines:
            if m.state == 'done':
                transfer_history[m.id] = 0
                for rec in m.move_history_ids2:
                    
                    if (rec.location_dest_id.id == m.location_id.id \
                        and rec.location_id.id == m.location_dest_id.id) \
                        or rec.transfered:
                        transfer_history[m.id] += (rec.product_qty * rec.product_uom.factor)
        return transfer_history

    def create_transfers(self, cr, uid, ids, context=None):

        if context is None:
            context = {} 
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.transfer.picking.memory')
        act_obj = self.pool.get('ir.actions.act_window')
        model_obj = self.pool.get('ir.model.data')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        transfered_lines = 0
        
     
        new_pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking')

        new_picking = pick_obj.copy(cr, uid, pick.id, {
                                        'name': ('%s-%s-Transfer') % (new_pick_name, pick.name),
                                        'move_lines': [], 
                                        'state':'done', 
                                        'type': 'internal',
                                        'date':date_cur,
                                        
        })
        
        val_id = data['product_transfer_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            if not mov_id:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            new_location = move.location_dest_id.id
            transfered_qty = move.product_qty
            for rec in move.move_history_ids2:
                transfered_qty -= rec.product_qty

            if transfered_qty != new_qty:
                set_invoice_state_to_none = False
            if new_qty:
                transfered_lines += 1
                new_move=move_obj.copy(cr, uid, move.id, {
                                            'product_qty': new_qty,
                                            'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                            'picking_id': new_picking, 
                                            'state': 'done',
                                            'location_id': move.location_dest_id.id, 
                                            'location_dest_id': data['location_id'][0],
                                            'date': date_cur,
                                            'prodlot_id': data_get.prodlot_id.id,
                                            'transfered':True,
                })
                move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move)]}, context=context)
        if not transfered_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        
        return {
            'domain': "[('id', 'in', ["+str(new_picking)+"])]",
            'name': _('Transfered Picking'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model': 'stock.picking',
            'type':'ir.actions.act_window',
            'context':context,
        }

stock_transfer_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
