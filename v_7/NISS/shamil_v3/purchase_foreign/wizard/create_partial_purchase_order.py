# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

# how can we use the existing things to make the changes of the code 
from openerp.osv import fields, osv
import time
from tools.translate import _

class create_partial_purchase_order(osv.osv_memory):
    _description='create partial purchase order'
    _name = 'create.partial.purchase.order'
    _columns = {
                'purchase_requisition': fields.many2one('ireq.m', 'Purchase Requisition', readonly=True),
                'current_date': fields.date('Current Date', readonly=True),
                'products_ids':fields.one2many('create.partial.purchase.order.products', 'wizard_id' , 'Products'),                
                }
    
    _defaults = {
                'purchase_requisition':lambda cr,uid,ids,context:context['active_id'],
                'current_date': lambda *a: time.strftime('%Y-%m-%d'),
                }
    
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        requisition_obj = self.pool.get('ireq.m')
        res ={}
        requisition_ids = context.get('active_ids', [])
        if not requisition_ids:
            return res

        result = []
        for req in requisition_obj.browse(cr, uid, requisition_ids, context=context):
            for product in req.pro_ids:
                if product.all_quantity_purchased:
                    continue
                result.append(self.__create_partial_purchase_order_products(product))
        res.update({'products_ids': result})
        if 'current_date' in fields:
            res.update({'current_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res


    def __create_partial_purchase_order_products(self, product):
        product_memory = {
            'product_id' : product.product_id.id,
            'product_qty':product.product_qty,
            'purchased_qty':product.purchased_quantity,
            'left_qty' : (product.product_qty - product.purchased_quantity) ,
            'desired_qty' : (product.product_qty - product.purchased_quantity) ,
            'requisition_product_id' : product.id,
        }
        return product_memory
    
    def create_partial_purchase_order(self, cr, uid, ids, context=None):
        requisition_obj = self.pool.get('ireq.m')
        requisition_line_obj = self.pool.get('ireq.products')
        order_obj = self.pool.get('purchase.order')
        order_line_obj = self.pool.get('purchase.order.line')
        quote_obj = self.pool.get('pur.quote')
        quote_line_obj = self.pool.get('pq.products')
        requisition_ids = context.get('active_ids', [])
        req = requisition_obj.browse(cr, uid, requisition_ids, context=context)
        purchase_id = self.create_purchase_order(cr, uid, ids, req)

        order_ids = order_obj.browse(cr, uid, purchase_id)
        for wizard in self.browse(cr, uid, ids):
            if not wizard.products_ids:
               raise osv.except_osv(('No Products !'), ("You can not create Purchase Order Without Products"))
            line_list = []
            all_the_new_quantity = 0.0
            freight_amonut = 0.0
            packing_amount = 0.0
            for product in wizard.products_ids:
                order_line  = []
                new_qty = product.desired_qty
                all_the_new_quantity += new_qty
                if new_qty > (product.requisition_product_id.product_qty - product.requisition_product_id.purchased_quantity):
                    raise osv.except_osv(('Wrong Amount Of Quantity !'), ("The Quantity for product '%s' is more than the Left Quantity")%(product.requisition_product_id.name))
                
                for order in order_ids:
                    order_line = order_line_obj.search(cr, uid, [('product_id','=',product.requisition_product_id.product_id.id),('order_id','=',order.id),('product_qty','=',product.requisition_product_id.product_qty)])
                    for record in order_line:
                        if record not in line_list:
                            line_list.append(record)
                    #line_list.append(order_line[0])
                    if len(order_line) > 0 :
                        if not new_qty:
                            order_line_obj.write(cr, uid, order_line[0],{'product_qty':0.0})
                        else :
                            order_line_obj.write(cr, uid, order_line[0],{'product_qty':new_qty})
                            new_purchased_qty = product.requisition_product_id.purchased_quantity + new_qty
                            requisition_line_obj.write(cr, uid,product.requisition_product_id.id, {'purchased_quantity':new_purchased_qty})
                            if new_purchased_qty == product.requisition_product_id.product_qty:
                                requisition_line_obj.write(cr, uid,product.requisition_product_id.id, {'all_quantity_purchased': True})

            for order in order_ids:
                for line in order.order_line:
                    freight_amonut = line.price_unit_freight
                    packing_amount = line.price_unit_packing
                    if not line.product_qty or line.id not in line_list:
                        order_line_obj.unlink(cr, uid, [line.id])
                        if line.id in line_list:
                            line_list.remove(line.id)
                if len(line_list) == 0 :
                    order_obj.unlink(cr, uid, [order.id])
                else:
                    order_obj.write(cr, uid, purchase_id, {'freight': all_the_new_quantity * freight_amonut, 'packing': all_the_new_quantity * packing_amount} )                
                done_items = []
                for item in req[0].pro_ids: 
                    if item.all_quantity_purchased:
                        done_items.append(item.id)
                if len(done_items) == len(req[0].pro_ids):
                    requisition_obj.write(cr, uid,req[0].id, {'state':'done'})
        return {}
    
    def create_purchase_order(self,cr, uid, ids, requisition, context=None):
        pur_q_obj = self.pool.get('pur.quote')
        for ir in requisition:
            qoute_ids = [qoute.id for qoute in ir.q_ids if qoute.state == 'done']
            order_id = pur_q_obj.make_purchase_order(cr, uid, qoute_ids)
        return order_id

create_partial_purchase_order()
class create_partial_purchase_order_products(osv.osv_memory):




    def _check_negative(self, cr, uid, ids, context=None):

        """ 
        Constrain function to check the quantity and price and frieght and packing should be greater than 0
        @return Boolean True or False
        """
        record = self.browse(cr, uid, ids[0], context=context)
        if record.product_qty <= 0 :
           raise osv.except_osv(_('Error !'), _('Product Quantity must be greater than zero'))
        if record.desired_qty < 0 :
           raise osv.except_osv(_('Error !'), _('Desire Quantity must be greater than zero'))
        if record.purchased_qty >  record.product_qty :
           raise osv.except_osv(_('Error !'), _('Purchased Quantity must be Less than or equal Product Quantity '))
        if record.left_qty <= 0:
           raise osv.except_osv(_('Error !'), _('Lefting Quantity must be greater than zero'))

        return True 
    _description="create partial purchase order products"
    _name = "create.partial.purchase.order.products"
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product"),
        'product_qty' : fields.float("Product Quantity"),
        'desired_qty' : fields.float("Desired  Quantity"),
        'purchased_qty' : fields.float("Purchased Quantity"),
        'left_qty' : fields.float("Left Quantity"),
        'requisition_product_id' : fields.many2one('ireq.products', "Products"),
        'wizard_id' : fields.many2one('create.partial.purchase.order', string="Wizard"),
        }    


    _constraints = [

         (_check_negative, 'One of this Fields[ Quantity ,Product UOM , Freight and Packing ] is less than one ... ',['product_qty']),
                   ]              
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
