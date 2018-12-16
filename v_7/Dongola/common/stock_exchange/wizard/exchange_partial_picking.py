# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import osv,fields
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from tools.float_utils import float_compare
import decimal_precision as dp
from openerp.tools.translate import _

class exchange_partial_picking_line(osv.TransientModel):
    _name = "exchange.partial.picking.line"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True, ondelete='CASCADE',readonly=True),
        'quantity' : fields.float("Quantity", digits_compute=dp.get_precision('Product UoM'), required=True),
        'real_qty' : fields.float("Real Stock", digits_compute=dp.get_precision('Product UoM'),required=True,readonly=True),
        'virtual_qty' : fields.float("Virtual Stock",digits_compute=dp.get_precision('Product UoM'),required=True,readonly=True),     
        'move_id' : fields.many2one('exchange.order.line', "Move", ondelete='CASCADE'),
        'wizard_id' : fields.many2one('exchange.partial.picking', string="Wizard", ondelete='CASCADE'),
    }
    def create(self, cr, uid, vals, context={}):
        """
        Create picking with move if we have exchange order line unless we can not create stock picking with move
        @param vals: dict. of values
        @return :super create function of exchange_partial_picking_line 
        """
        if 'move_id' not in vals:
            raise osv.except_osv(_('Error!'), _('You cann\'t create new order!.'))    
        return super(exchange_partial_picking_line, self).create(cr, uid, vals, context=context)        

        
class exchange_partial_picking(osv.osv_memory):
    _name = "exchange.partial.picking"
    _description = "Exchange Picking Processing Wizard"
    _columns = {
        'date': fields.datetime('Date', required=True),
        'move_ids' : fields.one2many('exchange.partial.picking.line', 'wizard_id', 'Product Moves'),
        'exchange_id': fields.many2one('exchange.order', 'Exchange', required=True, ondelete='CASCADE'),
     }
    
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values from the object
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.        
        """
        if context is None:
            context = {}
        res = super(exchange_partial_picking, self).default_get(cr, uid, fields, context=context)
        exchange_ids = context.get('active_ids', [])
        if not exchange_ids or (not context.get('active_model') == 'exchange.order') \
            or len(exchange_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        exchange_id, = exchange_ids
        if 'exchange_id' in fields:
            res.update(exchange_id=exchange_id)
        if 'move_ids' in fields:
            exchange = self.pool.get('exchange.order').browse(cr, uid, exchange_id, context=context)
            moves = [self._partial_move_for(cr, uid, m, context=context) for m in exchange.order_line if m.state not in ('done','cancel','picking')]
            res.update(move_ids=moves)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res

    def _partial_move_for(self, cr, uid, move, context=None):
        """ 
        Used to extract value from  move_id and return it as dictionary
        @param move :browse record of move id
        @return : dictionary
        """
        context = {}
        context['uom']=move.product_uom.id
        context['location'] = move.order_id.location_dest_id.id
        product = self.pool.get('product.product').browse(cr, uid, move.product_id.id, context=context)
        partial_move = {
            'product_id' : move.product_id.id,
            'quantity' : move.approved_qty-move.delivered_qty,
            'move_id' : move.id,
            'real_qty': product.qty_available,
            'virtual_qty': product.virtual_available
        }
        return partial_move

    def do_partial(self, cr, uid, ids, context=None):
        """ 
        Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
        exchange_order = self.pool.get('exchange.order')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data={}
        for wizard_line in partial.move_ids:
            line_uom = wizard_line.move_id.product_uom
            move_id = wizard_line.move_id.id
         
            #Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide Proper Quantity !'))

            #Compute the quantity 
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if qty_in_line_uom  > wizard_line.move_id.product_qty:
                raise osv.except_osv(_('Processing Error'), _('Processing quantity is larger than the approved quantity!'))
            if qty_in_line_uom > wizard_line.real_qty:
                    raise osv.except_osv(_('Warning'), _('Processing quantity  is larger than the available quantity in is location!'))
 
            partial_data['move%s' % (move_id)] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.move_id.product_uom.id,
            }
        exchange_order.do_partial(cr, uid, [partial.exchange_id.id], partial_data, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
