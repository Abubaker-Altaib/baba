# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv
from osv import fields

class purchase_initial_requests(osv.osv):
    """
    To add fields to manage foreign purchase initial requisition """

    TYPE_SELECTION = [
        ('internal', 'Internal Purchase'),
        ('foreign', 'Foreign Purchase'),
    ]
    
    PRODUCTS_TYPE = [
        ('service', 'Service'),
        ('items', 'Items'),
    ]
        
    _inherit = 'ireq.m'
    _columns = {
          'purchase_type':fields.selection(TYPE_SELECTION, 'Purchase Type', select=True),
          'product_type':fields.selection(PRODUCTS_TYPE, 'Product Type', select=True),
          }
    
    _defaults = {
                 'purchase_type':'internal',
                 'product_type': 'items',
                 } 

    def check_type_purpose(self,cr,uid,ids,*args):
        """
        Workflow function to check purchase type to manage foreign 
        purchase workflow.
  
        @return: True or False
        """
        obj = self.browse(cr, uid, ids)[0]
        if obj.purpose == "store":
            return True
        if obj.product_type == "service":
            return True
        return False


class initial_requisition_products(osv.osv):
    """
    To add fields to manage partial purchase order """

    _inherit = 'ireq.products'  
    _columns = {
                'all_quantity_purchased': fields.boolean('All Quantity Purchased',),
                'purchased_quantity': fields.float('Purchased Quantity',digits=(16,4)),
                }
    _defaults = {
                 'purchased_quantity': 0.0,
                 'all_quantity_purchased': False,
                 }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
