# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from amount_to_text_ar import amount_to_text as amount_to_text_ar


class purchase_order(osv.Model):
    """ 
    To remove pricelist and read configration information from company"""

    _inherit = 'purchase.order'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Overwite funtional filed method to modify the origin function take the currency from company 
        instead of pricelist, the amounts is summation not per line.

        @return: dictionary of value of purchase order amount 
        """
        result = {}
        currency_object = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            result[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            # summation of amount and tax amount of all the purchase order lines
            sum_amont_tax = sum_amont_untaxed = 0.0
            currency = order.company_id.currency_id
            for line in order.order_line:
                sum_amont_untaxed += line.price_subtotal
                for tax in self.pool.get('account.tax').compute_all(cr, uid, line.order_id.taxes_id, line.price_unit, line.product_qty, line.product_id.id, order.partner_id)['taxes']:
                    sum_amont_tax += tax.get('amount', 0.0)           
            # allocating the result to the fields        
            result[order.id]['amount_tax'] = currency_object.round(cr, uid, currency, sum_amont_tax)
            result[order.id]['amount_untaxed'] = currency_object.round(cr, uid, currency, sum_amont_untaxed)
            result[order.id]['amount_total'] = result[order.id]['amount_untaxed'] + result[order.id]['amount_tax']
            total = result[order.id]['amount_total']            
            # get the written total
            currency_format = order.company_id.currency_format
            if currency_format == 'ar':
                result[order.id]['written_total'] = amount_to_text_ar(total, currency_format)
            else: 
                result[order.id]['written_total'] = amount_to_text_ar(total)
        return result
    
    def _get_order(self, cr, uid, ids, context=None):
        """ 
        To call the function from purchase order object
		To be called by field of curent inherited object 

        @return: super _get_order() method
        """
        line = self.pool.get('purchase.order')
        return super(purchase_order, line)._get_order(cr, uid, ids, context)

    def create(self, cr, user, vals, context=None):
        """ 
        Override to read the name field form sequense.  

        @return: created purchase order id 
        """
        if vals.get('name', False) in ['/', False]:
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'purchase.order')
        return super(purchase_order, self).create(cr, user, vals, context)
        
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sign', 'Purchase dept. signed'),
        ('confirmed', 'Supply dept. signed'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('wait', 'Waiting'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
    ]
    
    _columns = {
        'name': fields.char('Order ID', size=64, required=True, readonly=1, select=True, help="unique number of the purchase order,computed automatically when the purchase order is created"),
        'financial_approve': fields.char('Financial Approve', size=64 , readonly=1,),
        'account_analytic_id':fields.many2one('account.analytic.account', 'Analytic Account',),
        'origin': fields.char('Created From', size=64, readonly=1,
            help="Reference of the document that generated this purchase order request."
        ),
        'location_id': fields.many2one('stock.location', 'Destination',readonly=1,states={'draft':[('readonly', False)]}, domain=[('usage', '<>', 'view')]),
        'currency_id': fields.many2one('res.currency','Currency', states={'confirmed':[('readonly', True)], 'approved':[('readonly', True)]}, select=1),
        'date_order':fields.date('Date', readonly=1, required=True, states={'confirmed':[('readonly', True)], 'approved':[('readonly', True)]}, select=True, help="Date on which this document has been created."),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
        'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=False, readonly=True, help="The pricelist sets the currency used for this purchase order. It also computes the supplier price for the selected products/quantities."),
        'department_id':fields.many2one('hr.department', 'Department', readonly=1),
        'taxes_id': fields.many2many('account.tax', 'pur_ord_taxe', 'ord_id', 'tax_id', 'Taxes'),
        'invoice_method': fields.selection([('manual', 'Manual'), ('order', 'From Order'), ('picking', 'From Picking')], 'Invoicing Control',   readonly=1,states={'draft':[('readonly', False)]}, required=True,
            help="From Order: a draft invoice will be pre-generated based on the purchase order. The accountant " \
                "will just have to validate this invoice for control.\n" \
                "From Picking: a draft invoice will be pre-generated based on validated receptions.\n" \
                "Manual: allows you to generate suppliers invoices by chosing in the uninvoiced lines of all manual purchase orders."
        ),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term',readonly=1,states={'draft':[('readonly', False)]}),
        'written_total': fields.function(_amount_all, method=True, string='written Total', type='char', size=128 ,
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'taxes_id'], 10),
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total written amount"),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Untaxed Amount',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'taxes_id'], 10),
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'taxes_id'], 10),
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'taxes_id'], 10),
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total amount"),
}



    def get_default_pricelist(self, cr, uid, context=None):
        pricelist_obj = self.pool.get('product.pricelist')
        pricelist = pricelist_obj.search(cr, uid, [('type', '=', 'purchase')])
        if len(pricelist) > 0:
            return pricelist[0]
        return False


    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'financial_approve': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'purchase.order.fi'),
        'invoice_method': 'order',
        'pricelist_id': get_default_pricelist,
    }



    def action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Override to reset the value of test_report_print when set the object to draft. 

        @return: True 
        """
        super(purchase_order, self).action_cancel_draft(cr, uid, ids, context)
        self.write(cr, uid, ids, {'test_report_print':'/'})
        return True    



class  purchase_order_line(osv.Model):
    """
    To modify the purchase order line amount """

    _inherit = 'purchase.order.line'

    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        """ 
        Functional filed function override to get the price from price unit instead of pricelist. 

        @return: purchase order line amount
        """
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * line.product_qty
        return res
    _columns = {
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute=dp.get_precision('Purchase Price')),
}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
