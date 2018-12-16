# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
import netsvc
from tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar


class letter_of_credit_bank(osv.osv):
    """
    To manage letter of credit bank information """

    _name = "letter.of.credit.bank"
    _description = 'Letter Of Credit Bank'
    _columns = {
            'name': fields.char('name', size=128, required=True),
            'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide important types."), 
            'bank_account_number': fields.integer('Account Number', required=True),
            'bank_account_id': fields.many2one('account.account', 'Bank Account', required=True),
       
    }


class purchase_letter_of_credit(osv.osv):
    """
    To Manage letter of credit """

    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence 
        and recalculate the amount_in_word value. 

        @return: new object id 
        """
        created_id = super(purchase_letter_of_credit, self).create(cr, user, vals)
        amount = vals.get('amount',False)
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'purchase.letter.of.credit')
        company = self.pool.get('res.users').browse(cr, user, user).company_id
        currency_format =  company.currency_format 
        amount_in_word = ''
        if currency_format=='ar':
            currency = self.pool.get('res.currency').read(cr, user, company.currency_id.id, ['units_name','cents_name'], context=context)
            amount_in_word = amount_to_text_ar(amount, currency_format, currency['units_name'], currency['cents_name'])
        else: 
            amount_in_word = amount_to_text(amount)
        vals.update({'amount':amount,'amount_in_word': amount_in_word})
        self.write(cr, user, created_id, vals, context)
        return created_id
    
    def write(self, cr, uid, ids,vals, context=None):
        """
        Override to force amount in word update

        @return: True
        """
        super(purchase_letter_of_credit, self).write(cr, uid, ids, vals, context)
        amount = vals.get('amount',False)
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        currency_format =  company.currency_format 
        amount_in_word = ''
        if currency_format=='ar':
            currency = self.pool.get('res.currency').read(cr, uid, company.currency_id.id, ['units_name','cents_name'], context=context)
            amount_in_word = amount_to_text_ar(amount, currency_format, currency['units_name'], currency['cents_name'])
        else: 
            amount_in_word = amount_to_text(amount)
        vals.update({'amount':amount,'amount_in_word': amount_in_word})   
        return True

    
    _name = 'purchase.letter.of.credit'
    _description = "Purchase Letter Of Credit"
    
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('bank', 'Banked'),
	('confirm','Confirmed'),
	('receive','Received'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]
    
    _columns = {
                'name': fields.char('LC Number', size=64, readonly=1, select=True, 
                    help="unique number of the LC, computed automatically when the LCt is created"),
                'lc_date': fields.date('LC Date', readonly=1, select=True, help="Date on which LC is created"),
                'purchase_order_ref': fields.many2one('purchase.order', 'Purchase order'),
                'amount': fields.float('Total Amount', required=True),
                'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
                'picking_policy': fields.selection([('partial', 'Partial Delivery'), ('complete', 'Complete Delivery')],
                    'Picking Policy', help="""deliver all at once as (complete), or partial shipments"""),
                'delivery_date': fields.date('Delivery Date', select=True, help="Date on which delivery will be done"), 
                'partner_id': fields.many2one('res.partner', 'Supplier', required=True, select=True),
                'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', help="Pricelist for current supplier"),
                'incoterm': fields.many2one('stock.incoterms', 'Incoterm', help="Incoterm which stands for 'International Commercial terms' implies its a series of terms which are used in the commercial transaction."),
                'items_types': fields.selection([('products', 'Products'),('service', 'Service'),('both', 'products and service'),
                ], 'Items types', help="the type of the contracts items"),
                'reference': fields.char('LC Reference', size=64, readonly=1, select=True),
                'source_number': fields.char('Created From', size=64,  readonly=1),
                'source_date':fields.date('Source Date', select=True, readonly=1),
                'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
                'user':  fields.many2one('res.users', 'Responsible',readonly=True,),
                'amount_in_word': fields.char('Written Total', size=250, readonly=1),
                'notes': fields.text('Notes'),
        	    'letter_of_credit_line_ids':fields.one2many('purchase.letter.of.credit.line', 'letter_of_credit_id' , 'Products'),
                'bank': fields.many2one('letter.of.credit.bank', 'LC Bank'),
                'currency_id': fields.many2one('res.currency','Currency',select=1),
                'account_voucher_ids': fields.many2many('account.voucher', 'purchase_letter_of_credit_voucher', 'letter_of_credit_id', 'voucher_id', 'Account voucher'),

                }
    _defaults = {
                 'name':'/',
                 'lc_date' : lambda *a: time.strftime('%Y-%m-%d'),
                 'amount': 0.0,
		 'state':'draft'		
                 }

    def onchange_amount(self, cr, uid, ids, amount, context={}):
        """
        On change function of amount to update amount in word.
     
        @return: Dictionary of amount and amount in word
        """
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        currency_format =  company.currency_format 
        amount_in_word = ''
        if currency_format=='ar':
            currency = self.pool.get('res.currency').read(cr, uid, company.currency_id.id, ['units_name','cents_name'], context=context)
            amount_in_word = amount_to_text_ar(amount, currency_format, currency['units_name'], currency['cents_name'])
        else: 
            amount_in_word = amount_to_text(amount)
        return {'value': {'amount':amount,'amount_in_word': amount_in_word}}
 

    def bank(self, cr, uid, ids, context=None):
        """
        Workflow function to change state to bank
 
        @return: True      
        """
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')        
        for lc in self.browse(cr, uid, ids):
            if not lc.letter_of_credit_line_ids:
                raise osv.except_osv(('No Products  !'),('Please fill the products list first ..'))                
        self.write(cr, uid, ids, {'state':'bank'})
        return True

    def confirm(self,cr,uid,ids,context=None):
        """
        Workflow function to change state to confirm and
        create account voucher.
 
        @return: True      
        """
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')        
        for lc in self.browse(cr, uid, ids):
            vouchers=[]
            if not lc.letter_of_credit_line_ids:
                raise osv.except_osv(('No Products  !'),('Please fill the products list first ..'))
            else:
                company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
                journal = company_obj.letter_of_credit_jorunal
                account = company_obj.letter_of_credit_account
                if not journal:
                    raise osv.except_osv(_('wrong action!'), _('No Letter Of Credit journal defined for your company!  please add the journal first ..'))
                voucher_id = voucher_obj.create(cr, uid, {
                                    'amount': lc.amount ,
                                    'type': 'purchase',
                                    'date': time.strftime('%Y-%m-%d'),
                                    'partner_id': lc.partner_id.id , 
                                    'journal_id': journal.id,
                                    'reference': lc.name,
                                    'name': 'Letter Of Credit'+lc.name,
                                    'state': 'draft',})
                vocher_line_id = voucher_line_obj.create(cr, uid, {
                                        'amount': lc.amount,
                                        'voucher_id': voucher_id,
                                        'account_id': account.id,
                                        'name': lc.notes,
                                         })  

                vouchers.append(voucher_id)             
            self.write(cr, uid, lc.id, {'state':'confirm','account_voucher_ids':[(6,0,vouchers)]})
        return True

    def receive(self,cr,uid,ids,context=None):
        """
        Workflow function to change the state to receive.

        @return: no return value 
        """
        #Todo: Add account move in this state 
        self.write(cr, uid, ids, {'state':'receive'}, context=context)

    def done(self,cr,uid,ids,context=None):
        """
        Workflow function to change the state to done.

        @return: no return value 
        """
        #Todo: Add account move in this state 
        self.write(cr, uid, ids, {'state':'done'}, context=context)

    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes order state to cancell and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Letter OF Credit Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes order state to Draft and reset the workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
		    self.write(cr, uid, s_id, {'state':'draft'})
		    wf_service.trg_delete(uid, 'purchase.letter.of.credit', s_id, cr)            
		    wf_service.trg_create(uid, 'purchase.letter.of.credit', s_id, cr)
        return True


class purchase_letter_of_credit_line(osv.osv):
    """
    To manage letter of credit lines """

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        """
        Functional field function compute the total price amount of line

        @return: dictionary of lines amount value
        """       
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.price_unit * line.product_qty
        return res
    
    def subtotal(self, cr, uid, ids, price, qty):
        """
        On change function to recompute the total price after changing product qty or product unit

        @return: dictionary of price_subtotal
        """
        if price or qty:
            res = {}
            res = {'value': {'price_subtotal': price * qty, }}
        return res   


    _name = 'purchase.letter.of.credit.line'
    _description = "Purchase Letter Of Credit line"
    _columns = {
        'name': fields.char('Description', size=256, required=True),
        'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'price_unit': fields.float('Unit Price', required=True),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits=(16,2), store=True),
        'letter_of_credit_id': fields.many2one('purchase.letter.of.credit', 'Letter of credit',),
        'tax_id': fields.many2many('account.tax', 'letter_of_credit_tax', 'purchase_letter_of_credit_line_id', 'tax_id', 'Taxes'),
        'product_packaging': fields.many2one('product.packaging', 'Packaging', help="Control the packages of the products"),
        'notes': fields.text('Notes'),        
        }
    _sql_constraints = [
       # ('produc_uniq', 'unique(letter_of_credit_id,product_id)', 'Sorry You Entered Product Two Time You are not Allow to do this.... So We going to delete The Duplicts!'),
            ] 

    def product_id_change(self, cr, uid, ids,product):
        """
        On change product function to read the default name and UOM of product

        @param product: product_id 
        @return: dictionary of product name and uom or empty dictionary 
        """
        if product:
            prod= self.pool.get('product.product').browse(cr, uid,product)
            return {'value': { 'name':prod.name,'product_uom':prod.uom_po_id.id}}
        return {}
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
