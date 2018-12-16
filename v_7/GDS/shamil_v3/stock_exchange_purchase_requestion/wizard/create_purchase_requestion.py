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

class create_purchase_requestion(osv.osv_memory):
    """ 
    class to manage the wizard of creating the purchase requestion """

    _description='create purchase requestion'
    _name = 'create.purchase.requestion'
    _columns = {
                'srock_exchange': fields.many2one('exchange.order', 'Stock Exchange', readonly=True),
                'current_date': fields.date('Current Date', readonly=True),
                'products_ids':fields.one2many('create.purchase.requestion.products', 'wizard_id' , 'Products'),                
                }
    
    _defaults = {
                #'srock_exchange':lambda cr,uid,ids,context:context['active_id'] or False,
                'current_date': lambda *a: time.strftime('%Y-%m-%d'),
                }

    def default_get(self, cr, uid, fields, context=None):
        """ 
        To get default values for the object.

        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        exchang_obj = self.pool.get('exchange.order')
        res ={}
        exchang_ids = context.get('active_ids', [])
        if not exchang_ids:
            return res

        result = []
        for req in exchang_obj.browse(cr, uid, exchang_ids, context=context):
            for product in req.order_line:
                result.append(self.__create_products(product))
        res.update({'products_ids': result})
        if 'current_date' in fields:
            res.update({'current_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res

    def __create_products(self, product):
        product_memory = {
            'product_id' : product.product_id.id,
            'product_qty':product.product_qty,
            'stock_exchange_line' : product.id,
            'description': product.notes,
        }
        return product_memory

    def create_purchase_requestion(self, cr, uid, ids, context=None):
        #TODO change the state of the purchase requestion to quotes and let the wizard in specefic state
        """
        Button function to create purchase requestion from the
 
        @return: Purchase Requestion Id
        """        
        purchase_requestion_obj = self.pool.get('ireq.m')
        exchange = self.pool.get('exchange.order').browse(cr, uid, context['active_id'])
        requestion_lines_obj = self.pool.get('ireq.products')
        prod = self.pool.get('product.product')
        wf_service = netsvc.LocalService("workflow")
        if exchange.purchase_requestion_id:
            raise  osv.except_osv(_('Warning'), _('You allredy create a purchase requestion for this exchange order '))
        for wizard in self.browse(cr, uid, ids):
            requestion_id =  purchase_requestion_obj.create(cr, uid, {'company_id': exchange.company_id.id,
                                                                      'user': context['uid'],
                                                                      'cat_id':exchange.category_id.id or False,
                                                                      'ir_ref': exchange.name, 
                                                                      'department_id' : exchange.department_id.id,
                                                                      'exchane_order_id':[(4, exchange.id)],})
            for wizard_lines in wizard.products_ids:
                product = prod.browse(cr, uid,wizard_lines.product_id.id)
                requestion_lines_obj.create(cr, uid, {'pr_rq_id':requestion_id,
                                                      'product_id': wizard_lines.product_id.id,
                                                      'name': product.name,
                                                      'product_qty': wizard_lines.product_qty,
                                                      'product_uom': product.uom_po_id.id, 
                                                      'desc': wizard_lines.description,})
         
        exchange.write({'purchase_requestion_id':requestion_id , 'state' : 'wait_purchase' }) 
        wf_service.trg_validate(uid, 'ireq.m', requestion_id, 'draft', cr)
        return requestion_id
       

class create_purchase_requestion_products(osv.osv_memory):
    """
    class to manage the purchase requestion lines """

    _description="create purchase requestion products"
    _name = "create.purchase.requestion.products"
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product"),
        'product_qty' : fields.float("Product Quantity"),
        'stock_exchange_line' : fields.many2one('exchange.order.line', "Product"),
        'wizard_id' : fields.many2one('create.purchase.requestion', string="Wizard"),
        'description':fields.char('Description', size=256,),
        } 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
