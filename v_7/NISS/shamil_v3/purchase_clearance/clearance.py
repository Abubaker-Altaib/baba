# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
#********************************************************
# This class To Manage the Purchase Clearance operations 
#********************************************************

from osv import fields,osv
import netsvc
import time
from tools.translate import _
import decimal_precision as dp
from datetime import datetime

# Class Clearance 

class purchase_clearance(osv.osv):
    """ Manage purchase clearance """

    def create(self, cr, user, vals, context=None):
        """ 
        Override to create new entry sequence for name field of purchase clearance.

	    @param vals: list of record to be process
	    @return: super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'purchase.clearance')
        return super(purchase_clearance, self).create(cr, user, vals, context)

    def _calculate_bills_amount(self, cr, uid, ids,field_name, arg, context=None):
        """ 
        Calculate the total amount of clrarance bills.

	    @return: dictionary of bills total amount 
        """
        # billes amount well be the same but different approch will give  problem 
        # calculate the summation of the bills 
        res={}
        for clearance in self.browse(cr, uid, ids, context=context):
            res[clearance.id] = {
                'bills_amoun_total': 0.0,
            }
            bill_amount_sum = 0.0
            for bills in clearance.clearance_bills:
                bill_amount_sum += bills.bill_amount
            res[clearance.id]['bills_amoun_total'] = bill_amount_sum
        return res


    def clearance_purpose_change(self, cr, uid, ids, purpose,context=None):
        if purpose :
            for record in self.browse(cr, uid, ids, context=context):
                if record.clearance_products_ids :
                    for line in record.clearance_products_ids :
                        self.pool.get('purchase.clearance.products').write(cr,uid,line.id,{'clearance_purpose_pro':purpose})   
        return True

    
        
        
        
        
        
        
        
        
        
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('recieve_document', 'Waiting for Recieve the Exemption '),
        ('exemption', 'Exemption Receieved'),
	('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('gm', 'Waiting For Supply Manager to Handle'),
        ('supply', 'Waiting for Clearance Mananger'),
        ('clear_stage', 'Waiting For Accounting'),
        ('accounting_price', 'Waiting to Sending To Account To Process'),
        ('check_p','check Purpose'),
        ('done', 'Done'),
        ('cancel', 'Canceled'), ]

    TYPE_SELECTION = [
        ('internal', 'Inside the company'),
	    ('external', 'Outside the company'),
	]
    
    DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
	('free_zone','Free Zone'),
        ('land_freight', 'Land Freight'),
        ('halfa','Halfa'),
    ]

    CLEARANCE_SELECTION = [
        ('income', 'income'),
        ('outcome', 'outcome'),
    ]

    _name = "purchase.clearance"
    _order = "date desc,name desc"
    _columns = {
	'name': fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the purchase clearance,computed automatically when the purchase clearance is created"),
	'partner_id':fields.many2one('res.partner', 'Savier', states={'done':[('readonly',True)]}),
    'clearance_purpose': fields.selection([('purchase','Purchase'),('other','Other')],'Purpose', select=True, states={'confirmed':[('readonly',True)],'done':[('readonly',True)]}),
    'purchase_order_ref' : fields.many2one('purchase.order', 'Purchase order', states={'confirmed':[('readonly',True)],'done':[('readonly',True)]}),
    'date' : fields.date('Date',states={'done':[('readonly',True)]}),
	'final_invoice_no':fields.char('Final Invoice No',size=64, states={'done':[('readonly',True)]}),
	'bill_of_lading_date':fields.date('Bill of Lading Date',states={'done':[('readonly',True)]}),
    'document_hand_date':fields.date('Document Hand date', states={'done':[('readonly',True)]}),
	'ship_method':fields.selection(DELIVERY_SELECTION,'Bill By', states={'confirmed':[('readonly',True)],'done':[('readonly',True)]}),
	'supplier_duties':fields.char('Supplier Duties', size=64, states={'done':[('readonly',True)]}),
	'clearance_date':fields.date('Date Of Clearance', states={'done':[('readonly',True)]}),
	'insurance_no' : fields.char('Insurance No', size=64, states={'done':[('readonly',True)]}),
	'insurance_duties' : fields.char('Insurance Duties', size=64, states={'done':[('readonly',True)]}) ,
	'insurance_certificate':fields.boolean('Insurance Certificate', states={'done':[('readonly',True)]}), 
	'notes': fields.text('Notes', size=256 , states={'done':[('readonly',True)]}),
 	'clearance_products_ids':fields.one2many('purchase.clearance.products', 'products_clearance_id' , 'Products', states={'confirmed':[('readonly',True)],'done':[('readonly',True)]}),
    'clearance_category_ids':fields.one2many('clearance.items.category', 'clearance_id' , 'Categories', states={'confirmed':[('readonly',True)],'done':[('readonly',True)]}),
    'containers_ids' : fields.one2many('container.container','clearance_id','Containers'),
 	'user':  fields.many2one('res.users', 'Responsible',states={'done':[('readonly',True)]}),
 	'entry_user':  fields.many2one('res.users', 'entry User',),
	'type':fields.selection(TYPE_SELECTION,'Type', required=True, states={'done':[('readonly',True)]}),
	'ministry_date':fields.date('Ministry Date', states={'done':[('readonly',True)]}),
	'im_no':fields.char('IM No',size=64, states={'done':[('readonly',True)]}),
    'final_invoice_amount': fields.float('Final Invoice Amount', digits=(16,3)),
    'initial_customs_amount': fields.float('Initial Customs Amount', digits=(16,3)),
    'final_customs_amount': fields.float('Final Customs Amount', digits=(16,3)),
    'currency': fields.many2one('res.currency','Currency',select=1),
	'im_send_date':fields.date('IM Send Date', states={'done':[('readonly',True)]}),
	'im_recieve_date':fields.date('IM Recieve Date', states={'done':[('readonly',True)]}),
	'delivery_date':fields.date('Delivery Date', states={'done':[('readonly',True)]}),
    'send_to_clearance_date':fields.date('Send To Clearance Date', states={'done':[('readonly',True)]}),
    'receive_document_date':fields.date('Receive Document in port Date', states={'done':[('readonly',True)]}),
	'exemption_date':fields.date('Exemption Date', states={'done':[('readonly',True)]}),
    'clearance_bills':fields.one2many('purchase.clearance.billing', 'clearance_id' , 'Bills'),
    'initial_bills_amount': fields.float('Initial Billing Total amount', digits=(16,3)),
    'bills_amoun_total':fields.function(_calculate_bills_amount, method=True, digits_compute=dp.get_precision('Account'), string='Billing Total amount', multi='all',readonly=True, store=True),
    'description': fields.text('Transportation description', states={'done':[('readonly',True)]}), 
    'account_voucher_ids': fields.many2many('account.voucher', 'purchase_clearance_voucher', 'clearance_id', 'voucher_id', 'Account voucher'),
	'bill_of_lading' :fields.char('Bill of Lading NO', size=64,  states={'done':[('readonly',True)]}),
        'bill_of_lading_type':fields.selection([('origin','Origin'),('copy','Copy')],'Bill of Lading Type', states={'done':[('readonly',True)]}, select=True),
	'customs_certificate_no':fields.char('Customs Certificate No', size=64, states={'done':[('readonly',True)]}),

    'all_data_complete':fields.selection([('completed','Completed'),('not_completed','Not Completed')],'All Data omplete', states={'done':[('readonly',True)]}, select=True), 

    'origin_certificate':fields.selection([('received','Received'),('not_received','Not Received')],'Certificate of origin', states={'done':[('readonly',True)]}, select=True), 
    'origin_invoice':fields.selection([('received','Received'),('not_received','Not Received')],'Invoice of origin', states={'done':[('readonly',True)]}, select=True), 
    'sender_to':fields.selection([('niss','NISS'),('other','Other')],'Sender To', states={'done':[('readonly',True)]}, select=True), 

    'packing_list':fields.selection([('received','Received'),('not_received','Not Received')],'Packing List', states={'done':[('readonly',True)]}, select=True), 
    'abdication_certificate':fields.selection([('received','Received'),('not_received','Not Received')],'Abdication Certificate', states={'done':[('readonly',True)]}, select=True),
    'accept_abdication_send_date' : fields.date('Accept Abdication Send Date', states={'done':[('readonly',True)]}),
    'accept_abdication_recieve_date'  : fields.date('Accept Abdication  Recieve Date', states={'done':[('readonly',True)]}),
     'origin_certificate_no':fields.char('Origin Certificate No',size=64, states={'done':[('readonly',True)]}),
     'origin_certificate_date':fields.date('Origin Certificate Date', states={'done':[('readonly',True)]}),

     'packing_list_no':fields.char('Packing List No',size=64, states={'done':[('readonly',True)]}),
     'packing_list_date':fields.date('Packing List Date', states={'done':[('readonly',True)]}),


     'packing_type':fields.selection([('container','Containers'),('package','Packages'),('vehicle','Vehicles'),('other','Others')],'Packing Type', states={'done':[('readonly',True)]},),
     'packing_type_count': fields.integer('No. Packing Type', states={'done':[('readonly',True)]},),
     'transporter_company_id':fields.many2one('transporter.companies', 'Name Of Transporter', states={'done':[('readonly',True)]}),

     'facilitate_letter_send_date' : fields.date('Facilitate Letter Send', states={'done':[('readonly',True)]}),
     'facilitate_letter_recieve_date' : fields.date('Facilitate Letter Recieve', states={'done':[('readonly',True)]}),

     'fin_customs_fees_send_date' : fields.date('Fin Customs Fees Letter Send', states={'done':[('readonly',True)]}),
     'fin_customs_fees_recieve_date' : fields.date('Fin Customs Fees Letter Recieve', states={'done':[('readonly',True)]}),

     'fin_value_added_send_date' : fields.date('Fin Value Added Letter Send', states={'done':[('readonly',True)]}),
     'fin_value_added_recieve_date' : fields.date('Fin Value Added Letter Recieve', states={'done':[('readonly',True)]}),
     
      'fin_ports_send_date' : fields.date('Fin Ports Letter Send', states={'done':[('readonly',True)]}),
      'fin_ports_recieve_date' : fields.date('Fin Ports Letter Recieve', states={'done':[('readonly',True)]}),

      'customs_fees_send_date' : fields.date('Customs Fees Letter Send', states={'done':[('readonly',True)]}),
      'customs_fees_recieve_date' : fields.date('Customs Fees Letter Recieve', states={'done':[('readonly',True)]}),

     'value_added_send_date' : fields.date('Value Added Letter Send', states={'done':[('readonly',True)]}),
     'value_added_recieve_date' : fields.date('Value Added Letter Recieve', states={'done':[('readonly',True)]}),
     
      'ports_send_date' : fields.date('Ports Letter Send', states={'done':[('readonly',True)]}),
      'ports_recieve_date' : fields.date('Ports Letter Recieve', states={'done':[('readonly',True)]}),

     'detection_goods_date' : fields.date('Detection Goods Send', states={'done':[('readonly',True)]}),
      
     'detection_letter_send_date' : fields.date('Detection Letter Send', states={'done':[('readonly',True)]}),
     'detection_letter_recieve_date' : fields.date('Detection Letter Recieve', states={'done':[('readonly',True)]}),
     'final_invoice_date' : fields.date('Final Invoice Date', states={'done':[('readonly',True)]}),

      'authority_approve':fields.selection([('gm','Genernal Manager'),('vice_gm','Vice of Genernal Manager'),('authoritym_manager','Authority Manager'),('other','Others')],'Authority Approve', states={'done':[('readonly',True)]},),
     'final_approve_date' : fields.date('Final Approve Date', states={'done':[('readonly',True)]}),
     'message_content':fields.char('Message Content',size=64, states={'done':[('readonly',True)]}),

     'origin_country':fields.char('Origin Country',size=64, states={'done':[('readonly',True)]}), 
     'letter_recipient' : fields.many2one('res.partner' , 'Recipient' , states={'done':[('readonly',True)]}),
     'letter_given' : fields.char('Given' , states={'done':[('readonly',True)]}),
     'letter_given_phone' : fields.char( 'Given Phone No.' , states={'done':[('readonly',True)]}),

    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'department_id':fields.many2one('hr.department', 'Department', states={'done':[('readonly',True)]}),
    'company_id': fields.many2one('res.company','Company',required=True,select=1,readonly=True),
    'log_trace': fields.text('Notes', size=512 ,),
    'bill_description' :fields.char('Bill Description', size=64,  states={'done':[('readonly',True)]}),
    'need_voucher':fields.selection([('yes','Yes'),('no','No')],'Need Voucher', states={'done':[('readonly',True)]}, select=True), 
    'specifections_required':fields.boolean('Required Specifections', states={'done':[('readonly',True)]}, help="This Field for determinate the item in this letter need specifections Letter or not"), 
    }


    def _check_categ(self, cr, uid, ids, context=None): 
        """ 
        Constrain function to check the quantity of items and let just the positive quantity.
for requisition in self.browse(cr, uid, ids, context=context):
            for line in requisition.pro_ids:
                if line.product_qty < 0.0 :
                    return False
        return True
        @return: Boolean True or False  
        """
        #pro_obj=self.pool.get('product.product')
        for clearance in self.browse(cr, uid, ids, context=context):
            for line in clearance.clearance_products_ids:
                if line.category_id :
                    if line.category_id.id != line.product_id.categ_id.id:
                        
                        return False
        
        return True

    _constraints = [
        (_check_categ, 'Products category missmatch ! \n ',['clearance_products_ids']),
    ]
        

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Purchase Clearance Reference must be unique !'),
        ('custom_uniq', 'unique(customs_certificate_no)', 'Custom Certificate Number must be unique !'),
        ('bill_of_lading_uniq', 'unique(bill_of_lading)', 'Bill Of Lading must be unique !'),
        ('final_invoice_amount_check', 'CHECK ( final_invoice_amount >= 0 )', "The final invoice amount must be greater than or equal Zero."),]
        
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'state': 'draft',
                'date': lambda *a: time.strftime('%Y-%m-%d'),
                'type' : 'external' ,
                'entry_user': lambda self, cr, uid, context: uid,
                'clearance_purpose':'other',
                'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.clearance', context=c),
                }
    
    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Override copy function to edit defult value.

        @param default: default vals dict
        @return: super copy method  
        """
        bill_of_lading = self.browse(cr, uid, ids, context).bill_of_lading
        customs_certificate_no = self.browse(cr, uid, ids, context).customs_certificate_no
        if bill_of_lading:
            default.update({'bill_of_lading':bill_of_lading + '(copy)'})
        if customs_certificate_no:
            default.update({
              'customs_certificate_no' : customs_certificate_no + '(copy)'          
        })
        default.update({ 
            'name': self.pool.get('ir.sequence').get(cr, uid, 'purchase.clearance'),
            
        })
        return super(purchase_clearance, self).copy(cr, uid, ids, default, context)
    
    def purchase_ref(self, cr, uid, ids, purchase_ref, context=None):
            """ 
            Dummey function to update the purchase orders field.

	        @param purchase_ref: purchase order id 
	        @return: Empty dictionary 
            """
            return {}
        
        
    
        
    def get_products(self,  cr, uid, ids, purchase_id, context={}): 
        """
        To read purchase order lines when select a purchase order.

        @param purchase_id: purchase order id
        @return: boolean True 
        """
        purchase_obj = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
        clearance_product_odj=self.pool.get('purchase.clearance.products')
        clearance = self.pool.get('purchase.clearance').browse(cr, uid, ids)
        if clearance[0].clearance_products_ids != []:
            raise osv.except_osv(_('this clearance is already contain products !'), _('to chose a Purchase Order delete all the products first ..'))            
        for product in purchase_obj.order_line:
            clearance_product_odj.create(cr,uid,{
                  'name': purchase_obj.name + ': ' +(product.name or ''),
                  'product_id': product.product_id.id,
                  'category_id' : purchase_obj.cat_id.id or product.product_id.categ_id.id ,
                  'price_unit': product.price_unit,
                  'product_qty': product.product_qty, 
                  'product_uom': product.product_uom.id,
                  'products_clearance_id': ids[0],
                  'description': 'purchase order '+ purchase_obj.name , 
                  'purchase_line_id': product.id ,
                  'price_unit': product.price_unit,         
                                                         })
        self.write(cr,uid,ids,{'description':purchase_obj.name})
        return True
           
    def load_items(self, cr, uid, ids,purchase_id, context=None):
        """ 
        To lode purchase order lines of the selected purchase order to clearance lines.

        @param purchase_ref: purchase order id 
        @return: True  
        """
        clearance_product_obj = self.pool.get('purchase.clearance.products')
        items_category_obj = self.pool.get('clearance.items.category')

        for clearance in self.browse(cr, uid, ids):
            if clearance.clearance_purpose == 'purchase':
                if clearance.purchase_order_ref:
                    self.get_products(cr, uid, ids,clearance.purchase_order_ref.id, context=context)
            else:
                
                items_category_obj.create(cr, uid, {'clearance_id':clearance.id , 'clearance_purpose_pro':clearance.clearance_purpose}, context)    
        return True
    


    def create_container(self,cr,uid,ids,context=None):
          container_obj = self.pool.get('container.container')
          for line in self.browse(cr,uid,ids):
              container_id = container_obj.create(cr,uid,{'clearance_id' : line.id ,} )
          return container_id 



    def confirmed(self, cr, uid, ids, context=None):
        """
        Workflow function to change state of purchase clearance from draft To confirmed.
 
        @return: True 
        """
        wf_service = netsvc.LocalService("workflow")
        for clearance in self.browse(cr, uid, ids):
            if not clearance.need_voucher:
                    raise osv.except_osv(_('Missing Need Voucher !'),_('Please fill The Need Voucher Field first') ) 


            if clearance.need_voucher == 'no' :
               
               wf_service.trg_validate(uid, 'purchase.clearance', clearance.id, 'confirmed_to_done', cr)
	       self.write(cr, uid, ids, {'state':'done'},context=context)
               
            

            else : 
		if clearance.clearance_purpose == 'purchase' :
    		    if not clearance.clearance_products_ids:
    		           raise osv.except_osv(_('No Products  !'), _('Please fill the products list first ..'))       
    		    if clearance.purchase_order_ref:
    		        if not clearance.clearance_products_ids:
    	     	            raise osv.except_osv(_('Load purchase items first!'), _('Please Load purchase items Purchase Order ..'))
	        else :
		    if not clearance.clearance_category_ids:
		       raise osv.except_osv(_('No Category  !'), _('Please fill the Categories list first ..')) 
		             
		if not clearance.clearance_bills or clearance.bills_amoun_total <= 0:
		          raise osv.except_osv(_('No Bills  !'), _('Please add or fill bills first ..'))
                    
		if not clearance.authority_approve :
                    raise osv.except_osv(_('Missing Authority Approve !'),_('Please fill The Authority Approve Field first') )     
		if not clearance.bill_description :
                    raise osv.except_osv(_('Missing Bill Description !'),_('Please fill The Bill Description Field first') )
               
		voucher_obj = self.pool.get('account.voucher')
		clearance_obj = self.pool.get('purchase.clearance').browse(cr,uid,ids)
		voucher_line_obj = self.pool.get('account.voucher.line')
		purchase_obj = self.pool.get('purchase.order') 
		clearance_products_obj = self.pool.get('purchase.clearance.products') 
		clearance_voucher=[]
		purchase_ids=[]
		purchase = ''
		for clearance in clearance_obj:
		    if clearance.clearance_purpose == 'purchase':
		        purchase = clearance.purchase_order_ref.name
		        purchase_ids.append(clearance.purchase_order_ref.id)               
		        items_amount = clearance._calculate_clearance_amount()
		    journal = clearance.company_id.clearance_jorunal
		    account = clearance.company_id.clearance_account
		    if not journal:
		        raise osv.except_osv(_('wrong action!'), _('no clearance journal defined for your company!  please add the journal first ..'))
		    if not account:
		        raise osv.except_osv(_('wrong action!'), _('no clearance account defined for your company!  please add the account first ..'))
		    
		    partner = clearance.partner_id            
		    if clearance.type in ['internal']:
		        partner = clearance.user.partner_id
		        result_amount = 0 
		    if not partner.property_account_payable:
		        raise osv.except_osv(_('No Account !'), _('Please add account for partner ..'))
		    voucher_id = voucher_obj.create(cr, uid, {
		                                'amount': clearance.bills_amoun_total,
		                                'type': 'purchase',
		                                'date': time.strftime('%Y-%m-%d'),
		                                'partner_id': partner.id , 
		                                'account_id': partner.property_account_payable.id , 
		                                'amount':clearance.bills_amoun_total,
		                                'journal_id': journal.id,
		                                'reference': clearance.name + purchase,
		                                'state': 'draft',
		                                'name': clearance.bill_description})
		    clearance_voucher.append(voucher_id)
		    line_ids=[]
		    for bill in clearance.clearance_bills :
		        account = clearance.get_account(clearance, bill.price_type)
		        vocher_line_id = voucher_line_obj.create(cr, uid, {
		                                'amount': bill.bill_amount,
		                                'voucher_id': voucher_id,
		                                'type': 'dr',
		                                'account_id': account.id,
		                                'name': bill.description.name,
		                                 })
		voucher_obj.compute_tax(cr, uid, [voucher_id], context=context)
		self.write(cr, uid, ids, {'state':'confirmed','account_voucher_ids':[(6,0,clearance_voucher)]}) 
		if clearance.clearance_purpose == 'purchase': 
		    self.allocate_purchase_order_line_price(cr, uid, ids, purchase_ids, items_amount)               
       

        return True


    def approved(self, cr, uid, ids, context=None):

        for clearance in self.browse(cr, uid, ids):

            if not clearance.clearance_bills:
                raise osv.except_osv(_('No Bills  !'), _('Please add bills first ..'))
        """
        Workflow function to change state of purchase clearance from draft To approved.
 
        @return: True 
        """

        self.write(cr, uid, ids, {'state':'approved'})        
       
        return True



    def gm(self,cr,uid,ids,context=None):
        """ 
        Workflow function to change state to gm.

	    @return: Ture 
        """
        self.write(cr, uid, ids, {'state':'gm'},context=context)
        return True

    def supply(self,cr,uid,ids,context=None):
        """ 
        Workflow function to change state to supply.

	    @return: Ture
        """
        self.write(cr, uid, ids, {'state':'supply'},context=context)
        return True

    def recieve_document(self,cr,uid,ids,context=None):
        """ 
        Workflow function to change state to recieve_document.

	    @return: Ture
        """
        self.write(cr, uid, ids, {'state':'recieve_document'},context=context)
        return True

    def exemption(self,cr,uid,ids,context=None):
        """ 
        Workflow function to change state to exemption.

	    @return: Ture
        """
        for clearance in self.browse(cr, uid, ids):
            if not clearance.send_to_clearance_date :
               raise osv.except_osv(_('Missing Send To Clearance date !'),_('Please fill The Send To Clearance date Field first') )
        self.write(cr, uid, ids, {'state':'exemption'},context=context)
        return True

    def clear_stage(self,cr,uid,ids,context=None):
        """ 
        Workflow function to change state to clear_stage.

	    @return: Ture
        """
        self.write(cr, uid, ids, {'state':'clear_stage'},context=context)
        return True


    def check_p(self,cr,uid,ids,*args):
        """ 
        Workflow function of router to fire check_type.

	    @return: Ture
        """
        return True

    def check_type(self,cr,uid,ids,*args):
        """ 
        Workflow function to ckeck the type of clearance.

	    @return: Ture or False
        """
        obj = self.browse(cr, uid, ids)[0]
        if obj.clearance_purpose == 'other' : 
            return True
        return False


    def accounting_price(self,cr,uid,ids,context=None):
        """ 
        Workflow function to change state to accounting_price.

	    @return: Ture
        """
        self.write(cr, uid, ids, {'state':'accounting_price'},context=context)
        return True
 

    def get_account(self, cr, uid ,ids,clearance , bill_type):
        """ 
        To read the appropriate account for the clearance according to its type and creation.
 
        @param clearance: clearance object
        @param bill_type: price allocation type
        @return: account object 
        """
        account = clearance.company_id.clearance_account
        if bill_type == 'add':
            if clearance.clearance_purpose == 'purchase': 
                if clearance.purchase_order_ref.purchase_type == 'foreign':
                    if not clearance.company_id.purchase_foreign_account:
                        raise osv.except_osv(_('NO Account !'), _('no account defined for purchase foreign.'))
                        account = clearance.company_id.purchase_foreign_account
                    if clearance.purchase_order_ref.contract_id:
                        if not clearance.purchase_order_ref.contract_id:
                            raise osv.except_osv(_('Missing Account Number !'),_('There No Account Defined Fore This Contract    please chose the account first') )
                        account = clearance.purchase_order_ref.contract_id.contract_account
        return account

 
    def done(self, cr, uid, ids, context={}):
        """ 
        Workflow function to create account voucher and change state to done.

	    @return: Ture
        """       
        # change state From Confirmed to done , create voucher and voucher lines    
        check = False 
        for rec in self.browse(cr,uid,ids):
            for voucher in rec.account_voucher_ids :
                if voucher.state == 'posted' :
                   check = True
            if check == False: 
               raise osv.except_osv(_('Bad Action !'), _('The Supplier Check doesnt printed yet'))
        self.write(cr, uid, ids, {'state':'done'})
        return True
    
    def allocate_purchase_order_line_price(self, cr, uid, ids, purchase_ids, items_amount):
        """ 
        Calculate clearance price for every purchase line and write the price to purchase order lines.

        @param purchase_ids: list of purchase orders ids
	    @return: Ture 
        """
        purchase_line_obj = self.pool.get('purchase.order.line')
        clearance_product_obj = self.pool.get('purchase.clearance.products')
        amount = 0
        for purchase in self.pool.get('purchase.order').browse(cr, uid, purchase_ids):
            for line in purchase.order_line:
                clearance_item = clearance_product_obj.search(cr,uid,[('product_id','=',line.product_id.id),('products_clearance_id','=',ids[0])])
                clearance_product = clearance_product_obj.browse(cr, uid, clearance_item)
                for item_list in items_amount:
                    if clearance_item[0] == item_list[0].id :
                        amount = item_list[1]
                #amount = clearance_product[0].clearance_price_unit
                total = line.extra_price_total+amount
                purchase_line_obj.write(cr,uid,line.id,{'clearance_price': amount,'extra_price_total':total})
        return True
    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function to changes clearance state to cancell and writes notes.

	    @param notes : contains information.
        @return: True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'purchase clearance Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        To changes clearance state to Draft.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
		    self.write(cr, uid, s_id, {'state':'draft'})
		    wf_service.trg_delete(uid, 'purchase.clearance', s_id, cr)            
		    wf_service.trg_create(uid, 'purchase.clearance', s_id, cr)
        return True
    
    def _calculate_clearance_amount(self, cr, uid, ids, context=None):
        """ 
        Calculate clearance amount for every clearance line accourding to allocation base 
        the default allocation is price percentage.

        @return: True
        """
        res = []
        purchase_line = self.pool.get('purchase.order.line')
        for clearance  in self.browse(cr,uid,ids):
            # get the total amount from bills for quantity base and weight base 
            # allocation when the type of price is add to item 
            amount_all_weight = amount_all_quantity = total_qty = total_weight = all_amount_price = 0.0
            total_purchase_price = clearance.purchase_order_ref.amount_untaxed
            for bill in clearance.clearance_bills :
                if bill.price_type =='add':
                    if bill.allocation_base == 'quantity': amount_all_quantity += bill.bill_amount
                    if bill.allocation_base == 'weight': amount_all_weight += bill.bill_amount
                    else: all_amount_price += bill.bill_amount
            # get the total quantity and weight for the items     
            for item in clearance.clearance_products_ids:
                total_qty += item.product_qty
                if item.product_weight:
                    total_weight += item.product_weight
                else: 
                    if amount_all_weight > 0.0:
                        raise osv.except_osv(_('No Product weight !'), _('Please fill the product weight first ..')) 
            # allocate the price for all products    
            for item in clearance.clearance_products_ids:
                if item.purchase_line_id:
                    line = item.purchase_line_id.id
                else : 
                    try :
                        line = purchase_line.search(cr, uid,[('order_id','=',clearance.purchase_order_ref.id), ('product_id','=',item.product_id.id),('product_qty','=',item.product_qty)])[0] 
                    except :
                        raise osv.except_osv(_('Warrning !'), _('Can not find purchase line')) 
                line_obj = purchase_line.browse(cr, uid, line)
                clearance_price = 0.0
                if amount_all_quantity:
                    clearance_price += (amount_all_quantity * (item.product_qty / total_qty))/item.product_qty
                if amount_all_weight:
                    clearance_price += (amount_all_weight * (item.product_weight / total_weight))/item.product_weight
                if all_amount_price:
                    clearance_price += all_amount_price * (line_obj.price_unit / total_purchase_price)
                item.write({'clearance_price_unit': clearance_price}),"   ",line_obj.price_unit
                res.append([item, clearance_price])
        return res
    
    def onchange_ship_method(self, cr, uid, ids, ship_method ,context=None):
        """
        On change ship method function to change packing type

        @param ship method: ship method
        @return: Dictionary 
        """
        partner_id = []
        notes = ""
        user = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'The Document Changed  at : '+time.strftime('%Y-%m-%d') + ' by '+ user
       
        if ship_method :
           record_id = self.pool.get('partner.ship.config').search( cr, uid, [('ship_method','=', ship_method) ])
           if record_id :
              for record in self.pool.get('partner.ship.config').browse(cr,uid,record_id):
                  partner_id = record.partner_id.id
           
           return {'value': { 
                             'partner_id' : partner_id  or False,
                             'log_trace' : notes }}
        return {}
    
    def create_quote(self,cr, uid, ids, context=None):  
        
        """
        Generates quotation  of internal requestion orders and links that quotation ID 
        with current requestion order.

        @return: True
        """ 
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.clearance_category_ids or obj.clearance_products_ids:         
                pq_id = self.pool.get('purchase.clearance.billing').create(cr, uid, {'clearance_id': obj.id,'ship_method' : obj.ship_method}, context=context)
            else:
                raise osv.except_osv(_('No Products !'), _('Please fill the product list first ..'))
        return pq_id

class purchase_clearance_products(osv.osv):
    """ 
    Manage purchase clearance Products """

    _name = "purchase.clearance.products"
    _description = 'Products of Purchase Clearance'
    


    '''def create(self, cr, uid, vals, context=None):
        clearance_purpose=vals and vals['products_clearance_id'] and  self.pool.get('purchase.clearance').browse(cr, uid, vals['products_clearance_id'], context).clearance_purpose or 'purchase'
        if clearance_purpose =='purchase' :
            raise osv.except_osv(_('Can not add new items'), _('because clearance purpose is purchase'))
        vals ['clearance_purpose_pro'] = clearance_purpose
        return super(purchase_clearance_products, self).create(cr, uid, vals, context)
'''




    _columns = {
                'name': fields.char('Name', size=64 ),
                'product_id': fields.many2one('product.product','Item'),
                'clearance_price_unit': fields.float('Clearance price', digits=(16,2)), 
                'product_qty': fields.float('Item Quantity', required=True, digits=(16,2)),
                'product_weight': fields.float('Item Weight', digits=(16,2)),
                'product_uom': fields.many2one('product.uom', 'Item UOM'),
                'product_packaging': fields.many2one('product.packaging', 'Items Packing', help="Control the packages of the products"),
                'products_clearance_id': fields.many2one('purchase.clearance', 'Purchase clearance', ondelete='restrict'),
                'notes': fields.text('Notes', size=256 ,),
                'description': fields.text('Specification'),
                'category_id': fields.many2one('product.category','Category'),
                'purchase_line_id': fields.many2one('purchase.order.line','order_line'),
                'price_unit': fields.float('Purchase Price Unite', digits=(16,2)),
                'clearance_purpose_pro': fields.selection([('purchase','Purchase'),('other','Other')],'Purpose', readonly=True),
               }

    
    _sql_constraints = [
        ('produc_uniq', 'unique(products_clearance_id,product_id)', 'Sorry You Entered Product Two Time You are not Allow to do this.... So We going to delete The Duplicts!'),
        ('product_quantity_check', 'CHECK ( product_qty > 0 )', "Product quantity must be greater than Zero."),
        ('product_weight_check', 'CHECK ( product_weight >= 0 )', "Product wieght must not be less than Zero."),
                 ]  

    _defaults = {
                 'product_qty': 1.0,
                 'clearance_purpose_pro':'purchase',
                 } 
 
    def product_id_change(self, cr, uid, ids,product):
       """
       On change product_id method to read the default name and UOM of product.

       @param product: product_id 
       @return: dictionary of product name and uom
       """
       if product:
           prod= self.pool.get('product.product').browse(cr, uid,product)
           return {'value': { 'name':prod.name,'product_uom':prod.uom_po_id.id}}




class purchase_clearance_billing(osv.osv):
    """ 
    Manage clearance bills """
    
    
    
    
    
    
    
    _name = "purchase.clearance.billing"
    _description = 'Purchase Clearance Billing Information' 
    _columns = { 
                'name': fields.char('Name', size=64 ,required=True), 
                'clearance_id':  fields.many2one('purchase.clearance', 'Clearance',),
                'ship_method': fields.char('Ship Method', size=64 ,readonly=True ),
                'bill_amount': fields.float('Bill Amount', digits=(16,2)),  
                'bill_no': fields.char('Bill No', size=64 ),
                'bill_date': fields.date('Bill Date'),
                'partner_id':fields.many2one('res.partner', 'Supplier',),
                'allocation_base':fields.selection([('weight','WEIGHT'),('quantity','QUANTITY'),('price','PRICE')],'Allocation Base', ),
                'price_type':fields.selection([('add','Add To Items'),('not_add','Not Add To Items Price')],'Price Type', ),
                'description': fields.many2one('bill.clearance.items', 'Specification',),
               }
    
    
    
    
      
    _defaults = {
                'name': lambda self, cr, uid, context: '/', 
                'price_type' : 'not_add' ,
                'allocation_base' : 'price' ,
                }
    _sql_constraints = [

        ('bill_amount_check', 'CHECK ( bill_amount > 0 )', "Bill amount must be greater than Zero."),
        ('bill_items_unique', 'unique(clearance_id,description)', 'Sorry You Entered Description Two Time You are not Allow to do this.... Please delete The Duplicts!'),
       ]
    
    

class container_container(osv.osv):
      
    
      def compute_fine(self,cr,uid,ids,context=None):
           
          for line in self.browse(cr,uid,ids):
             
              if line.date_delivery : 
              
		 d1 = datetime.strptime(line.date_delivery,"%Y-%m-%d")
		 d2 = datetime.strptime(line.date_planned,"%Y-%m-%d")      
		 dif = d1 - d2
		 no_days = dif.days
		 if no_days > 0 :
	            self.write(cr,uid,ids,{'fine_day' : no_days })
		     
              
          return True
      def change_container_stauts(self,cr,uid,ids,context=None):

          for con in self.browse(cr,uid,ids):
              
              return {'value' :  {'container_stauts' : 'returned'} }
      _name = "container.container"
      _columns = {
         'clearance_id' : fields.many2one('purchase.clearance','Clearance ID',),
         'no_container' : fields.char('Container No',size=16),
         'date_received' : fields.date('Received Date'),
         'date_planned' : fields.date('Planned Date'), 
         'date_delivery' : fields.date('Delivery Date'),
         'container_size' : fields.selection([('20','20 F'),('40','40 F')],'Container Size'),
         'container_target' : fields.many2one('hr.department','Destination' , size=64 ),
         'container_type' : fields.selection([('own','OWN'),('rent','RENT')],'Container Type'),
         'container_owner_name' : fields.char('Name Of Container Owner',size=32),
         'container_stauts' : fields.selection([('returned','Returned'),('not yet','Not Yet')],'Container Stauts'),
         'fine_day' : fields.char('No Of Days' , size=16),
         'desc' : fields.text('Description'),
         
                    }
       
      _defaults = {
   
         'container_stauts' : 'not yet' 
                   }


class clearance_items_category(osv.osv):
    """ 
    Manage purchase clearance Category """

    _name = "clearance.items.category"
    _description = 'Category of Items'
    


    




    _columns = {
                'name': fields.char('Name', size=64 ),
                'category_id': fields.many2one('items.category','Category'),
                'category_qty': fields.float('Item Quantity', required=True, digits=(16,2)),
                'clearance_id': fields.many2one('purchase.clearance', 'Purchase clearance', ondelete='restrict'),
                'notes': fields.text('Notes', size=256 ,),
                'clearance_purpose_pro': fields.selection([('purchase','Purchase'),('other','Other')],'Purpose', readonly=True),
               }

    
    _sql_constraints = [
        ('category_uniq', 'unique(clearance_id,category_id)', 'Sorry You Entered category Two Time You are not Allow to do this.... So We going to delete The Duplicts!'),
        ('category_quantity_check', 'CHECK ( category_qty > 0 )', "category quantity must be greater than Zero."),
                 ]  

    _defaults = {
                 'category_qty': 1.0,
                 } 
