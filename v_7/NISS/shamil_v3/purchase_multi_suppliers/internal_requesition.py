# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from tools.translate import _
from osv import osv
from osv import fields
import netsvc
import time
from datetime import datetime

class multi_ireq_m(osv.osv):
    _inherit = 'ireq.m'
    _columns = {
        'multi':fields.selection([('exclusive','One Supplier'),('multiple','Multiple suppliers')],'Requisition Type',states={'confirmed':[('readonly',True)], 'wait_confirmed':[('readonly',True)],'approve1':[('readonly',True)],'checked':[('readonly',True)],'wait_budget':[('readonly',True)],'cancel':[('readonly',True)],'done':[('readonly',True)]}, help="Purchase Requisition (exclusive):  On the confirmation of a purchase order, it cancels the remaining purchase order.\nPurchase Requisition(Multiple):  It allows to have multiple purchase orders.On confirmation of a purchase order it does not cancel the remaining orders"""),  
          }  
    def onchange_category_check_products_line(self,cr,uid,ids,cat_id,pro_ids,context=None):
        """
        This function overwrite the main function in purchase custom module to make the request contains different products categories .

        @param cat_id: product category id 
        @param pro_ids: product id 
        """
        super(exchange_order,self).onchange_category_check_products_line(cr,uid,ids,cat_id,pro_ids,context)
        
        return {}




  


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
