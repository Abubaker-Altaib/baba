# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class qoute(osv.osv):
    """
    To change the purchase quote to fit foreign purchase """

    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence. 

        @return: new object id 
        """       
        quote_id = super(qoute, self).create(cr, user, vals, context)
        ireq_id = self.pool.get('ireq.m').search(cr, user, [('q_ids','=',quote_id)])
        type =''
        product_type =''
        for purchase in self.pool.get('ireq.m').browse(cr, user, ireq_id):
            type = purchase.purchase_type
            product_type = purchase.product_type
            self.write(cr, user, quote_id,{'purchase_type': type, 'product_type': product_type})
        return quote_id
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Method to compute functional fields: the amount of lines either with taxes 
        or without taxes and add (freight and packing). 

        @param field_name:  'amount_untaxed', 'amount_tax', 'amount_total' fields
        @param arg: other argument
        @return: dictionary of value of fields amount_untaxed, 
                                               amount_tax, 
                                               amount_total       
        """
        result = super(qoute, self)._amount_all(cr, uid, ids, field_name, arg, context)
        for quote in self.browse(cr, uid, ids, context=context):
                if result[quote.id]['amount_total'] == 0.0:
                    return result
                total=0.0
                packing = 0.0
                qty_sum =0.0
                for product in quote.pq_pro_ids:
                    qty_sum+=product.product_qty
                for item in quote.pq_pro_ids:
                    rate=item.product_qty/qty_sum
                    freight_total=rate*quote.freight
                    packing = rate * quote.packing
                    if item.product_qty:
                        unit_freight=freight_total/item.product_qty
                        unit_packing = packing/item.product_qty
                    if item.price_unit_tax:
                        total=unit_freight+item.price_unit_tax+item.price_unit+unit_packing
                    else:
                        total=unit_freight+item.price_unit+unit_packing
                    cr.execute("UPDATE pq_products SET price_unit_freight=%s, price_unit_total=%s, price_unit_packing=%s where id = %s ", (unit_freight,total,unit_packing,item.id))
                result[quote.id]['amount_total'] +=quote.freight 
                result[quote.id]['amount_total'] +=quote.packing 
                result[quote.id]['amount_total'] *= (1-(quote.discount or 0.0)/100.0)              
        return result
    
    def _get_order(self, cr, uid, ids, context={}):
        """
        Override to make the functional field work.

        @return: quotaion lines id
        """
        line_ids = [line.id for line in self.pool.get('pq.products').browse(cr, uid, ids, context=context)]
        return line_ids

    def get_default_pricelist(self, cr, uid, context=None):
        pricelist_obj = self.pool.get('product.pricelist')
        pricelist = pricelist_obj.search(cr, uid, [('type', '=', 'purchase')])
        if len(pricelist) > 0:
            return pricelist[0]
        return False

    def get_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        currency = company.currency_id.id
        return currency

    
    PRODUCTS_TYPE = [
        ('service', 'Service'),
        ('items', 'Items'),
    ]       
    TYPE_SELECTION = [
        ('internal', 'Internal Purchase'),
        ('foreign', 'Foreign Purchase'),]
        
    DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
        ('land_freight', 'Land Freight'),
        ('free_zone','Free Zone'),    ]
    
    PYMENT = [('lc','Letter of credit'),
              ('cash','Cash Transfer Advance'),
              ('cad','CAD Cash Against Document'),
              ('partial','Partial and complete after receipt'),
              ('defer','Defer Payment')
              ]
    
    _inherit = 'pur.quote'
    _columns = {
        'incoterm': fields.many2one('stock.incoterms', 'Incoterm', help="Incoterm which stands for 'International Commercial terms' implies its a series of terms which             are used in the commercial transaction."),
        'delivery_method': fields.selection(DELIVERY_SELECTION, 'Method of dispatch', select=True),
        'picking_policy': fields.selection([('partial', 'Partial Delivery'), ('complete', 'Complete Delivery')],
        'Picking Policy', help="""deliver all at once as (complete), or partial shipments"""),
        'freight': fields.float('Freight', digits=(16, 2)),
        'packing': fields.float('Packing', digits=(16, 2)),
        'discount': fields.float('Discount(%)', digits=(16, 8)),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        'other_conditions': fields.text('other conditions'),
        'notes': fields.text('Notes'),
        'delivery_date': fields.date('Delivery Date', select=True, help="Date on which delivery will be done"), 
        'purchase_type':fields.selection(TYPE_SELECTION, 'Purchase Type', select=True),
        'payment_method': fields.selection(PYMENT, 'Payment Method', select=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', help="Pricelist for current supplier",states={'done':[('readonly',True)]}),
        'currency_id': fields.many2one('res.currency','Currency',select=1),
        'product_type':fields.selection(PRODUCTS_TYPE, 'Product Type', select=True), 
        'amount_untaxed': fields.function(_amount_all, method=True, string='Untaxed Amount', 
            store={
                'pur.quote': (lambda self, cr, uid, ids, c={}: ids, ['pq_pro_ids', 'taxes_id'], 10), 
                'pq.products': (_get_order, ['price_unit','product_qty'], 10), 
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
    _defaults = {
                'freight':  0.0,
                'packing':  0.0,
                'pricelist_id': get_default_pricelist,
                'currency_id': get_currency,
    }
    
    def on_change_supplier(self, cr, uid, ids, supplier):
        """ 
        To checks if this supplier already selected by an other qoutation 
	    if so it raise an exception else continue.

	    @param quote_ids: the ids of all created code.
	    @return: Dictonary of supplier and supplier's vats 
        """
        res = {}
        quote_obj = self.pool.get('pur.quote')
        if supplier:
            supplier_obj = self.pool.get('res.partner').browse(cr, uid, supplier)
            for quote in self.browse(cr, uid, ids):
                quote_ids = quote_obj.search(cr, uid, [('pq_ir_ref', '=', quote.pq_ir_ref.id)])
                for created_quote in quote_ids:
                    if created_quote != quote.id:
                        quote = quote_obj.browse(cr, uid, created_quote)
                        if quote.supplier_id.id == supplier:  #Check if this supplier already selected by an other quote
                            res = {'value': { 'supplier_id':'', }}
                            raise osv.except_osv(('Duplicated Supplier !'), ('This Supplier is already chosed for another Quote \n Please .. Chose another supplier ..'))
            vat =supplier_obj.vat_subjected
            pricelist = supplier_obj.property_product_pricelist_purchase.id
            if pricelist:
                res = {'value': { 'vat_supp':vat, 'pricelist_id': pricelist}}
            res = {'value': { 'vat_supp':vat }}
        return res
    
    def make_purchase_order(self, cr, uid, ids, context=None):
        """
        Workflow function override to create letter of credit
        and change the values of purchase order according to 
        foreign purchase.

        @return creates purchase order  
        """
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        product_obj = self.pool.get('product.product')
        quote_product_obj = self.pool.get('pq.products')
        letter_of_credit_obj = self.pool.get('purchase.letter.of.credit')
        letter_of_credit_line_obj = self.pool.get('purchase.letter.of.credit.line') 
        purchase_id = super(qoute, self).make_purchase_order(cr, uid, ids, context)
        for quote in self.browse(cr, uid, ids):
            partner = quote.supplier_id           
            invoice = 'order'
            if quote.payment_method in ['cash','cad','partial']:
                invoice = 'order' 
            if quote.product_type == 'service':
                invoice = 'order'
            purchase_obj.write(cr, uid, purchase_id,{'purchase_type':quote.purchase_type,
                                                     'delivery_method':quote.delivery_method,
                                                     'invoice_method':invoice, 
                                                     'freight':quote.freight,
                                                     'packing':quote.packing,
                                                     'currency_id': quote.currency_id and quote.currency_id.id or False,
                                                     'pricelist_id':quote.pricelist_id and quote.pricelist_id.id or False,
                                                     })
            for purchase in purchase_obj.browse(cr, uid, purchase_id):
                for line in purchase.order_line :                    
                    product_id = quote_product_obj.search(cr,uid,[('pr_pq_id','=',quote.id),('product_id','=',line.product_id.id),('price_unit','=',line.price_unit)])
                    if len(product_id)>0 :
                        product = quote_product_obj.browse(cr,uid,product_id)[0]
                        line.write({'price_unit_freight': product.price_unit_freight*(1-(quote.discount or 0.0)/100.0),
                                                              'price_unit_packing': product.price_unit_packing*(1-(quote.discount or 0.0)/100.0),
                                                              'price_unit_tax':product.price_unit_tax *(1-(quote.discount or 0.0)/100.0), 
                                                              'price_unit_total':product.price_unit_total *(1-(quote.discount or 0.0)/100.0),
                                                              'price_unit':product.price_unit*(1-(quote.discount or 0.0)/100.0), 
                                                                  })
        
        return purchase_id

class quote_products(osv.osv):
    """
    To modify purchase quote to add foreign purchase """
    
    _inherit = 'pq.products'
    _columns = {
        'product_packaging': fields.many2one('product.packaging', 'Packing', help="Control the packages of the products"),
        'price_unit_freight': fields.float('Freight',digits=(16, 2)),
        'price_unit_packing': fields.float('Packing',digits=(16, 2)),
}
    _defaults = {
                 'price_unit_freight':0.0,
                 'price_unit_packing': 0.0,
                } 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
