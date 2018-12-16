# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from osv import osv, fields
from tools.translate import _

class create_clearance_from_po(osv.osv_memory):
    """
    To create purchase clearance from purchase order """
    _name = "create.clearance.from.po"
    _description = "Create Clearance"
    _columns = {
                'purchase_order_ref': fields.many2one('purchase.order', 'Purchase order', readonly=True),
                'current_date': fields.date('Current Date', readonly=True),
                }
    
    _defaults = {
                'purchase_order_ref':lambda cr,uid,ids,context:context['active_id'],
                'current_date': lambda *a: time.strftime('%Y-%m-%d'),
                }
    
    def create_clearace(self, cr, uid, ids, context=None):
        """
        wizard function to create clearance.

        @return: Empty dictionary
        """
        purchase_obj = self.pool.get('purchase.order').browse(cr,uid,context['active_id'])
        clearance_obj=self.pool.get('purchase.clearance')
        clearance_product_odj=self.pool.get('purchase.clearance.products')
        purchase_clearance_id = purchase_obj.clearance_ids
        if purchase_clearance_id:
            raise osv.except_osv(_('Wrong Operation !'),
                _('This purchase order already have clearance ,\n you can create more clearance for it from the clearance view'))

	elif purchase_obj.purchase_type == 'internal':
            raise osv.except_osv(_('Wrong Operation !'),
                _('This Purchase Order Type is Internal so u can not create clearance'))

        else:
            clearance_id = clearance_obj.create(cr, uid, {
                               'purchase_order_ref': context['active_id'] or False,
                               'type': 'internal',
                	       'delivery_date':purchase_obj.minimum_planned_date,
                               'ship_method':purchase_obj.delivery_method,
                               'description': 'purchase order '+ purchase_obj.name ,
                               'clearance_purpose':'purchase',
                               'currency':purchase_obj.currency_id.id,
                               'final_invoice_amount': purchase_obj.amount_total,
                               'company_id':purchase_obj.company_id.id,
                               })
        for product in purchase_obj.order_line:
            clearance_product_odj.create(cr,uid,{
                                  'name': product.name or '',
                                  'category_id' : purchase_obj.cat_id.id or product.product_id.categ_id.id ,
                                  'product_id': product.product_id.id,
                                  'price_unit': product.price_unit,
                                  'product_qty': product.product_qty, 
                                  'product_uom': product.product_uom.id,
                                  'products_clearance_id': clearance_id,
                                  'description': 'purchase order '+ purchase_obj.name , 
                                  'purchase_line_id': product.id,
                                  'price_unit':product.price_unit,         
                                                 })
            
        return {}
    

