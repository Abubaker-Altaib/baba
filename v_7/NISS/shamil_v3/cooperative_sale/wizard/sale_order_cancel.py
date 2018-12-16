# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
import time
from datetime import timedelta,date , datetime
from openerp.tools.translate import _
import netsvc

#----------------------------------------
#sale_order_cancel
#----------------------------------------

class sale_order_cancel_wiz(osv.osv_memory):

    _name = "sale.order.cancel"
    _description = "Sale order cancel wizard"

    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'shop_id' : fields.many2one('sale.shop','Shop'),
        'state' : fields.selection([
            ('draft', 'Draft'),
            ('complete', 'waiting for co-oprative manager'),
	    ('invoice','waiting to pay'),
		], 'Status', select=True),
        'cancel_type' : fields.selection([
            ('draft', 'Draft'),
            ('complete2', 'waiting for co-oprative manager'),
	    ('invoice','waiting to pay'),
            ('done', 'Done'),
		], 'Cancel Type', select=True ,required=True),
        'order_cancel_lines': fields.many2many('sale.order',string = 'Order Lines',), }

    def order_cancel(self,cr,uid,ids,context={}):
        picking_obj = self.pool.get('stock.picking')
        loan_obj = self.pool.get('hr.employee.loan')
        stock_move_obj=self.pool.get('stock.move')
        sale_order_obj=self.pool.get('sale.order')
	for record in self.browse(cr,uid,ids,context=context):
		for line in record.order_cancel_lines:
				if record.cancel_type != 'done' :
					cr.execute ("""update sale_order set state='cancel' where id=%s """%line.id)
				else :
  					check_picking = picking_obj.search(cr,uid,[('sale_id','=',line.id),('state','not in',('done','cancel'))],context=context)
  					check_loan = loan_obj.search(cr,uid,[('sale_order_id','=',line.id)],context=context)
					if check_picking :
						for order in check_picking :
							picking = picking_obj.browse(cr,uid,order,context=context)
                           				picking_obj.write(cr ,uid , picking.id , {'state' : 'cancel'},context = context)
							move_ids = stock_move_obj.search(cr,uid,[('picking_id','=',picking.id)],context=context)
							for move in move_ids :
                           					stock_move_obj.write(cr ,uid , move , {'state' : 'cancel'},context = context)
				
						
					if check_loan :
						for loan in check_loan :
							loan_id = loan_obj.browse(cr,uid,loan,context=context)
                                			loan_obj.write(cr ,uid , loan_id.id , {'state' : 'rejected'},context = context)
                           		sale_order_obj.write(cr ,uid , line.id , {'state' : 'cancel'},context = context)
					
					

	return {}


