# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import netsvc
import time
import datetime
from tools.translate import _


class pur_quote(osv.osv):
    """
    Purchase Quote module for managing initial purchase quotation"""

    _name = "pur.quote"
    _description = 'Custom Purchase Quote'
    
    def create(self, cr, user, vals, context=None):
        """ 
        Override to editing the name field by a new sequence.

        @return super create() method 
        """
        if vals.get('name', False) in ['/', False]:
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'pur.quote')
        return super(pur_quote, self).create(cr, user, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """ 
        Ovrride to add constrain on deleting the quotaions. 

        @return: super unlink() method
        """
        if context is None:
            context = {}
        if [quote for quote in self.browse(cr, uid, ids, context=context) if quote.state not in ['draft']]:
            raise osv.except_osv(_('Invalid action !'), _('You cannot remove qutation not in draft state !'))
        return super(pur_quote, self).unlink(cr, uid, ids, context=context)
    
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
        return True
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        """
        To compute the amount of lines either with taxes or without taxes. 

        @param field_name :  'amount_untaxed', 'amount_tax', 'amount_total' fields
        @return: dictionary of value of fields amount_untaxed, 
                                               amount_tax, 
                                               amount_total       
        """
        
        res = {}
        for quote in self.browse(cr, uid, ids, context=context):
                res[quote.id] = {
                    'amount_untaxed': 0.0, 
                    'amount_tax': 0.0, 
                    'amount_total': 0.0, 
                }
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
                'name': fields.char('ID', size=256, required=True, readonly=True), 
                'delivery_period': fields.integer('Delivery period',), 
                'delv_plan': fields.char('Delivery Plan', size=256), 
                'pq_date': fields.date('Quote Date', states={'confirmed':[('readonly', True)], 'cancel':[('readonly', True)], 'done':[('readonly', True)]},), 
                'pq_ir_ref': fields.many2one('ireq.m', 'REF', states={'confirmed':[('readonly', True)], 'cancel':[('readonly', True)], 'wait_budget':[('readonly', True)], 'done':[('readonly', True)]}, readonly=True), 
                'q_no':fields.integer('Quote No.', help="No. of Quotation of supplier", states={'confirmed':[('readonly', True)], 'cancel':[('readonly', True)], 'wait_budget':[('readonly', True)], 'done':[('readonly', True)]},), 
                'supplier_id':fields.many2one('res.partner', 'Supplier', states={'confirmed':[('readonly', True)], 'cancel':[('readonly', True)], 'wait_budget':[('readonly', True)], 'done':[('readonly', True)]}, change_default=True), 
                'vat_supp': fields.boolean('VAT Legal Statement',), 
                'pq_pro_ids':fields.one2many('pq.products', 'pr_pq_id' , 'Items', states={'confirmed':[('readonly', True)], 'cancel':[('readonly', True)], 'wait_budget':[('readonly', True)], 'done':[('readonly', True)]},), 
                'taxes_id': fields.many2many('account.tax', 'purchase_quote_taxe', 'q_id', 'tax_id', 'Taxes', states={'confirmed':[('readonly', True)], 'cancel':[('readonly', True)], 'wait_budget':[('readonly', True)], 'done':[('readonly', True)]},), 
                'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Approved to be Purchased'), ('cancel', 'Cancelled')], 'State', readonly=True, select=True), 
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
    _defaults = {
                'name': lambda self, cr, uid, context: '/', 
                'state': lambda *a: 'draft', 
                'vat_supp':0, 
                }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Purchase Quote Reference must be unique !'), 
        ('name_uniq', 'unique(pq_ir_ref,supplier_id)', 'supplier is must be unique !'),
        ]

    def _check_negative_price(self, cr, uid, ids, context=None): 
        """ 
        Constrain function to prevent the price from being negitive or 0.

        @return: True or False 
        """
        for quote in self.browse(cr, uid, ids, context=context):
            for line in quote.pq_pro_ids:
                if line.price_unit < 0:
                    return False
        return True

    _constraints = [
        (_check_negative_price, 'Negative price ! \n kindly change the price field to positive value .',['amount_total']),
    ]
    
    def on_change_supplier(self, cr, uid, ids, supplier, context={}):
        """ 
        To checks if this supplier already selected by an other qoutation 
	    if so it raise an exception else continue.

	    @param quote_ids: the ids of all created code.
	    @return: Dictonary of supplier and supplier's vats 
        """
        res = {}
        quote_obj = self.pool.get('pur.quote')
        for quote in self.browse(cr, uid, ids):
            quote_ids = quote_obj.search(cr, uid, [('pq_ir_ref', '=', quote.pq_ir_ref.id)])
            #Check if this supplier already selected by an other quote
            if[created_quote for created_quote in quote_ids if created_quote != quote.id and quote_obj.browse(cr, uid, created_quote).supplier_id.id == supplier]: 
                res = {'value': { 'supplier_id':'', }}
                raise osv.except_osv(_('Dupplicated Supplier !'), _('This Supplier is already chosed for another Quote \n Please .. Chose another supplier ..'))
            else:
                vat = self.pool.get('res.partner').browse(cr, uid, supplier).vat_subjected
                res = {'value': { 'vat_supp':vat, }}
        return res    

    def copy(self, cr, uid, id, default={}, context={}):
        """
        Override copy function to edit defult value.

        @param default: default vals dict
        @return: super copy() method   
        """
        default.update({
            'state':'draft', 
            'name': self.pool.get('ir.sequence').get(cr, uid, 'pur.quote'), 
        })
        return super(pur_quote, self).copy(cr, uid, id, default, context)
        
    #Workflow functions
    def confirmed(self, cr, uid, ids):
        """ 
        Workflow function to check fields and change the state to confirm.

        @return: no return value
        """
        for quote in self.browse(cr, uid, ids):
            if not quote.q_no: #Check if there is a number 
                raise osv.except_osv(_('No Quotation Number !'), _('Please .. Fill quotation Number and Date then make Confirmation ..')) 
            if quote.supplier_id.id: #Check if there is a supplier then continue            
                if quote.vat_supp and (not quote.taxes_id) :
                    raise osv.except_osv(_('No Taxes !'), _('Please .. Fill Taxes then make Confirmation ..'))
            
            if[product for product in quote.pq_pro_ids if product.price_unit and (quote.amount_total != 0.0)]:
                self.write(cr, uid, ids, {'state':'confirmed'})
            else:
                raise osv.except_osv(_(' Zero Prices  !'), _('Please ..  make sure you enter prices for products and compute then make Confirmation ..'))
  
                
    def cancel(self, cr, uid, ids,context=None):
        """ 
        Workflow function changes order state to Cancel.

        @return: True
        """
        self.write(cr, uid, ids, {'state':'cancel'})
        
#     def action_cancel_draft(self, cr, uid, ids, context=None): 
#         """ 
#         Changes order state to Draft.
#  
#         @return: True
#         """
#         for quote in self.browse(cr,uid,ids):
#             rec_state = quote.pq_ir_ref.state
#         if rec_state == "confirmed" :
#             if not len(ids):
#                 return False
#             self.write(cr, uid, ids, {'state':'draft'}, context=context)
#             wf_service = netsvc.LocalService("workflow")
#             for s_id in ids:
#                 # Deleting the existing instance of workflow for PO
#                 wf_service.trg_delete(uid, 'pur.quote', s_id, cr)            
#                 wf_service.trg_create(uid, 'pur.quote', s_id, cr)
#         else :
#              raise osv.except_osv(_("Error"), _("You Can't Reset Quote After Approved The Winner Quote"))
#         return True

    def done(self, cr, uid, ids, n='',context=None):  
        """ 
        Workflow function changes quotation state to done, cancel all other quotations of the requisition
        and change the requisition state to wait_confirmed.

        @return: True
        """
        group_obj = self.pool.get('res.groups')
        users_obj = self.pool.get('res.users')
        internal_obj = self.pool.get('ireq.m')
        internal_products = self.pool.get('ireq.products')
        quote_obj = self.pool.get('pur.quote')
        group = group_obj.search(cr, uid, [('name', '=', 'Purchase / Commitee Member')]) 
        users = users_obj.search(cr, uid, [('groups_id', '=', group)])         
         
        for quote in self.browse(cr, uid, ids):
            self.write(cr, uid, ids, {'state':'done'})
            # For updating the internal requestion products prices
            for product in quote.pq_pro_ids:
                if product.req_product:
                    internal_products_ids = product.req_product.id
                else: 
                    internal_products_ids = internal_products.search(cr, uid, [('pr_rq_id', '=', quote.pq_ir_ref.id), ('product_id', '=', product.product_id.id)])
                internal_products_ids = internal_products.search(cr, uid, [('pr_rq_id', '=', quote.pq_ir_ref.id), ('product_id', '=', product.product_id.id)])
                internal_products.write(cr, uid, internal_products_ids, {'price_unit': product.price_unit })
            # For cancel all other quotes except this one                 
            quote_ids = quote_obj.search(cr, uid, [('pq_ir_ref', '=', quote.pq_ir_ref.id)])
            for created_quote in quote_ids:
                current_quote = quote_obj.browse(cr, uid, created_quote)
                if current_quote.id != quote.id:
                    quote_obj.write(cr, uid, created_quote, {'state':'cancel'})
            # Put All information in note field
            names = ''
            notes = internal_obj.browse(cr, uid, quote.pq_ir_ref.id).notes or ''
            chose = internal_obj.browse(cr, uid, quote.pq_ir_ref.id).chose
            for user in users:
                names = names + '\n' + self.pool.get('res.users').browse(cr, uid, user).name
            if chose==0 :
                notes = notes + '\n \nCommitee Members:\n' + names
                internal_obj.write(cr, uid, quote.pq_ir_ref.id, {'chose':1, })
            internal_obj.write(cr, uid, quote.pq_ir_ref.id, {'state':'wait_confirmed'})
        return True


    def make_purchase_order(self, cr, uid, ids, context=None): 
        """
        Workflow function of purchase requisition creates purchase order from the approved quote
        and changes the status of purchase requisition to done.

        @return creates purchase order  
        """
        purchase_ids = []
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        quote_obj = self.pool.get('pur.quote')
        partner_obj = self.pool.get('res.partner') 
        product_obj = self.pool.get('product.product')       
        for purchase_quote in self.browse(cr, uid, ids): 
                if purchase_quote:
                    if purchase_quote.state == 'done':
                        part_addr = partner_obj.address_get(cr, uid, [purchase_quote.supplier_id.id], ['default'])
                        dif = datetime.timedelta(days=purchase_quote.delivery_period)
                        current_date = datetime.date.today()
                        edate = current_date + dif
                        or_id = purchase_obj.create(cr, uid, {
                            'partner_id':purchase_quote.supplier_id.id, 
                            'partner_address_id':part_addr['default'], 
                            'pricelist_id':purchase_quote.supplier_id.property_product_pricelist_purchase.id, 
                            'state':'draft', 
                            'origin':purchase_quote.pq_ir_ref.name+'-'+purchase_quote.name, 
                            'pq_id':purchase_quote.id, 
                            'purpose':purchase_quote.pq_ir_ref.purpose, 
			                'cat_id':purchase_quote.pq_ir_ref.cat_id.id, 
                            'ir_id':purchase_quote.pq_ir_ref.id, 
                            'ir_date':purchase_quote.pq_ir_ref.ir_date, 
                            'department_id':purchase_quote.pq_ir_ref.department_id.id, 
                            'taxes_id': [(6, 0, [x.id for x in purchase_quote.taxes_id])], 
                            'delivery_period': purchase_quote.delivery_period , 
                            'delv_plan':purchase_quote.delv_plan , 
                            'e_date':edate, 
                            'company_id':purchase_quote.pq_ir_ref.company_id.id,
                            'currency_id': purchase_quote.currency_id and purchase_quote.currency_id.id or False,
                            'pricelist_id':purchase_quote.pricelist_id and purchase_quote.pricelist_id.id or False,
		                            })

                        purchase_ids.append(or_id)
                        for product in purchase_quote.pq_pro_ids:
                            p_uom = product_obj.browse(cr, uid, product.product_id.id).uom_po_id.id
                            purchase_line_obj.create(cr, uid, {
                                 'name': product.product_id.name, 
                                 'product_id': product.product_id.id, 
                                 'product_qty': product.product_qty, 
                                 'date_planned':time.strftime('%Y-%m-%d'), 
                                 'product_uom':p_uom, 
                                 'price_unit':product.price_unit, 
                                 'order_id':or_id, 
                                 'price_unit_tax':product.price_unit_tax, 
                                 'price_unit_total':product.price_unit_total, 
                                 'quote_product': product.id,
                                 'notes': product.desc, 
                                 })

                    else:
                        # This part of code for future use, if all quotes in done state the code creates purchase orders
                        # and this part of code delete all purchase orders except one
                        quote_name = quote.pq_ir_ref.name
                        name = quote_name+'-'+quote.name
                        pos = purchase_obj.search(cr, uid, [('origin', '=', name)])
                        purchase_obj.unlink(cr, uid, pos)
                        quote.write({'state':'cancel'}, context=context)
                        
                
        return purchase_ids


#
# Model definition
#

class pq_products(osv.osv):
    """
    Manage the products of purchase inintail quotaion"""

    _name = "pq.products"
    _description = 'Custom Purchase Quote Product'

    
    def _amount_line(self, cr, uid, ids,  fields, arg ,context):
        """
        Compute the price amount of each quotaion line.

        @return:  dictionary of lines subtotal
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
        res = {}
        if price or qty:
            res = {'value': {'price_subtotal': price * qty, }}
        return res
    
    _columns = {
                'name': fields.char('Name', size=64, required=True, readonly=True , select=True), 
                'product_id': fields.many2one('product.product', 'Items', readonly=True , change_default=True), 
                'product_qty': fields.float('Quantity', required=True, readonly=True, digits=(16, 2)), 
                'price_unit': fields.float('Unit Price'), 
                'price_unit_tax': fields.float('Tax Unit Price',digits=(16, 4)), 
                'price_unit_total': fields.float('Total Unit Price',digits=(16, 4)), 
                'pr_pq_id': fields.many2one('pur.quote', 'Quote Ref', select=True), 
                'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', 
                                  store = { 'pq.products': (lambda self,cr,uid,ids,ctx={}: ids, ['price_unit','product_qty'], 10),}), 
                'req_product': fields.many2one('ireq.products', 'requisition product', ondelete='restrict', readonly=True),
                'desc': fields.text('Specification'), 
               }
    _defaults = {
                'product_qty': lambda *a: 1.0, 
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
