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
import time
import netsvc

class multi_quote(osv.osv):
    """ class to add fields to purchase quote to check the products for more than one supplier """
    
    
    _inherit = 'pur.quote'
    
    
    
    def _get_order(self, cr, uid, ids, context={}):
        """ 
        To read the products of quotaion.

        @return: products ids
        """
        line_ids = [line.id for line in self.pool.get('pq.products').browse(cr, uid, ids, context=context)]
        return line_ids
    
    
    def button_dummy(self, cr, uid, ids, context={}):
        """ 
        Dummy function to recomputes the functional felids. 

        @return: True
        """
        super(multi_quote, self).button_dummy( cr, uid, ids, context=context)
        
        return True
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Override _amount_all Function To Compute amount depend on value of  the chosen field       
        """
        res = {}
        res = super(multi_quote, self)._amount_all( cr, uid, ids, field_name, arg,context=context)        
        for quote in self.browse(cr, uid, ids, context=context):
                res[quote.id] = {
                    'amount_untaxed': 0.0, 
                    'amount_tax': 0.0, 
                    'amount_total': 0.0, 
                }
                if quote.pq_pro_ids :
                    if quote.pq_ir_ref.multi == 'multiple' :
                        total_with_tax = total_without_taxes = 0.0
                        for line in quote.pq_pro_ids:
                            if line.chosen == True :
                                unit_price = line.price_subtotal
                                total_without_taxes += unit_price
                                tax_to_unit = 0.0
                                for tax in self.pool.get('account.tax').compute_all(cr, uid, quote.taxes_id, line.price_unit, line.product_qty)['taxes']:
                                    unit_tax= tax.get('amount', 0.0)
                                    tax_to_unit += unit_tax/line.product_qty
                                    total_with_tax += unit_tax
                                line_tax = tax_to_unit + line.price_unit 
                                
                                cr.execute("UPDATE pq_products SET price_unit_tax=%s, price_unit_total=%s where id = %s ", (tax_to_unit, line_tax, line.id))
                                res[quote.id] = {
                                'amount_tax':total_with_tax, 
                                'amount_untaxed':total_without_taxes, 
                                'amount_total':total_with_tax + total_without_taxes
                            }
                    else :
                        total_with_tax = total_without_taxes = 0.0
                        for line in quote.pq_pro_ids:
                            unit_price = line.price_subtotal
                            total_without_taxes += unit_price
                            tax_to_unit = 0.0
                            for tax in self.pool.get('account.tax').compute_all(cr, uid, quote.taxes_id, line.price_unit, line.product_qty)['taxes']:
                                unit_tax= tax.get('amount', 0.0)
                                tax_to_unit += unit_tax/line.product_qty
                                total_with_tax += unit_tax
                            line_tax = tax_to_unit + line.price_unit 
                            
                            cr.execute("UPDATE pq_products SET price_unit_tax=%s, price_unit_total=%s where id = %s ", (tax_to_unit, line_tax, line.id))
                            res[quote.id] = {
                            'amount_tax':total_with_tax, 
                            'amount_untaxed':total_without_taxes, 
                            'amount_total':total_with_tax + total_without_taxes
                        }
        return res
    
    _columns = {
                'multi_purchase_total': fields.float('Total For Multi Purchase'),
                'amount_untaxed': fields.function(_amount_all, method=True, string='Untaxed Amount',
            store={
                'pur.quote': (lambda self, cr, uid, ids, c={}: ids, ['pq_pro_ids', 'taxes_id'], 10), 
                'pq.products': (_get_order,  ['price_unit','product_qty'], 10), 
            }, multi="sums", help="The amount without tax"), 
                'amount_tax': fields.function(_amount_all, method=True, string='Taxes', 
            store={
                'pur.quote': (lambda self, cr, uid, ids, c={}: ids, ['pq_pro_ids', 'taxes_id'], 10), 
                'pq.products': (_get_order, ['price_unit','product_qty'], 10), 
            }, multi="sums", help="The tax amount"), 
                'amount_total': fields.function(_amount_all, method=True, string='Total',
            store={
                'pur.quote': (lambda self, cr, uid, ids, c={}: ids, ['pq_pro_ids', 'taxes_id'], 10), 
                'pq.products': (_get_order, ['price_unit','product_qty'], 10), 
            }, multi="sums"), 
                
                }


    def confirmed(self, cr, uid, ids, context=None):
        """
        Inhertited to add the check of multi suppliers, product just in one quote
        and must select product in the quote        
        """
        # product just in one quote
        quote = self.browse(cr,uid,ids)[0]
        requisition = self.pool.get('ireq.m').browse(cr, uid, quote.pq_ir_ref.id)
        if requisition.multi in ['multiple']:
            quotations = self.pool.get('pur.quote').search(cr, uid, [('pq_ir_ref','=',requisition.id)])
            for test_quote in self.pool.get('pur.quote').browse(cr, uid, quotations):
                name1=''
                name2=''
                if test_quote.id != quote.id :
                    for product in quote.pq_pro_ids :
                        if product.chosen :
                            name1 = product.name
                            count = 0
                            for quots in test_quote.pq_pro_ids :
                                if quots.chosen and test_quote.state not in ['cancel']:
                                    name2=quots.name
                                    if name1==name2:
                                        count += 1
                                if count != 0:
                                    raise osv.except_osv(('Product is already chosen !'), ('The Product %s must be chosen just ones ...')%(name1,))

        # must select product 
        multi_po = requisition.multi
        for quotes_ in self.browse(cr, uid, ids):
            count=0
            if multi_po in ['multiple']:
                for product in quotes_.pq_pro_ids :
                    if product.chosen:
                        count += 1
                if count == 0:
                    raise osv.except_osv(('No product is chosen !'), ('You must choose products from this quote first then confirm it or cancel it ...'))
        super(multi_quote, self).confirmed(cr, uid, ids)      
        

    def cancel(self, cr, uid, ids, context=None):
        """
        To modify the utomatic cancelling 
        """        
        #TODO chech if this functiion is needed (when cancel the last one mack the requisition move )
        super(multi_quote, self).cancel(cr, uid, ids, context)
        multi_po = self.browse(cr, uid, ids)[0].pq_ir_ref.multi
        if multi_po in ['multiple']:
            qoute_obj = self.browse(cr, uid, ids)[0]
            requisition = self.pool.get('ireq.m').browse(cr, uid, qoute_obj.pq_ir_ref.id)
            requisition_qoute = self.pool.get('pur.quote').search(cr, uid, [('pq_ir_ref','=', requisition.id)])
            count1=0
            count2=0
            for qoute in self.pool.get('pur.quote').browse(cr, uid, requisition_qoute):
                count1 += 1
                if qoute.state in ['done','cancel']:
                    count2 += 1
            if count1 == count2 :
                notes = self.pool.get('ireq.m').browse(cr, uid, qoute.pq_ir_ref.id).notes or ''
                self.pool.get('ireq.m').write(cr, uid, qoute.pq_ir_ref.id, {'state':'wait_confirmed','notes':notes})
    

    def done(self,cr, uid, ids, context=None): 
########### product just in one quote
        record = self.browse(cr, uid, ids)[0]
        req = self.pool.get('ireq.m').browse(cr, uid, record.pq_ir_ref.id)
        internal_products = self.pool.get('ireq.products')
        if not req.multi in ['multiple']:
            super(multi_quote, self).done(cr, uid, ids, context)
        else:
            all_qoutes = self.pool.get('pur.quote').search(cr, uid, [('pq_ir_ref','=',req.id)])
            for product in self.pool.get('pur.quote').browse(cr, uid, all_qoutes):
                name1=''
                name2=''
                if product.id != record.id :
                    for pro in record.pq_pro_ids :
                        if pro.chosen :
                            name1 = pro.name
                            count = 0
                            for quots in product.pq_pro_ids :
                                if quots.chosen and record.state not in ['cancel']:
                                    name2=quots.name
                                    if name1==name2:
                                        count += 1
                                if count != 0:
                                    raise osv.except_osv(('Product is already chosen !'), ('The Product %s must be chosen just ones ...')%(name1,))
        self.write(cr, uid, ids, {'state':'done'})
        # For updating the internal requestion products prices
        quote = self.browse(cr, uid, ids)[0]
        for product in quote.pq_pro_ids:
            if product.req_product:
                internal_products_ids = product.req_product.id
            else: 
                internal_products_ids = internal_products.search(cr, uid, [('pr_rq_id', '=', quote.pq_ir_ref.id), ('product_id', '=', product.product_id.id)])
            internal_products_ids = internal_products.search(cr, uid, [('pr_rq_id', '=', quote.pq_ir_ref.id), ('product_id', '=', product.product_id.id)])
            internal_products.write(cr, uid, internal_products_ids, {'price_unit': product.price_unit })
        multi_po=self.browse(cr,uid,ids)[0].pq_ir_ref.multi
        #TODO check when to close the quote state 
        all_qoutes = self.pool.get('pur.quote').search(cr, uid, [('pq_ir_ref','=',req.id)])
        count1=0
        count2=0
        for product in self.pool.get('pur.quote').browse(cr, uid, all_qoutes):
            count1 += 1
            if product.state in ['done','cancel']:
                count2 += 1
        if count1 == count2 :
            self.pool.get('ireq.m').write(cr, uid, product.pq_ir_ref.id, {'state':'wait_confirmed'})
        return True


    def make_purchase_order(self,cr, uid, ids, context=None):  
       purchase_line_obj = self.pool.get('purchase.order.line')
       or_id = super(multi_quote, self).make_purchase_order(cr, uid, ids, context=context)
       for quote in self.browse(cr, uid, ids):
           if quote.pq_ir_ref.multi in ['multiple']:
               for one_quote in quote.pq_ir_ref.q_ids:
                   if one_quote.state == 'done':
                       for product in one_quote.pq_pro_ids:
                           if not product.chosen:
                               order_line = purchase_line_obj.search(cr, uid, [('quote_product','=', product.id)])
                               purchase_line_obj.unlink(cr, uid, order_line)           
       return or_id


class multi_quote_products(osv.osv):
    """
    To add chosen field to qoutes products"""

    _inherit = 'pq.products'
    _columns = {
               'chosen' : fields.boolean('Chosen',help="The Chosen field is determined whether the field is selected from this partner or not."), 
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
