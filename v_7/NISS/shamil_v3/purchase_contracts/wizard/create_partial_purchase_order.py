# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

# how can we use the existing things to make the changes of the code 
from osv import fields, osv
import time

class create_partial_purchase_order_contract(osv.osv_memory):
    _description='create partial purchase order for contract'
    _name = 'create.partial.purchase.order.contract'
    _columns = {
                'purchase_contract': fields.many2one('purchase.contract', 'Purchase Contract', readonly=True),
                'current_date': fields.date('Current Date', readonly=True),
                'products_ids':fields.one2many('create.partial.purchase.order.products.contract', 'wizard_id' , 'Products'),                
                }
    
    _defaults = {
                'purchase_contract':lambda cr,uid,ids,context:context['active_id'],
                'current_date': lambda *a: time.strftime('%Y-%m-%d'),
                }
    
    def default_get(self, cr, uid, fields, context=None):
        """
        To get default values for the object.

        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        contract_obj = self.pool.get('purchase.contract')
        res ={}
        contract_ids = context.get('active_ids', [])
        if not contract_ids:
            return res

        result = []
        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            for product in contract.contract_line_ids:
                if product.all_quantity_purchased:
                    continue
                result.append(self.__create_partial_purchase_order_products_contract(product))
        res.update({'products_ids': result})
        if 'current_date' in fields:
            res.update({'current_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res


    def __create_partial_purchase_order_products_contract(self, product):
        """
        To read the contract product information in to 
        partila purchase order products.

        @return: Dictionary of product information
        """
        product_memory = {
            'product_id' : product.product_id.id,
            'product_qty':product.product_qty,
            'purchased_qty':product.purchased_quantity,
            'left_qty' : (product.product_qty - product.purchased_quantity) ,
            'contract_product_id' : product.id,
        }
        return product_memory
    
    def create_partial_purchase_order(self, cr, uid, ids, context=None):
        """
        Create a purchase order acording to the information of the wizard,
        ckech the quantity and mack the contract done if all the quantity 
        is purchased ckech (fright,packing and discount) to match the purchased 
        quantity and remove the extra purchase order lines if exsist.

        @return: Empty dictionary 
        """
        contract_obj = self.pool.get('purchase.contract')
        contract_line_obj = self.pool.get('purchase.contract.line')
        order_obj = self.pool.get('purchase.order')
        order_line_obj = self.pool.get('purchase.order.line')
        contract_ids = context.get('active_ids', [])
        contract = contract_obj.browse(cr, uid, contract_ids, context=context)
        purchase_id = self.create_purchase_order(cr, uid, ids, contract)
        order = order_obj.browse(cr, uid, purchase_id)
        for wizard in self.browse(cr, uid, ids):
            line_list = []
            all_the_new_quantity = 0.0
            for product in wizard.products_ids:
                new_qty = product.desired_qty
                all_the_new_quantity += new_qty
                if new_qty > (product.contract_product_id.product_qty - product.contract_product_id.purchased_quantity):
                    raise osv.except_osv(('Wrong Amount Of Quantity !'), ("The Quantity for product '%s' is more than the Left Quantity")%(product.contract_product_id.name))
                order_line = order_line_obj.search(cr, uid, [('product_id','=',product.contract_product_id.product_id.id),('order_id','=',order.id)])
                line_list.append(order_line[0])
                if not new_qty:
                    order_line_obj.write(cr, uid, order_line[0],{'product_qty':0.0})
                else :
                    order_line_obj.write(cr, uid, order_line[0],{'product_qty':new_qty})
                    new_purchased_qty = product.contract_product_id.purchased_quantity + new_qty
                    contract_line_obj.write(cr, uid,product.contract_product_id.id, {'purchased_quantity':new_purchased_qty})
                    if new_purchased_qty == product.contract_product_id.product_qty:
                        contract_line_obj.write(cr, uid,product.contract_product_id.id, {'all_quantity_purchased': True})
            for line in order.order_line:
                if not line.product_qty or line.id not in line_list: 
                    order_line_obj.unlink(cr, uid, [line.id])
                    if line.id in line_list:
                        line_list.remove(line.id)
            if len(line_list) == 0 :
                order_obj.unlink(cr, uid, [order.id])
            done_items = []
            for item in contract[0].contract_line_ids: 
                if item.all_quantity_purchased:
                    done_items.append(item.id)
            if len(done_items) == len(contract[0].contract_line_ids):
                contract_obj.write(cr, uid,contract[0].id, {'state':'done'})
        return {}
    
    def create_purchase_order(self,cr, uid, ids, contracts, context=None):
        """
        Override to change the constrain of only one purchase ordr for every
        object that create a purchase order.
   
        @return: created purchase order id
        """
        pur_q_obj = self.pool.get('purchase.contract')
        for contract in contracts:
            order_id = pur_q_obj.make_purchase_order(cr, uid, [contract.id])
        return order_id



class create_partial_purchase_order_products_contract(osv.osv_memory):
    """
    To manage the wizard lines which contain the contract products """

    _description="create partial purchase order products"
    _name = "create.partial.purchase.order.products.contract"
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product"),
        'product_qty' : fields.float("Product Quantity"),
        'desired_qty' : fields.float("Desired  Quantity"),
        'purchased_qty' : fields.float("Purchased Quantity"),
        'left_qty' : fields.float("Left Quantity"),
        'contract_product_id' : fields.many2one('purchase.contract.line', "Products"),
        'wizard_id' : fields.many2one('create.partial.purchase.order.contract', string="Wizard"),
        }                  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
