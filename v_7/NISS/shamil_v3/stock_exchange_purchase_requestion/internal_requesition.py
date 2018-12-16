# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time

from openerp.osv import osv,fields
from openerp import netsvc
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class exchange_order(osv.Model):
    """
    class to add exchange order Id to purchase requestion """
    


    
    _inherit = "ireq.m"

    _columns = {
              'exchane_order_id':fields.one2many('exchange.order', 'purchase_requestion_id' , 'Exchange Order',readonly=True,),

                }
    

    def cancel(self,cr,uid,ids,notes='',context=None):
        """ 
        Workflow function changes order state to cancel and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        #if not notes:

        
        rec = self.browse(cr,uid,ids)[0]
        exch_obj = self.pool.get('exchange.order')
        if rec.exchane_order_id :
           for exchange in rec.exchane_order_id:
               exch_obj.write(cr,uid,[exchange.id],{'state' : 'cancel'})
        return super(exchange_order,self).cancel(cr,uid,ids,notes=notes,context=None)







class pur_quote(osv.Model):
    _inherit = "pur.quote"

    def make_purchase_order(self,cr,uid,ids,context=None):
        """ This Function For Writing Location in purchase order depend on The Location which chose in exchange order  """
        res = {}
        purchase_id = super(pur_quote, self).make_purchase_order(cr, uid, ids, context=context)
        if not isinstance(ids, list):
           ids = [ids]
        for quote in self.browse(cr, uid, ids):
            if quote.pq_ir_ref.ir_ref not in ['/', ''] :
               purchase_obj = self.pool.get('purchase.order')
               exchange_obj = self.pool.get('exchange.order')
               exchange_id = exchange_obj.search(cr, uid,[('name','=', quote.pq_ir_ref.ir_ref)])
               #purchase_id = purchase_obj.search(cr, uid,[('ir_id','=', quote.pq_ir_ref.id)])
               for order in exchange_obj.browse(cr,uid,exchange_id):
                   res = { 
                                'location_id': order.location_dest_id.id,
                                }        
               purchase_obj.write(cr,uid,purchase_id,res)
        return purchase_id 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
