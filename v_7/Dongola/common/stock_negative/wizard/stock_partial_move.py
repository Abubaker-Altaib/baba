# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm
from openerp.tools.translate import _
import time
import decimal_precision as dp
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class stock_partial_move_line(osv.osv_memory):
#FIXME: Depend on stock
#TODO : add new column (real_qty)

    _inherit = "stock.partial.move.line"

    _columns = {
       'real_qty' : fields.float("Real Stock", digits_compute=dp.get_precision('Product UoM'),required=True),   
    }

class stock_partial_move(osv.osv_memory):
    _inherit = 'stock.partial.move'

    def _partial_move_for(self, cr, uid, move, context=None):
        """
        Inherit to add real stock quantity in partial move dict
        @param move : id of picking move

        @return : id
        """
        context = {}
        c = context.copy()
        c['uom']=move.product_uom.id
        c['location'] = move.location_id.id
        product = self.pool.get('product.product').browse(cr, uid, move.product_id.id, context=c)
        partial_move= super(stock_partial_move,self)._partial_move_for(cr, uid, move, context=context)
        partial_move.update( {
            'real_qty': product.qty_available
        })
        return partial_move


    def do_partial(self, cr, uid, ids, context=None):
        """
        Inherit fuction to add constrains in picking 

        @return : super function of stock_partial_move
        """
        assert len(ids) == 1, 'Partial move processing may only be done one form at a time'
        partial = self.browse(cr, uid, ids[0], context=context)
        uom_obj = self.pool.get('product.uom')
        partial_data = {
            'delivery_date' : partial.date
        }

        moves_ids = []
        for move in partial.move_ids:
            quantity = uom_obj._compute_qty(cr, uid, move.product_uom.id, move.quantity, move.move_id.product_uom.id)
            #Adding a check whether any move line contains exceeding  real location qty to original moveline
            context = {}
            c = context.copy()
            c['uom']=move.product_uom.id
            c['location'] = move.move_id.location_id.id
            product = self.pool.get('product.product').browse(cr, uid, move.move_id.product_id.id, context=c)
            if move.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide Proper Quantity !'))

            if quantity  > move.move_id.product_qty:
                raise osv.except_osv(_('Processing Error'), _('Processing quantity for is larger than the available quantity !'))

            if (move.move_id.picking_id.type in ['out','internal']) and (quantity > product.qty_available ):
                    raise osv.except_osv(_('Warning'),_('Processing quantity  is larger than the available quantity in is location!'))

        return super(stock_partial_move, self).do_partial(cr, uid, ids, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
