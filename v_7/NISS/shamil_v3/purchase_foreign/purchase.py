# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv
from osv import fields
import decimal_precision as dp
from tools.translate import _
import time
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

class bill_type(osv.osv):
    """
    Foreign purchase exstra prices types """

    _name = "bill.type"
    _description = ' Bills Type'
    _columns = {
            'name': fields.char('name', size=128, required=True),
            'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide important types."), 
            'property_type_journal': fields.property('account.journal',
                    relation='account.journal', type='many2one',required=True,
                    string='Journal', method=True, view_load=True,
                    help="Accounting Journal in which entries will be automatically posted when purchase order are processed."),
            'property_type_account': fields.property('account.account',
                    type='many2one', relation='account.account',required=True,
                    string='Account', method=True, view_load=True,
                    help='This account will be used when purchase order processed for this type'),       
    }


class purchase_bills(osv.osv):
    """
    To manage foreign purchase extra prices bills"""

    _name = "purchase.bills"
    _description = 'Purchase Bills'
    _columns = {
                'name': fields.char('ID', size=256, required=True, readonly=True), 
                'purchase_id':  fields.many2one('purchase.order', 'Clearance',),
                'bill_amount': fields.float('Bill Amount', digits=(16,2)),  
                'bill_date': fields.date('Bill Date'),
                'bill_no': fields.integer('Bill No' ),
                'type': fields.many2one('bill.type', 'Type', required=True),
                'partner_id':fields.many2one('res.partner', 'Supplier', required=True),
                'description': fields.text('Specification'),
               }
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                }


class purchase(osv.osv):
    """
    Modify purchase order to fit foreign purchase order """

    def _calculate_bills_amount(self, cr, uid, ids):
        """
        To calculate bills total amouunt

        @return: True
        """
        for purchase in self.browse(cr, uid, ids):
            bill_amount_sum = 0.0
            for bills in purchase.purchase_bills:
                bill_amount_sum += bills.bill_amount
            self.write(cr, uid, purchase.id, {'bills_amoun_total': bill_amount_sum, })
        return True

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        Functional field function to calculate the amount_total,amount_untaxed,
        amount_tax and written_total of purchase order to add exstra amount to the 
        purchase order.

        @return: Dictionary of fields value
        """
        res = super(purchase, self)._amount_all(cr, uid, ids, field_name, arg, context)
        for order in self.browse(cr, uid, ids, context=context):
            freight_all = 0.0
            packing_all = 0.0
            for line in order.order_line :
                freight_all += line.price_unit_freight * line.product_qty
                packing_all += line.price_unit_packing * line.product_qty
            self.write(cr, uid, order.id, {'freight': (freight_all), 'packing':(packing_all)})
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']+ (freight_all) +(packing_all)
            currency_format = order.company_id.currency_format
            total = res[order.id]['amount_total']            
            if currency_format == 'ar':
                res[order.id]['written_total'] = amount_to_text_ar(total, currency_format, order.currency_id['units_name'],order.currency_id['cents_name'])
            else: 
                res[order.id]['written_total'] = amount_to_text_ar(total)           
        return res

 
    def _get_order(self, cr, uid, ids, context=None):

        """
        Override to calling the function from purchase order object.

        @return: super _get_order method 
        """
        line = self.pool.get('purchase.order')
        return super(purchase, line)._get_order(cr, uid, ids, context)
    
    DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
        ('land_freight', 'Land Freight'),
        ('free_zone','Free Zone'),    ]
    
    TYPE_SELECTION = [
        ('internal', 'Internal Purchase'),
        ('foreign', 'Foreign Purchase'),
    ]
           
    _inherit = 'purchase.order'
    _columns = {
        'account_voucher_ids': fields.many2many('account.voucher', 'purchase_order_voucher', 'purchase_id', 'voucher_id', 'Account voucher'),
        'purchase_bills':fields.one2many('purchase.bills', 'purchase_id' , 'Other Cost'),
        'bills_amoun_total': fields.float('Billing Total amount', digits=(16,2)),
        'purchase_type':fields.selection(TYPE_SELECTION, 'Purchase Type', select=True),
	    'final_invoice_no':fields.integer('Final Invoice No',size=64,states={'done':[('readonly',True)]}),
	    'final_invoice_date':fields.date('Final Invoice Date', states={'done':[('readonly',True)]}),
 	    'delivery_method': fields.selection(DELIVERY_SELECTION, 'Method of dispatch', select=True , required=False,states={'done':[('readonly',True)]}),
        'freight': fields.float('Freight', digits=(16, 2)),
        'packing': fields.float('Packing', digits=(16, 2)),
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
    _defaults = {
            'bills_amoun_total': 0.0 ,
            'freight': 0.0,   
            'packing':  0.0,
            'purchase_type':'internal',

                 }

    def wkf_sign_order(self, cr, uid, ids, context=None):
        """
        Workflow function override to create voucher with the 
        extra cost prices.

        @return: True
        """
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for po in self.browse(cr, uid, ids, context=context):
            if not po.location_id:
                raise osv.except_osv(_('NO Stock Location !'), _('Please chose stock location then make Confirmation.'))
        self.write(cr, uid, ids, {'state': 'sign', })
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        purchase_obj = self.pool.get('purchase.order').browse(cr,uid,ids)
        if not company_obj :
            company_obj = purchase_obj.company_id
        list=[]
        for purchase in purchase_obj:
            if purchase.purchase_bills :
                for bill in purchase.purchase_bills :
                    journal = bill.type.property_type_journal
                    account = bill.type.property_type_account  
                    voucher_id = voucher_obj.create(cr, uid, {
                                            'amount': bill.bill_amount ,
                                            'type': 'purchase',
                                            'date': time.strftime('%Y-%m-%d'),
                                            'partner_id': bill.partner_id.id, 
                                            'journal_id': journal.id,
                                            'reference': purchase.name,
                                            'reference': purchase.name,})
                    list.append(voucher_id)
                    vocher_line_id = voucher_line_obj.create(cr, uid, {
                                        'amount': bill.bill_amount,
                                        'voucher_id': voucher_id,
                                        'account_id': account.id,
                                        'type': 'dr',
                                        'name': bill.description,
                                         })
                self.write(cr, uid, ids,{'account_voucher_ids':[(6,0,list)]})
            purchase._calculate_bills_amount()        
        self.write(cr, uid, ids, {'state': 'sign', })
        return True
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        """
        Workflow function override to force calculate the extra price amount.

        @return: super wkf_confirm_order method
        """
        #for purchases in self.browse(cr, uid, ids):
            #purchases._calculate_bills_amount()
            #for line in purchases.order_line:
                #line._calculate_extra_amount(purchases)
        return super(purchase, self).wkf_confirm_order(cr, uid, ids, context) 

 
    def create_supplier_invoive(self, cr, uid, ids, context=None):

        """
        Function For create Invoice From Button add check whether it created before.

        @return: True
        """ 
        order_obj = self.browse(cr, uid, ids)[0]
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line') 
        invoice_record = invoice_obj.search(cr,uid,[('origin' , '=' , order_obj.name )])
        if invoice_record :
           raise osv.except_osv(_('Duplicated Invoices !'), _('You are Already Create Invoice for this order before.'))
        invoice_id = super(purchase, self).action_invoice_create(cr, uid, ids, context)
        self.write(cr,uid,ids,{'invoice_method' : 'manual'})
        return True


    def action_invoice_create(self, cr, uid, ids, context=None):
        """
        Override to add invoice lines to manage freight and packing prices.

        @return: invoice id
        """  
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')             
        invoice_id = super(purchase, self).action_invoice_create(cr, uid, ids, context)
        for order in self.browse(cr, uid, ids):
            company_obj = order.company_id
            invoice_obj.write(cr, uid, invoice_id, {'currency_id':order.currency_id.id})           
            line_id = invoice_line_obj.search(cr, uid,[('invoice_id','=',invoice_id)],limit=1)
            account_id = invoice_line_obj.browse(cr,uid,line_id)[0].account_id.id
            if order.freight > 0.0:
                invoice_line_id = invoice_line_obj.create(cr, uid,
                   {
                        'name': 'Freight',
                        'origin': order.name,
                        'invoice_id': invoice_id,
                        'uos_id': 0,
                        'product_id': 0,
                        'account_id': account_id,
                        'price_unit': order.freight,
                        'discount': 0,
                        'quantity': 1,
                        'invoice_line_tax_id':0,
                        'account_analytic_id': 0,
                    })
            if order.packing > 0.0 :
                invoice_line_id = invoice_line_obj.create(cr, uid,
                   {
                        'name': 'Packing',
                        'origin': order.name,
                        'invoice_id': invoice_id,
                        'uos_id': 0,
                        'product_id': 0,
                        'account_id': account_id,
                        'price_unit': order.packing,
                        'discount': 0,
                        'quantity': 1,
                        'invoice_line_tax_id':0,
                        'account_analytic_id': 0,
                    })
            if order.purchase_type == 'foreign':
                account_from_company = company_obj.purchase_foreign_account
                journal_id = company_obj.purchase_foreign_journal
                if not account_from_company:
                    raise osv.except_osv(_('NO Account !'), _('no account defined for purchase foreign.'))
                if not journal_id:
                    raise osv.except_osv(_('NO Journal !'), _('no journal defined for purchase foreign.'))
                invoice = invoice_obj.browse(cr,uid,invoice_id)
                invoice_obj.write(cr, uid, invoice_id,{'journal_id':journal_id.id})
                for line in invoice.invoice_line:
                    invoice_line_obj.write(cr, uid, line.id ,{'account_id':account_from_company.id})
        #print"invoice_id %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",invoice_id
        return invoice_id
    
    def action_picking_create(self,cr, uid, ids, *args):
        """
        Override to read account of purchase foreign from the company,
        and add foreign purchase price to picking.

        @return: picking id
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        picking_id = super(purchase,self).action_picking_create(cr, uid, ids, *args)
        move_obj = self.pool.get('stock.move')
        currency_obj = self.pool.get('res.currency')
        for purchase_obj in self.browse(cr, uid, ids):
            company_obj = purchase_obj.company_id
            if purchase_obj.purchase_type == 'foreign':
                account_from_company = company_obj.purchase_foreign_account
                if not account_from_company:
                    raise osv.except_osv(_('NO Account !'), _('no account defined for purchase foreign.'))
                else:
                    res = { 
                        'account_id': account_from_company.id or False,
                        'company_id':company_obj.id,
                    }
            picking_obj.write(cr,uid,picking_id,res)
            move = {}
            total_amount = 0.0
            for order_line in purchase_obj.order_line:
                stock_move_obj = move_obj.search(cr, uid, [('purchase_line_id', '=',order_line.id)])
                total_amount = order_line.price_unit_freight + order_line.price_unit_packing + order_line.price_unit
                new_price = currency_obj.compute(cr, uid, order_line.order_id.currency_id.id, order_line.order_id.company_id.currency_id.id, total_amount,purchase_obj.date_order)
                price = new_price
                if purchase_obj.purchase_type == 'internal': 
                    price = order_line.price_unit + order_line.price_unit_freight + order_line.price_unit_packing + order_line.price_unit_tax
                move = {                                
                                'price_unit': price,
                        }
                move_obj.write(cr,uid,stock_move_obj,move) 
        return picking_id


class purchase_order_lines(osv.osv):
    """
    To Manage foreign purchase line"""
    _inherit = 'purchase.order.line'
    
    def _calculate_extra_amount(self, cr, uid, ids, purchase, context=None):
        """
        To calculate extra cost total amount.

        @return: True
        """
        total_qty =  0.0
        amount_all = purchase.bills_amoun_total
        for item in purchase.order_line:
            total_qty += item.product_qty
        for item in purchase.order_line:
            item_price = amount_all/item.product_qty
            total = item.extra_price_total + item_price
            self.write(cr, uid, item.id, {'extra_cost':item_price , 'extra_price_total':total})
        return True
    
    _columns = {
                 'extra_cost': fields.float('Extra price',digits=(16,2) ),
                 'extra_price_total': fields.float('Extra Price Total ', digits=(16,2)),  
                 'price_unit_freight': fields.float('Freight',digits=(16,4)),
                 'price_unit_packing': fields.float('Packing',digits=(16, 2)),
                } 
    _defaults = {
                 'extra_cost': 0.0,
                 'extra_price_total': 0.0,
                 'price_unit_freight': 0.0,
                 'price_unit_packing': 0.0,

                } 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
