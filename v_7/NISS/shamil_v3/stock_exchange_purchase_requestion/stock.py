# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp import netsvc



class stock_picking(osv.osv):


      _inherit = "stock.picking"


      
      def action_done(self, cr, uid, ids, context=None):
        """
        Checks if Goods aviable in stock after Purchases Procedure is done 

        @return: True
        """

        super(stock_picking, self).action_done(cr, uid, ids, context=context)
        exchange = self.pool.get('exchange.order')
        for picking_record in self.browse(cr,uid,ids):
            if picking_record.type == 'in' :
	       if picking_record.purchase_id and picking_record.purchase_id.ir_id.ir_ref :
		  exchange_ref = picking_record.purchase_id.ir_id.ir_ref
		  exchange_id = exchange.search(cr , uid , [('name' , '=' , exchange_ref)])
		  for exchange_record in exchange.browse(cr ,uid , exchange_id):
		      if exchange_record.state == 'wait_purchase' :
		         exchange.write(cr , uid , exchange_id , {'state' : 'goods_in_stock' })
        return True
