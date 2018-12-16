# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm
from openerp.tools.translate import _
import decimal_precision as dp


class stock_partial_picking_line(osv.TransientModel):

#FIXME: Depend on stock
#TODO : add new column (real_qty)

    _inherit = "stock.partial.picking.line"

    _columns = {
       'real_qty' : fields.float("Real Stock", digits_compute=dp.get_precision('Product UoM')),   
    }

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        while False in res.get('move_ids',[]): 
            res.get('move_ids',[]).remove(False)
        return res

    def _partial_move_for(self, cr, uid, move, context=None):
        """
        Inherit to add real stock quantity in partial move dict
        @param move: id of picking move

        @return: id
        """
        context = {}
        context['uom']=move.product_uom.id
        context['location'] = move.location_id.id
        product = self.pool.get('product.product').browse(cr, uid, move.product_id.id, context=context)
        partial_move= super(stock_partial_picking,self)._partial_move_for(cr, uid, move, context=context)
        partial_move.update( {
            'real_qty': product.qty_available 
        })
        if move.state != 'assigned' and move.picking_id.type != 'in':
            partial_move=False
        return partial_move

    def do_partial(self, cr, uid, ids, context=None):
        """
        Inherit fuction to add constrains in picking 

        @return: super function of stock_partial_move
        """
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:
            line_uom = wizard_line.product_uom

            #Adding a check whether any move line contains exceeding  real location qty to original moveline
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity,  wizard_line.move_id.product_uom.id)

            if qty_in_line_uom  > wizard_line.move_id.product_qty:
                raise osv.except_osv(_('Processing Error'), _('Processing quantity for is larger than the available quantity !'))
           

            if (picking_type in ['out','internal'])  and partial.picking_id.state == 'assigned' and (qty_in_line_uom > wizard_line.real_qty ):
                    raise osv.except_osv(_('Warning'), _('Processing quantity  is larger than the available quantity in is location!'))
            
        return super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)

class stock_return_picking(osv.osv_memory):
    _name = 'stock.return.picking'
    _inherit = 'stock.return.picking'

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
        move_obj = self.pool.get('stock.move')
        data_obj = self.pool.get('stock.return.picking.memory')
        data = self.read(cr, uid, ids[0], context=context)
        record_id = context and context.get('active_id', False) or False
        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            if not mov_id:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            return_history = self.get_return_history(cr, uid, record_id, context)       
            qty = move.product_qty - return_history.get(move.id, 0)
            returned_qty = move.product_qty
            if new_qty > qty:
               raise osv.except_osv(_('Warning !'), _("The return quantity greater than move quantity"))
            if new_qty < 0.0:
               raise osv.except_osv(_('Warning !'), _("The return quantity less than zero."))
        return super(stock_return_picking, self).create_returns(cr, uid, ids, context=context)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
