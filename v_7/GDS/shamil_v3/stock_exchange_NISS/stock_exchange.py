# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp import netsvc

#----------------------------------------------------------
# stock_journal (Inherit)
#----------------------------------------------------------
class product_template(osv.Model):
    _inherit = 'stock.journal'

    USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
    _columns = {
	'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
        'need_visit': fields.boolean('Need Visit', help="If this box is checked then the exchange order for this product must passes by committee before delivered."),
        #'product_manager': fields.many2many('res.users', 'product_template_user','product_id','user_id', 'Product Manager'),
    }

    _defaults={
           'need_visit':0,
              }


class stock_picking(osv.Model):
 
    _inherit = "stock.picking"
 

    _columns = {
	
	'request': fields.many2one('exchange.order','request'  ),	
	 
    }
     

stock_picking()


class stock_picking_out(osv.osv):
 
    _inherit = "stock.picking.out"
 

    _columns = {
	
	'request': fields.many2one('exchange.order','request'  ),
	 
    }
     

stock_picking_out()
# ----------------------------------------------------
# Exchange Order inherit
# ----------------------------------------------------

class exchange_order(osv.Model):
    _inherit = 'exchange.order'

    USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
    _columns = {
                'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),

                }

    _defaults = {

          'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,

                }

    def has_category_manager(self, cr, uid, ids, context=None):
        """
        Condition Workflow function.
        @return: boolean 
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.ttype == "other":
                if order.stock_journal_id.need_visit:
                    return True
                for line in order.order_line:
                    if line.product_id.need_visit:
                        return True
        return super(exchange_order, self).has_category_manager(cr, uid, ids, context)

    def action_approve_order(self, cr, uid, ids, context=None):
        """ 
        Workflow function Changes order state to approve.
        @return: True
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.state == 'category_manager' and order.ttype == 'other':
                for line in order.order_line:
                   if line.product_id.need_visit and uid not in [manager.id for manager in line.product_id.product_manager]:
                       raise osv.except_osv(_('Error !'), _('You can not approve this order because you are not responsible for visit for this product.'))
        return super(exchange_order, self).action_approve_order(cr, uid, ids, context)

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ 
        Creates pickings and appropriate stock moves for given order lines, then
        confirms the moves, makes them available, and confirms the picking.
        @param partial_datas : Dictionary containing details of partial picking
        like  moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        pick_obj=self.pool.get('stock.picking')
        line_obj = self.pool.get('exchange.order.line')
        stock_move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr, uid, ids, context=context):
            picking_id = None
            todo_moves = []
            for line in order.order_line:
                if line.state in ('done', 'cancel', 'picking'):
                    continue
                partial_data = partial_datas.get('move%s' % (line.id), {})
                product_qty = partial_data.get('product_qty') or 0.0
                if not picking_id and product_qty != 0:
                    picking_id = pick_obj.create(cr, uid, self. _prepare_order_picking(cr, uid, order, context=context))
                if product_qty != 0:
                    move_id = stock_move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id,product_qty ,context=context))
                    todo_moves.append(move_id)
                stock_move_obj.action_confirm(cr, uid, todo_moves)
                #stock_move_obj.force_assign(cr, uid, todo_moves)
                line_obj.write(cr, uid, [line.id], {'delivered_qty' : line.delivered_qty + product_qty})
                if line.approved_qty - line.delivered_qty == product_qty:
                    line_obj.write(cr, uid, [line.id], {'state' :'picking'})
                if picking_id:
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

                self.write(cr, uid, ids, {})
        return res

