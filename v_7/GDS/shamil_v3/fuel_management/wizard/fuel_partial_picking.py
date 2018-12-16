# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from tools.float_utils import float_compare
import decimal_precision as dp
from tools.translate import _
  
class fuel_partial_picking_line(osv.TransientModel):

    """Inherit stock partial picking and add override some fields """

    _inherit = "stock.partial.picking.line"
    _name = "fuel.partial.picking.line"
    _rec_name = 'product_id'
    _columns = {
        'real_qty' : fields.float("Real Stock", digits_compute=dp.get_precision('Product UoM'),required=True,readonly=True),        
        'wizard_id' : fields.many2one('fuel.partial.picking', string="Wizard", ondelete='CASCADE'),
    } 
    
class fuel_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    _name = "fuel.partial.picking"
    _description = "Partial Picking Processing Wizard"

    def _hide_tracking(self, cursor, user, ids, name, arg, context=None):  
        """
        Override function field  used to decide if the column production lot has to be shown on the moves or not
        
        @param name: field name
        @param arg: other argument
        @return: dictionary of value
        """
        res = {}
        for wizard in self.browse(cursor, user, ids, context=context):
            res[wizard.id] = any([not(x.tracking) for x in wizard.move_ids])
        return res

    _columns = {
        'move_ids' : fields.one2many('fuel.partial.picking.line', 'wizard_id', 'Product Moves'),
        'picking_id': fields.many2one('fuel.picking', 'Picking', required=True, ondelete='CASCADE'),
     }


    def default_get(self, cr, uid, fields, context=None):
        """ 
        To get default values for the object.

        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        if context is None: context = {}
        context['active_model']='stock.picking'
        res = super(fuel_partial_picking, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        context['active_model']='fuel.picking'
        if not picking_ids or (not context.get('active_model') == 'fuel.picking') \
            or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(picking_id=picking_id)
        if 'move_ids' in fields:
            picking = self.pool.get('fuel.picking').browse(cr, uid, picking_id, context=context)
            moves = [self._partial_move_for(cr, uid, m) for m in picking.move_lines if m.state not in ('done','cancel')]
            res.update(move_ids=moves)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res
    
    def _partial_move_for(self, cr, uid, move):
        """
        Inherit to update partial move and set real quantity
        @param move:ID of stock move
        @return:super method of fuel_partial_picking   
        """
        context = {}
        c = context.copy()
        c['uom']=move.product_uom.id
        c['location'] = move.location_id.id
        product = self.pool.get('product.product').browse(cr, uid, move.product_id.id, context=c)
        partial_move= super(fuel_partial_picking,self)._partial_move_for(cr, uid, move)
        partial_move.update( {
            'real_qty': product.qty_available
        })
        return partial_move
    
    def do_partial(self, cr, uid, ids, context=None):
        """ 
        Creates pickings and appropriate stock moves for given order lines, then
        confirms the moves, makes them available, and confirms the picking.
        @param partial_datas : Dictionary containing details of partial picking
        like  moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
        fuel_picking = self.pool.get('fuel.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date' : partial.date
        }
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:
            #added by nctr
            quantity = uom_obj._compute_qty(cr, uid, wizard_line.product_uom.id, wizard_line.quantity, wizard_line.move_id.product_uom.id)
            #Adding a check whether any move line contains exceeding  real location qty to original moveline
            context = {}
            c = context.copy()
            c['uom']=wizard_line.product_uom.id
            c['location'] = wizard_line.move_id.location_id.id
            product = self.pool.get('product.product').browse(cr, uid, wizard_line.move_id.product_id.id, context=c)
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide Proper Quantity !'))
            if quantity  > wizard_line.move_id.product_qty:
                raise osv.except_osv(_('Processing Error'), _('Processing quantity for is larger than the available quantity !'))

            if (wizard_line.move_id.fuel_picking_id.type in ['out','internal']) and (quantity > product.qty_available ):
                    raise osv.except_osv(_('Warning'),_('Processing quantity  is larger than the available quantity in is location!'))

            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id
            #finish
            #Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide Proper Quantity !'))

            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor <> 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning'), _('The uom rounding does not allow you to ship "%s %s", only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g), 
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name =  'fuel.picking.' + picking_type
                move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
                                                    'product_id': wizard_line.product_id.id,
                                                    'product_qty': wizard_line.quantity,
                                                    'product_uom': wizard_line.product_uom.id,
                                                    'prodlot_id': wizard_line.prodlot_id.id,
                                                    'location_id' : wizard_line.location_id.id,
                                                    'location_dest_id' : wizard_line.location_dest_id.id,
                                                    'fuel_picking_id': partial.picking_id.id
                                                    },context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            partial_data['move%s' % (move_id)] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
            }
            if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
                                                                  product_currency=wizard_line.currency.id)
        fuel_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
