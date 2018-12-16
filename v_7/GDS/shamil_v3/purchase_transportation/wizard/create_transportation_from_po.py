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

class create_transportation_from_po(osv.osv_memory):
    """
    To create purchase transportaion fro purchase order """

    _name = "create.transportation.from.po"
    _description = "Create Transportation"
    _columns = {
                'purchase_order_ref': fields.many2one('purchase.order', 'Purchase order', readonly=True),
                'current_date': fields.date('Current Date', readonly=True),
                }
    
    _defaults = {
                'purchase_order_ref':lambda cr,uid,ids,context:context['active_id'],
                'current_date': lambda *a: time.strftime('%Y-%m-%d'),
                }
        
    def create_transportation(self, cr, uid, ids, context=None):
        """
        To create transportaion from purchase order
       
        @return: Empty dictionary
        """
        purchase_obj = self.pool.get('purchase.order').browse(cr,uid,context['active_id'])
        transportation_obj=self.pool.get('transportation.order')
        transportation_product_odj=self.pool.get('transportation.order.line')
        purchase_transportation_id = purchase_obj.transportation_ids
        if purchase_transportation_id:
            raise osv.except_osv(_('Wrong Operation !'),
                _('This purchase order already have transportation ,\n you cane create more transportation for it from the transportation view'))

	#elif purchase_obj.purchase_type == 'foreign':
            #raise osv.except_osv(_('Wrong Operation !'),
                #_('This Purchase Order Type is Foreign so u can not create Transportation From here ,\n It will create automaticaly After clearance is done ,\n Or From transportation view'))

        else:
            transportation_id = transportation_obj.create(cr, uid, {
                               'purchase_order_id': context['active_id'] or False,
                               'description':'from purchase order '+ purchase_obj.name,
                               'purpose':'purchase' 
                               })
        for product in purchase_obj.order_line:
            transportation_product_odj.create(cr,uid,{
                                  'name': product.name or '',
                                  'product_id': product.product_id.id,
                                  'price_unit': product.price_unit,
                                  'product_qty': product.product_qty, 
                                  'product_uom': product.product_uom.id,
                                  'transportation_id': transportation_id,
                                  'description': 'purchase order '+ purchase_obj.name ,
                                  'notes': 'created from purchase order '+ purchase_obj.name,
                                  'purchase_line_id': product.id,
                                  'price_unit':product.price_unit, 
                                  'code_calling': True,         
                                                 })
            
        return {}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
