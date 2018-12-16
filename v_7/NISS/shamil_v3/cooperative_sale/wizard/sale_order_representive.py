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

class sale_order_representive(osv.osv_memory):

    _name = "sale.order.representive"
    _description = "Sale order Representive wizard"

    _columns = {
        'process_type': fields.selection([('print', 'Print sale order'),('done', 'Process Receive')], 'Process type',required=True,),
        #'payment_type': fields.selection([('cash', 'Cash'),('up_cash', 'Installment with Upfront')], 'Payment type',),
        'order_cancel_lines': fields.many2many('sale.order',string = 'Order Lines',), }

    _defaults = {
		'process_type':'print'
		}

    def order_process(self,cr,uid,ids,context={}):
        picking_obj = self.pool.get('stock.picking')
        loan_obj = self.pool.get('hr.employee.loan')
        stock_move_obj=self.pool.get('stock.move')
        sale_order_obj=self.pool.get('sale.order')
	for record in self.browse(cr,uid,ids,context=context):
		lines_ids = [line.id for line in record.order_cancel_lines]
  		check_picking = picking_obj.search(cr,uid,[('sale_id','in',lines_ids),('state','not in',('done','cancel'))],context=context)
                picking_obj.write(cr ,uid , check_picking , {'state' : 'done'},context = context)
		move_ids = stock_move_obj.search(cr,uid,[('picking_id','in',check_picking)],context=context)
                stock_move_obj.write(cr ,uid , move_ids , {'state' : 'done'},context = context)
    def order_print(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'sale.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sale.order.custom',
            'datas': datas,
            }
										
	return {}


