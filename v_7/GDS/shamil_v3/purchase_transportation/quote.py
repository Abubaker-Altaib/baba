# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields 
from osv import osv
import netsvc
import time
import datetime
from tools.translate import _

class quote (osv.osv):
    """
    Purchase Quote module for managing purchase transportaion quotation"""

    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence.

        @return super create() method 
        """
        if vals.get('name', False) in ['/', False]:
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'transportation.quotes')
        return super(quote, self).create(cr, user, vals, context)
    
    def _get_order(self, cr, uid, ids, context={}):
        """ 
        To read the quotaion products.

        @return: products ids
        """
        line_ids = [line.quote_id.id for line in self.pool.get('transportation.quotes.products').browse(cr, uid, ids, context=context)]
        return line_ids
    
    def button_dummy(self, cr, uid, ids, context={}):
        """ 
        Dummy function to recomputes the functional felids. 

        @return: True
        """ 
        for quote in self.browse(cr, uid, ids):
            if quote.price_total:
                quote.caculate_price(quote)
        return True
   
    
    def _calc_amount(self, cr, uid, ids,field_name, arg, context=None):
        """
        Functional field function to compute quotaion line amount

        @return: dictionary of line amount values
        """
        res = {}
        for quote in self.browse(cr, uid, ids):
            res[quote.id] = 0.0
            for quote_line in quote.quotes_products_ids:
                res[quote.id] += quote_line.price_unit * quote_line.product_qty
        return res
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Functional field function to compute the amount of line either with taxes or without taxes 

        @return dictionary of {
                'amount_untaxed': value,                 
                'amount_tax': value,                     
                'amount_total': value,           
                 }
        """
        res = {}
        for quote in self.browse(cr, uid, ids, context=context):
            res[quote.id] = {
                'amount_untaxed': 0.0, 
                'amount_tax': 0.0, 
                'amount_total': 0.0, 
            }
            val = val1 = 0.0
            for line in quote.quotes_products_ids:
                unit_price = line.price_subtotal
                val1 += unit_price
                tax_to_unit = 0.0
                for tax in self.pool.get('account.tax').compute_all(cr, uid, quote.taxes_id, line.price_unit, line.product_qty)['taxes']:
                    unit_tax= tax.get('amount', 0.0)
                    if line.product_qty > 0.0 :
		            tax_to_unit += unit_tax/line.product_qty
		            val += unit_tax
                line_tax = tax_to_unit + line.price_unit 
                cr.execute("UPDATE transportation_quotes_products SET price_unit_tax=%s, price_unit_total=%s where id = %s ", (tax_to_unit, line_tax, line.id))
                res[quote.id] = {
                'amount_tax':val, 
                'amount_untaxed':val1, 
                'amount_total':val + val1
            }
        return res
    
    STATE = [('draft', 'Draft'), 
             ('confirmed', 'Confirmed'), 
             ('done', 'Approved'), 
             ('cancel', 'Cancelled')]
    
    _name = 'transportation.quotes'
    _columns = {
                'name': fields.char('Quote ID', size=256, required=True, readonly=True), 
                'delivery_period': fields.integer('Delivery period',states={'done':[('readonly',True)],'cancel':[('readonly',True)],'confirmed':[('readonly',True)]}), 
                'quote_no':fields.char('Quote No.', size=256, help="No. of Quotation of supplier",states={'done':[('readonly',True)],'cancel':[('readonly',True)],'confirmed':[('readonly',True)]}),
                'supplier_id':fields.many2one('res.partner', 'Transporter',states={'done':[('readonly',True)],'cancel':[('readonly',True)],'confirmed':[('readonly',True)]}),
                'supplier_vat': fields.boolean('VAT Legal Statement',states={'done':[('readonly',True)],'cancel':[('readonly',True)],'confirmed':[('readonly',True)]}),  
                'taxes_id': fields.many2many('account.tax', 'purchase_quote_taxe', 'q_id', 'tax_id', 'Taxes',states={'done':[('readonly',True)],'cancel':[('readonly',True)],'confirmed':[('readonly',True)]}), 
                'quote_date': fields.date('Quote Date',states={'done':[('readonly',True)],'cancel':[('readonly',True)],'confirmed':[('readonly',True)]}), 
                'transportation_id': fields.many2one('transportation.order', 'Transportation ref',),
                'quotes_products_ids':fields.one2many('transportation.quotes.products', 'quote_id' , 'Items',), 
                'state': fields.selection(STATE, 'State', readonly=True, select=True),
                'price_total': fields.float('Price in Total',states={'done':[('readonly',True)],'cancel':[('readonly',True)],'confirmed':[('readonly',True)]}),  
                'amount_untaxed': fields.function(_amount_all, method=True, string='Untaxed Amount', 
            store={
                'transportation.quotes': (lambda self, cr, uid, ids, c={}: ids, None, 10), 
                'transportation.quotes.products': (_get_order,None, 10), 
            }, multi="sums", help="The amount without tax"), 
               'amount_tax': fields.function(_amount_all, method=True, string='Taxes', 
            store={
                'transportation.quotes': (lambda self, cr, uid, ids, c={}: ids, ['quotes_products_ids', 'taxes_id', 'price_total'], 10), 
                'transportation.quotes.products': (_get_order,None, 10), 
            }, multi="sums", help="The tax amount"), 
                'amount_total': fields.function(_amount_all, method=True, string='Total', 
            store={
                'transportation.quotes': (lambda self, cr, uid, ids, c={}: ids, None, 10), 
                'transportation.quotes.products': (_get_order, None, 10), 
            }, multi="sums"), 
               }
    _defaults = {
                'name': lambda self, cr, uid, context: '/', 
                'state': lambda *a: 'draft', 
                'supplier_vat':0, 
                 }
    _sql_constraints = [ 
        ('name_uniq', 'unique(name)', 'This Quote is already exist  !'), 
        ('name_uniq', 'unique(transportation_id,supplier_id)', 'This supplier is already chosen !'),
        ]  

    def _check_price(self, cr, uid, ids, context=None): 
        """ 
        Constrain function to check the unit_price of items and let just the positive quantity.

        @return: Boolean True or False  
        """
        for quote in self.browse(cr, uid, ids, context=context):
            for line in quote.quotes_products_ids:
                if line.price_unit < 0.0 :
                    return False
        return True

    _constraints = [
        (_check_price, 'Negative Price ! \n Please .. Enter positive prices for product.',['quotes_products_ids']),
    ]
      
    def on_change_supplier(self, cr, uid, ids, supplier):
        """ 
        To checks if this supplier already selected by an other qoutation 
	    if so it raise an exception else continue.

	    @param quote_ids: the ids of all created code.
	    @return: Dictonary of supplier and supplier's vats 
        """
        res = {}
        quote_obj = self.pool.get('transportation.quotes')
        if supplier:
            for quote in self.browse(cr, uid, ids):
                quote_ids = quote_obj.search(cr, uid, [('transportation_id', '=', quote.transportation_id.id)])
                for created_quote in quote_ids:
                    if created_quote != quote.id:
                        quote = quote_obj.browse(cr, uid, created_quote)
                        if quote.supplier_id.id == supplier:  #Check if this supplier already selected by an other quote
                            res = {'value': { 'supplier_id':'', }}
                            raise osv.except_osv(('Duplicated Supplier !'), ('This Supplier is already chosen for another Quote \n Please .. Chose another supplier ..'))
                        else:
                            vat = self.pool.get('res.partner').browse(cr, uid, supplier).vat_subjected
                            res = {'value': { 'supplier_vat':vat, }}
        return res
    
    def confirmed(self, cr, uid, ids):
        """
        Workflow function to check fields value and then change 
        the states to confirm and call caculate_price() to 
        calculate the price of lines if the price givan in 
        total.
 
        @return: no return value
        """
        # This method is workflow function it checks many field then change the states
        for quote in self.browse(cr, uid, ids):
            if not quote.quote_no: #Check if there is a number 
                raise osv.except_osv(('No Quotation Number !'), ('Please .. Fill supplier quotation Number and Date then make Confirmation ..'))            
            if quote.supplier_id.id: #Check if there is a supplier then continue
                for product in quote.quotes_products_ids:
                    # to calculate the value of all the items when the price in total
                    if quote.price_total:
                        quote.caculate_price(quote)
                        
                        self.write(cr, uid, ids, {'state':'confirmed'})
                    else:            
                        if product.price_unit:
                            if quote.amount_total != 0.0:
                                self.write(cr, uid, ids, {'state':'confirmed'})
                            else:
                                raise osv.except_osv(('Zero Total !'), ('Please .. Enter prices for products and compute then make Confirmation ..'))
                        else:
                            raise osv.except_osv(('Zero Prices !'), ('Please .. Enter prices for products and compute then make Confirmation ..'))
            else:
                raise osv.except_osv(('No Supplier !'), ('Please .. Chose supplier then make Confirmation ..'))
            
            if quote.supplier_vat:
                if not quote.taxes_id:
                    raise osv.except_osv(('No Taxes !'), ('Please .. Fill Taxes then make Confirmation ..'))
                
    def caculate_price(self, cr, uid, ids, quote):
        """
        To calculate the price of lines if the quotaion price givan in total.
        The price is calculated accourding to price percentage of every line.

        @return: True
        """
        qty = 0
        price = 0
        for item in quote.quotes_products_ids:
            qty += item.product_qty
        price = quote.price_total / qty 
        for item in quote.quotes_products_ids:
            item.write({'price_unit':price})
        return True
                                               
    def cancel(self, cr, uid, ids):
        """
        Workflow function to change the state to cancel

        @return: no return value 
        """               
        self.write(cr, uid, ids, {'state':'cancel'})

        
    def action_cancel_draft(self, cr, uid, ids, context=None): 
        """ 
        To changes Trnsportation state to Draft and reset the workflow.

        @return: True 
        """
        #for trans in self.browse(cr, uid, ids):
            #if trans.transportation_id.state not in ['trans_manager']:
               #raise osv.except_osv(_('Wrong action !'), _('You can not cancel the quotaion in this state ..')) 
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            # Deleting the existing instance of workflow and make new one 
            wf_service.trg_delete(uid, 'transportation.quotes', s_id, cr)            
            wf_service.trg_create(uid, 'transportation.quotes', s_id, cr)
        return resssss

    def done(self, cr, uid, ids, n='',context=None):  
        """ 
        Workflow function to changes state to Done, cancel all other quotaions
        and change the transportaion state to trans_manager.

        @return: True 
        """ 
        group_obj = self.pool.get('res.groups')
        users_obj = self.pool.get('res.users')
        internal_obj = self.pool.get('transportation.order')
        internal_products = self.pool.get('transportation.order.line')
        quote_obj = self.pool.get('transportation.quotes')
        users_obj = self.pool.get('res.users')
         
        for quote in self.browse(cr, uid, ids):
            self.write(cr, uid, ids, {'state':'done'})
            for product in quote.quotes_products_ids:
                internal_products_ids = internal_products.search(cr, uid, [('transportation_id', '=', quote.transportation_id.id), ('product_id', '=', product.product_id.id)])
                internal_products.write(cr, uid, internal_products_ids, {'price_unit': product.price_unit })
                
            quote_ids = quote_obj.search(cr, uid, [('transportation_id', '=', quote.transportation_id.id)])
            for created_quote in quote_ids:
                current_quote = quote_obj.browse(cr, uid, created_quote)
                if current_quote.id != quote.id:
                    quote_obj.write(cr, uid, created_quote, {'state':'cancel'})
            group = group_obj.search(cr, uid, [('name', '=', 'Purchase / Commitee Member')]) 
            users = users_obj.search(cr, uid, [('groups_id', '=', group)]) 
            names = ''
            notes = internal_obj.browse(cr, uid, quote.transportation_id.id).notes or ''
            for user in users:
                names = names + '\n' + users_obj.browse(cr, uid, user).name
            internal_obj.write(cr, uid, quote.transportation_id.id, {'state':'invoice', 'notes':notes})
        return True


class quote_products(osv.osv):
    """
    Manage the products of transportaion quotaion"""

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        """
        This function compute the total price amount of line

        @return  dictionary of subtotal value for each line
        """       
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * line.product_qty
        return res
    
    def subtotal(self, cr, uid, ids, price, qty):
        """ 
        On change function to recompute the total price after changing product qty or product unit

	    @param price: price of the product.
        @param qty: quantity of the product.	
        @return: price_subtotal.
        """
        if price < 0:
            raise osv.except_osv(('Negative Price !'), ('Please .. Enter positive prices for product'))
        if price or qty:
            res = {}
            res = {'value': {'price_subtotal': price * qty, }}
        return res
    
    _name = 'transportation.quotes.products'
    _table = 'transportation_quotes_products'            
    _columns = {
                'quote_id': fields.many2one('transportation.quotes', 'Quote Ref', select=True),   
                'name': fields.char('Name', size=64, required=True, readonly=True , select=True),
                'product_id': fields.many2one('product.product', 'Items', readonly=True , change_default=True), 
                'product_qty': fields.float('Quantity', required=True, readonly=True, digits=(16, 2)), 
                'price_unit': fields.float('Unit Price'), 
                'price_unit_tax': fields.float('Tax Unit Price'), 
                'price_unit_total': fields.float('Total Unit Price',digits=(16,4)), 
                'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'), 
                'desc': fields.text('Specification'),
                'transportation_line': fields.many2one('transportation.order.line', 'Transportation Line'),               
                }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
