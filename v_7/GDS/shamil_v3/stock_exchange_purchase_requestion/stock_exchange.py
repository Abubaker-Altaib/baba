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


# ----------------------------------------------------
# Exchange Order 
# ----------------------------------------------------
class exchange_order(osv.Model):
    
    _inherit = "exchange.order"

    _columns = {
        'purchase_requestion_id' : fields.many2one('ireq.m', string="Purchase Requestion Id"),
        'category_id':fields.many2one('product.category', 'Category',),

    }





        
        


    def __init__(self, pool, cr):
        """Add a Purchase states """
        super(exchange_order, self)._columns['state'].selection.append(('wait_purchase', 'Waiting For Purchase Procedure'))
        super(exchange_order, self)._columns['state'].selection.append(('goods_in_stock','Approve'))
        return super(exchange_order, self).__init__(pool, cr)





    def approve_exchange ( self , cr , uid , ids , context = None ):


        """ Change Exchange Order State To Approve state """

        self.write( cr , uid , ids , { 'state' : 'approved' } ,context=context )

        return True  




    def onchange_category_check_products_line(self,cr,uid,ids,cat_id,line_ids,context=None):\
        #TODO check the method to work with the exchange order 
        """
        Checks the products lines and order category to prohibit the user from change the category
        of the order  and mack sure no products from diffrent category in the order.

        @param cat_id: product category id 
        @param line_ids: product id 
        @return: values of product category and warning 
        """
        res={}
        if line_ids:
            for pro in line_ids:
                product = self.pool.get('exchange.order.line').browse(cr,uid,pro[1]).product_id                   
                values = {'category_id': cat_id} 
                # Update the category value by the old one
                values.update({'category_id': product.categ_id.id}) 
                if (cat_id != product.categ_id):
                    warning={'title': _('Warning'), 'message': _('The selected cateogry is not related to ordered products, the 				ordered  product have this category %s') % product.categ_id.name}
                    return {'value':values,'warning':warning}
        return {}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
