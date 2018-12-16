# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import netsvc
import time
from tools.translate import _
from osv import osv, fields
import decimal_precision as dp


class transportation_order(osv.osv):
    """
    To manage the transportation basic concepts and  operations"""
    
    def create(self, cr, user, vals, context=None):
        """
		This method override the create method to get sequence and update
		field name by sequence value.

	    @param vals: list of record to be process
		@return: new created record ID
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'transportation.order')
        new_id = super(transportation_order, self).create(cr, user, vals, context)
        return new_id
        
    TYPE = [
        ('purchase', 'Purchase transportation'),
    ]
    STATE_SELECTION = [
        ('draft', 'Draft'),
	    ('confirmed', 'Confirmed'),
	    ('invoice','Invoice'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ]
    
    DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
        ('land_freight', 'Land Freight'),
    ]
        
    _name = 'transportation.order'
    _description = "Transportation order"
    _columns = {
        'name': fields.char('Reference', size=64, required=True, readonly=1, select=True, 
            help="unique number of the transportations, computed automatically when the transportations order is created"),
        'purchase_order_id' : fields.many2one('purchase.order', 'Purchase order',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'department_id':fields.many2one('hr.department', 'Department',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'source_location': fields.char('Source location', size=64,select=True,states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'destination_location': fields.char('Destination location', size=64,select=True,states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'transportation_date':fields.date('Transportation Date', required=True, select=True,states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],},
            help="Date on which this document has been created."),
        'transportation_type': fields.selection(TYPE, 'Transportation type', select=True,states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'description': fields.text('Transportation description' ,states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),        
        'delivery_method': fields.selection(DELIVERY_SELECTION, 'Method of dispatch', select=True ,states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],} ),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', help="Pricelist for current supplier",states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'transportation_line_ids':fields.one2many('transportation.order.line', 'transportation_id' , 'Products',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'transportation_drivers':fields.one2many('transportation.driver', 'transportation_id' , 'Drivers',states={'done':[('readonly',True)]}),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, help="The state of the transportation.", select=True),
        'notes': fields.text('Notes',states={'done':[('readonly',True)]}),
 	    'user':  fields.many2one('res.users', 'Responsible',readonly=True,states={'done':[('readonly',True)]}),
        'account_vouchers': fields.many2many('account.voucher', 'transportation_voucher', 'transportation_id', 'voucher_id', 'Account voucher',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}), 
        'allocation_base':fields.selection([('weight','WEIGHT'),('quantity','QUANTITY'),('space','Space (volume)'),('price','PRICE'),],'Allocation Base',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'quotes_ids':fields.one2many('transportation.quotes', 'transportation_id' ,'Quotes',states={'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'supplier_chose_reason_delivery':fields.boolean('Good delivery',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'supplier_chose_reason_quality':fields.boolean('High quality',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'supplier_chose_reason_price':fields.boolean('Good price',states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'supplier_chose_reason_others': fields.char('Other Reasons', size=256 ,states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],} ),
        'partner_id':fields.many2one('res.partner', 'Transporter', states={'done':[('readonly',True)],'invoice':[('readonly',True)],}),
        'purpose': fields.selection([('purchase','Purchase'),('stock','Stock'),('other','Other')],'Purpose', required=True ,select=True, states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'invoice':[('readonly',True)],}),

                } 
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'transportation_date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'user': lambda self, cr, uid, context: uid,
        'transportation_type':'purchase',
        'allocation_base': 'price',

        }
    
    def copy(self, cr, uid, id, default={}, context=None):
        """
        Override copy function to edit defult value.

        @param default: default vals dict
        @return: super copy method  
        """
        seq_obj = self.pool.get('ir.sequence')
        default.update({
            'state':'draft',
            'name': seq_obj.get(cr, uid, 'transportation.order'),
            'transportation_date':time.strftime('%Y-%m-%d'),
            'transportation_line_ids':[],
        })
        return super(transportation_order, self).copy(cr, uid, id, default, context)

    def get_products(self,  cr, uid, ids, purchase_id, context={}): 
        """
        To read purchase order lines when select a purchase order.

        @param purchase_id : purchase order id
        @return: True 
        """
        purchase_obj = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
        transportation_product_odj=self.pool.get('transportation.order.line')
        transportation = self.pool.get('transportation.order').browse(cr, uid, ids)
        if transportation[0].transportation_line_ids != []:
            raise osv.except_osv(_('this Transportation is already contain products !'), _('to chose a Purchase Order delete all the products first ..'))            
        for product in purchase_obj.order_line:
            transportation_product_odj.create(cr,uid,{
                  'name': purchase_obj.name + ': ' +(product.name or ''),
                  'product_id': product.product_id.id,
                  'price_unit': product.price_unit,
                  'product_qty': product.product_qty, 
                  'product_uom': product.product_uom.id,
                  'transportation_id': ids[0],
                  'description': 'purchase order '+ purchase_obj.name , 
                  'purchase_line_id': product.id,
                  'price_unit': product.price_unit,         
                  'code_calling':True,                                     })
        self.write(cr,uid,ids,{'description':purchase_obj.name})
        return True

    def load_items(self, cr, uid, ids,purchase_id, context=None):
        """ 
        To load purchase order lines of the selected purchase order to transportaion lines.

        @param purchase_id: purchase order id 
        @return: True  
        """
        for order in self.browse(cr, uid, ids):
            if order.purchase_order_id:
               self.get_products(cr, uid, ids,order.purchase_order_id.id, context=context)
        return True
           

    def confirmed(self,cr,uid,ids,*args):
        """
        Workflow function to change state of Purchase transportation to confirmed. 

        @return: True
        """

        for order in self.browse(cr, uid, ids):
            if order.purchase_order_id:
                if not order.transportation_line_ids:
                    raise osv.except_osv(_('Load purchase items first!'), _('Please Load purchase items Purchase Order ..')) 
            if order.transportation_line_ids:
                self.write(cr, uid, ids, {'state':'confirmed'})
            else:
                raise osv.except_osv(_('No Products  !'), _('Please fill the products list first ..'))
        return True




    def invoice(self, cr, uid, ids, context={}):
        """
        function to change state of Purchase transportation to invoice, 
        check driver information and calculate transportaion price of purche 
        line by allocate_purchase_order_line_price() and write the price to 
        purhase order. 

        @return: True
        """  
        purchase_ids = []
        for transportation in self.browse(cr, uid, ids):
            if not  transportation.quotes_ids:  
               raise osv.except_osv(_('wrong action!'), _('Sorry no quotes to be invoiced'))
            if not transportation.transportation_drivers :
                raise osv.except_osv(_('No Driver !'), _('Please add the Drivers first ..'))
            amount = 0.0 
            for quote in transportation.quotes_ids:
                if quote.state in ['done']:
                    quote_obj = quote
                #else : raise osv.except_osv(_('wrong action!'), _('Please approve your quotes first'))
            purchase_ids.append(transportation.purchase_order_id.id)
            transportation._calculate_transportation_amount(quote_obj.amount_total,quote_obj)
        self.write(cr, uid, ids, {'state':'invoice'},context=context)
        if  False not in purchase_ids:
            self.allocate_purchase_order_line_price(cr,uid,ids,purchase_ids)
        return True

 
    def done(self, cr, uid, ids, context=None):
        """
        Workflow function to change state of Purchase transportation to Done 
        and create voucher and voucher lines with transportaion price. 

        @return: True
        """
        self.invoice(cr, uid, ids, context)
        transportation_line_obj = self.pool.get('transportation.order.line')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        journal = company_obj.transportation_jorunal
        account = company_obj.transportation_account
        if not journal:
            raise osv.except_osv(_('wrong action!'), _('no Transportation journal defined for your company!  please add the journal first ..'))
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        transportation_obj = self.pool.get('transportation.order').browse(cr,uid,ids)
        transportation_voucher = []
        purchase_ids = []
        for transportation in transportation_obj:
            amount = 0.0 
            purchase = ''
            if transportation.purpose == 'purchase':
                purchase = transportation.purchase_order_id.name
                if transportation.purchase_order_id.purchase_type == 'foreign':
                    account = company_obj.purchase_foreign_account
                    if transportation.purchase_order_id.contract_id:
                        if not transportation.purchase_order_id.contract_id:
                            raise osv.except_osv(_('Missing Account Number !'),_('There No Account Defined Fore This Contract    please chose the account first') )
                        account = transportation.purchase_order_id.contract_id.contract_account                
            for quote in transportation.quotes_ids:
                if quote.state in ['done']:
                    quote_obj = quote
            if not account:
                raise osv.except_osv(_('wrong action!'), _('no Transportation Account defined!  please add the account first ..'))
            voucher_id = voucher_obj.create(cr, uid, {
                                    'amount': quote_obj.amount_total ,
                                    'type': 'purchase',
                                    'date': time.strftime('%Y-%m-%d'),
                                    'partner_id': quote_obj.supplier_id.id, 
                                    'account_id': quote_obj.supplier_id.property_account_payable.id,
                                    'journal_id': journal.id,
                                    'reference': transportation.name + purchase,})
            vocher_line_id = voucher_line_obj.create(cr, uid, {
                                        'amount': quote_obj.amount_total ,
                                        'voucher_id': voucher_id,
                                        'type': 'dr',
                                        'account_id': account.id,
                                        'name': transportation.description or transportation.name ,
                                         })
            transportation_voucher.append(voucher_id)
            purchase_ids.append(transportation.purchase_order_id.id)

        self.write(cr, uid, ids, {'state':'done','account_vouchers':[(6,0,transportation_voucher)]})
        return True
    
    def allocate_purchase_order_line_price(self, cr, uid,ids,purchase_ids):
        """ 
        Calculate transportaion price for every purchase line and write the price to purchase order lines.

        @param purchase_ids: list of purchase orders ids
	    @return: Ture 
        """
        purchase_line_obj = self.pool.get('purchase.order.line')
        transportation_product_obj = self.pool.get('transportation.order.line')
        for purchase in self.pool.get('purchase.order').browse(cr, uid, purchase_ids):
            for line in purchase.order_line:
                transportation_item = transportation_product_obj.search(cr,uid,[('product_id','=',line.product_id.id),('transportation_id','in',[ids])])
                if transportation_item :
                    transportation_product = transportation_product_obj.browse(cr, uid, transportation_item[0])
                    amount = transportation_product.transportation_price_unit
                    total = line.extra_price_total+amount
                    if line.transportation_price:
                        amount += line.transportation_price
                    purchase_line_obj.write(cr,uid,line.id,{'transportation_price': amount,'extra_price_total':total})
        return True

    def cancel(self,cr,uid,ids,notes=''):
        """ 
        Workflow function to changes clearance state to cancell and writes notes.

	    @param notes : contains information.
        @return: True
        """
        notes = ""
        user = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'purchase Transportation Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ user
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, *args):
        """ 
        To changes clearance state to Draft and reset workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'transportation.order', s_id, cr)            
            wf_service.trg_create(uid, 'transportation.order', s_id, cr)
        return True
    
    def partner_id_change(self, cr, uid, ids,partner):
       """ 
        On change partner function to read partner pricelist.

	    @param partner: partner id.
	    @return: Dictonary of partner's pricelist value 
       """
       partne = self.pool.get('res.partner.address').search(cr, uid, [('partner_id', '=', partner)])
       if partne:
           prod= self.pool.get('res.partner.address').browse(cr, uid,partne[0])
           return {'value': {'pricelist_id':prod.partner_id.property_product_pricelist_purchase.id }}
       
       
    def create_quote(self, cr, uid, ids, context=None):
        """
        Button function to creates qoutation   

        @return: True
        """ 
        for obj in self.browse(cr, uid, ids):
            if obj.transportation_line_ids:         
                pq_id = self.pool.get('transportation.quotes').create(cr, uid, {'transportation_id': obj.id,}, context=context)
                for product in obj.transportation_line_ids:
                    prod_name = ''
                    if product.product_id.id :
                        prod_name = self.pool.get('product.product').browse(cr, uid,product.product_id.id, context=context).name
                    if product.name:
                        prod_name = product.name
                    q_id = self.pool.get('transportation.quotes.products').create(cr, uid, {
                    'name':prod_name,
                    'price_unit': 0.0,
                    'price_unit_tax': 0.0,
                    'price_unit_total': 0.0,
                    'product_id': product.product_id.id or False,
                    'product_qty': product.product_qty,
                    'quote_id':pq_id,
                    'description': product.description,
                    'transportation_line': product.id,
                    })
            else:
                raise osv.except_osv(('No Products !'), ('Please fill the product list first ..'))
        return True
    
    def _calculate_transportation_amount(self, cr, uid, ids, quote_amount,quote):
        """ 
        To calculate transportasiion amount for every clearance line accourding to 
        allocation base the default allocation is price percentage.

        @return: True
        """
        quote_product = self.pool.get('transportation.quotes.products')
        for transportation in self.browse(cr, uid, ids):
            total_qty = total_weight = total_space = 0.0
            # calculate the total amount of qty, wight, space and price
            for item in transportation.transportation_line_ids:
                total_qty += item.product_qty
                if transportation.allocation_base in ['weight']:
                    if item.weight:
                       total_weight += item.weight
                    else: 
                       raise osv.except_osv(_('No Product weight!'), _('Please fill the product weight first ..'))
                if transportation.allocation_base in ['space']:
                    if item.space :
                        total_space += item.space
                    else: 
                        raise osv.except_osv(_('No Product Space (volume) !'), _('Please fill the product Space (volume) first ..'))
                
            for item in transportation.transportation_line_ids:
                # get the line Id to get the price of the item 
                line = quote_product.search(cr, uid,[('quote_id','=',quote.id), ('product_id','=',item.product_id.id),('product_qty','=',item.product_qty)])[0] 
                line_obj = quote_product.browse(cr, uid, line)

                # alocate the price to the item base on the allocation base
                if transportation.allocation_base in ['quantity']: amount = quote_amount*( item.product_qty/ total_qty)
                elif transportation.allocation_base in ['weight']:amount = quote_amount*(item.weight/total_weight)
                elif transportation.allocation_base in ['space']: amount = quote_amount*(item.space / total_space)
                else: amount = line_obj.price_unit
                item.write({'transportation_price_unit':amount})
        return True

    def purchase_ref(self, cr, uid, ids, purchase_ref, context=None):
        #To Clear Products Line From Clearance_Ids
        if purchase_ref:
            if ids == []:
                raise osv.except_osv(_('The Transportation must be saved first!'), _('please save the Transportation before selecting the Purchase Order ..'))  
            else:
                self.get_products(cr, uid, ids,purchase_ref)
            return {}

    def onchange_purpose(self, cr, uid, ids, purpose ,context=None):
        """
        On change purpose function to change delivery Method

        @param purpose: purpose
        @return: Dictionary 
        """
        if purpose and ids:
            unlink_ids = self.pool.get('transportation.order.line').search(cr, uid,[('transportation_id','=',ids[0])] )
            self.pool.get('transportation.order.line').unlink(cr, uid, unlink_ids, context=context)
        land = 'land_freight'
        if purpose != 'purchase' :
           return {'value': { 'delivery_method' : land }}
        return {}



class transportation_order_line(osv.osv):
    """
    To manage transportaion order lines """

    _name = 'transportation.order.line'
    _description = "Transportation order line"
        
    _columns = {
        'name': fields.char('Description', size=256, required=True,readonly=False),
        'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
        'product_uom': fields.many2one('product.uom', 'Product UOM',readonly=False),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'transportation_id': fields.many2one('transportation.order', 'Transportation',),
        'transportation_price_unit': fields.float('Transportation price',readonly=True, digits=(16,2)),
        'product_packaging': fields.many2one('product.packaging', 'Packaging', help="Control the packages of the products"), 
        'description': fields.text('Specification' ,readonly=True),
        'weight': fields.float('Weight',readonly=False, digits=(16, 2)),
        'space': fields.float('Space (volume)',readonly=True, digits=(16, 2)),
        'notes': fields.text('Notes'),
        'purchase_line_id': fields.many2one('purchase.order.line','order_line'),
        'price_unit': fields.float('Purchase Price Unite',readonly=True, digits=(16,2)),
       
        }

    _defaults = {
        'name': lambda self, cr, uid, context: '/',

        }
    _sql_constraints = [
        ('produc_uniq', 'unique(product_id,transportation_id)', 'Sorry You Entered Product Two Time You are not Allow to do this.... So We going to delete The Duplicts!'),
        ('check_product_quantity', 'CHECK ( product_qty > 0 )', "Sorry Product quantity must be greater than Zero."),
            ]

 

    def create(self, cr, uid, vals, context=None):
        purpose = vals and vals['transportation_id'] and self.pool.get('transportation.order').browse(cr, uid,vals['transportation_id']).purpose
        if purpose =='purchase' and ( ('code_calling' not in vals) or not vals['code_calling']):
            raise osv.except_osv(_('Sorry Can not add new items'), _('the purpose is purchase'))
        return super(transportation_order_line, self).create(cr, uid, vals, context)



    def product_id_change(self, cr, uid, ids,product):
        """
        On cange product function to read the default name and UOM of product

        @param product: product_id 
        @return: Dictionary of product name and uom or empty dictionary
        """
        if product:
            prod= self.pool.get('product.product').browse(cr, uid,product)
            return {'value': { 'name':prod.name,'product_uom':prod.uom_po_id.id,'product_qty': 1.0}}
        return {}
    
    def qty_change(self, cr, uid, ids, product_qty, context=None):
        """
        To check the product quantity to not vaulate transportaion order quantity.

        @return: True
        """
        for product in self.browse(cr, uid, ids):
            purchase_id = product.transportation_id.purchase_order_id
            if purchase_id.order_line:
                for line in purchase_id.order_line:
                    if product.product_id == line.product_id:
                        if product_qty > line.product_qty : 
                            raise osv.except_osv(_('wrong action!'), _('This Quantity is more than the Purchase Order Quantity ..'))
        return True
        

class transportation_driver(osv.osv):
    """
    To manage transportaion driver """

    _name = 'transportation.driver'
    _description = "Transportation Driver"
    _columns = {
            'name': fields.char('Reference', size=64, required=True, readonly=1, select=True),
            'driver_name': fields.char('Driver Name', size=64, required=True,),
            'phone_number': fields.integer('Phone Number'),
            'car_type': fields.char('Car Type', size=64, required=True, select=True),
            'car_number': fields.char('Car Number', size=64, required=True, select=True),
            'transportation_id': fields.many2one('transportation.order', 'Transportation ref',),
            'description': fields.text('Description'),
                }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'transportation.driver')
        }
    _sql_constraints = [
        #('tran_driver_uniq', 'unique(transportation_id,car_number)', 'Sorry You Entered The Same Car Tow Times for this transportaion order!'),
            ]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
                    
