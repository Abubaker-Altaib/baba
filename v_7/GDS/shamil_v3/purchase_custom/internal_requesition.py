# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import netsvc
import time
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class ireq_m(osv.osv):
    """
    internal requisition which manging the purchase for approval orders"""
    
    def next_by_id(self, cr, uid, sequence_id, context=None):
        """
        Override to edit Sequences to read company from res_user.

        @param sequence_id: sequence id 
        @return: object _next method
        """
        seq_obj = self.pool.get('ir.sequence')
        user_obj = self.pool.get('res.users')
        self.check_access_rights(cr, uid, 'read')
        company_id = user_obj.browse(cr, uid, uid).company_id.id 
        ids = seq_obj.search(cr, uid, ['&',('id','=',
sequence_id),('company_id','in',[company_id, False])])
        return seq_obj._next(cr, uid, ids, context)

    def next_by_code(self, cr, uid, sequence_code, context=None):
        """
        Gets the sequence by code.

        @param sequence_code: Code of the sequence by which we'll fetch the sequence
        @param context: standard dictionary
        @return: object _next method
        """
        seq_obj = self.pool.get('ir.sequence')
        user_obj = self.pool.get('res.users')
        self.check_access_rights(cr, uid, 'read')
        #Get the company only from user
        company_id = user_obj.browse(cr, uid, uid).company_id.id 
        ids = seq_obj.search(cr, uid, ['&',('code','=',
sequence_code),('company_id','in',[company_id,False])])
        return seq_obj._next(cr, uid, ids, context)

    def get_id(self, cr, uid, sequence_code_or_id, code_or_id='id', context=None):
        """ 
        Draw an interpolated string using the specified sequence.
        The sequence to use is specified by the ``sequence_code_or_id``
        argument, which can be a code or an id (as controlled by the
        ``code_or_id`` argument. This method is deprecated.
             
        @param sequence_code_or_id: code or id of the sequence
        @param code_or_id: type of the sequence
        @return: object next_by_code or next_by_id method
        """
        _logger.debug("ir_sequence.get() and ir_sequence.get_id() are deprecated. "
            "Please use ir_sequence.next_by_code() or ir_sequence.next_by_id().")
        if code_or_id == 'id':
            return self.next_by_id(cr, uid, sequence_code_or_id, context)
        else:
            return self.next_by_code(cr, uid, sequence_code_or_id, context)

    def get(self, cr, uid, code, context=None):
        """ 
        Draw an interpolated string using the specified sequence.
        The sequence to use is specified by its code. This method is
        deprecated.

        @param code: code of the sequence
        @return: object get_id method   
        """
        return self.get_id(cr, uid, code, 'code', context)

    def create(self, cr, user, vals, context=None):
        """ 
        Override to edit the name field by a new sequence. 

        @return: new object id 
        """

        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'ireq.m'
            vals['name'] = self.pool.get('ireq.m').get(cr, user, seq_obj_name)
        new_id = super(ireq_m, self).create(cr, user, vals, context)
        return new_id 
#
# Model definition
#
    _name = "ireq.m"
    _description = 'Custom Purchase Intial Request'
    STATE_SELECTION = [
         ('draft', 'Draft Request'),
         ('confirmed_d','Department Approved'),
         ('confirmed_s','Supply Department Approved'),
         ('confirmed','Approved to be Procured'),
         ('wait_confirmed','Wait Confirmed'),
         ('approve1','Approved By Purchase Dept'),
         ('approve2','Approved by Supply Dept'),
         ('done','Done'),
         ('cancel', 'Cancelled')
         ]
    _columns = {
                'name': fields.char('Request ID', size=256, required=True, readonly=True),
                'company_id': fields.many2one('res.company','Company',required=True,readonly=True, states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_s':[('readonly',False)]}),
                'department_id':fields.many2one('hr.department', 'Department',readonly=True, states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_s':[('readonly',False)]}, ),
                'ir_date': fields.date('Request Date', readonly=True, states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_s':[('readonly',False)]}),
                'account_id':fields.many2one('account.account', 'Account',),
                'cat_id':fields.many2one('product.category', 'Category',readonly=True, states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_s':[('readonly',False)]} ),
                'ir_ref': fields.char('Exchange No.', size=256,readonly=True),
                'purpose': fields.selection([('store', 'Feed Store')],'Purpose',readonly=True, states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_s':[('readonly',False)]}),
                'pro_ids':fields.one2many('ireq.products', 'pr_rq_id' , 'Products',readonly=True, states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_s':[('readonly',False)]} ),
                'q_ids':fields.one2many('pur.quote', 'pq_ir_ref' ,'Quotes',readonly=True, states={'confirmed':[('readonly',False)],'wait_confirmed':[('readonly',False)]}),
                'chose': fields.boolean('chose',),
                'r1':fields.boolean('Good delivery', readonly=True, states={'confirmed':[('readonly',False)],'wait_confirmed':[('readonly',False)]}),
                'r2':fields.boolean('High quality',readonly=True, states={'confirmed':[('readonly',False)],'wait_confirmed':[('readonly',False)]},),
                'r3':fields.boolean('Good price',readonly=True, states={'confirmed':[('readonly',False)],'wait_confirmed':[('readonly',False)]}, ),
                'r4': fields.char('Other Reasons', size=256 ,readonly=True, states={'confirmed':[('readonly',False)],'wait_confirmed':[('readonly',False)]},),
                'purchase_type': fields.char('Purchase Type', size=256 ,readonly=True, states={'confirmed':[('readonly',False)],'wait_confirmed':[('readonly',False)]}, ),
                'notes': fields.text('Notes', size=256 ,),
                'inform': fields.char('information', size=125 ,readonly=True),
                'user':  fields.many2one('res.users', 'Responsible', readonly=True,),
                'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, select=True),
               }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Intial Request Reference must be unique !'),
    ]

    def _check_quantity(self, cr, uid, ids, context=None): 
        """ 
        Constrain function to check the quantity of items and let just the positive quantity.

        @return: Boolean True or False  
        """
        for requisition in self.browse(cr, uid, ids, context=context):
            for line in requisition.pro_ids:
                if line.product_qty < 0.0 :
                    return False
        return True

    _constraints = [
        (_check_quantity, 'Products quantity ! \n kindly fill the product quantity with positive value .',['pro_ids']),
    ]
    _order = "ir_date desc,name desc"
    _defaults = {
                'name': '/',
                'user': lambda self, cr, uid, context: uid,
                'ir_date': time.strftime('%Y-%m-%d'),
                'purpose':'store',
                'chose': 0,
                'notes': '/',
                'ir_ref':'/',
                'r1': 0,
                'r2': 0,
                'r3': 0,
                'r4': '',
                'state':'draft',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'ireq.m', context=c),
                }

    def onchange_category_check_products_line(self,cr,uid,ids,cat_id,pro_ids,context=None):
        """
        Checks the products lines and order category to prohibit the user from change the category
        of the order  and mack sure no products from diffrent category in the order.

        @param cat_id: product category id 
        @param pro_ids: product id 
        @return: values of product category and warning 
        """
        res={}
        if pro_ids:
	    for pro in pro_ids:
                product = product_id = self.pool.get('ireq.products').browse(cr,uid,pro[1]).product_id # Take the first product in products lines                   
                values = {'cat_id': cat_id} 
                values.update({'cat_id': product.categ_id.id}) # Update the category value by the old one
		if (cat_id != product.categ_id):
                    warning={'title': _('Warning'), 'message': _('The selected cateogry is not related to ordered products, the 				ordered  product have this category %s') % product.categ_id.name}
                    return {'value':values,'warning':warning}
        return {}

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict 
        @return: id of the newly created record  
        """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'ireq.m'),
            'q_ids':[],
        })
        return super(ireq_m, self).copy(cr, uid, id, default, context)


    def unlink(self, cr, uid, ids, context=None):
        """ 
        Ovrride to add constain on deleting the records. 

        @return: super unlink method
        """
        if context is None:
            context = {}
        if [ir for ir in self.browse(cr, uid, ids, context=context) if ir.state in ['done','cancel']]:
            raise osv.except_osv(_('Invalid action !'), _('You cannot remove Requisition in done or cancel state !'))
        return super(ireq_m, self).unlink(cr, uid, ids, context=context)

    # Workflow functions 
    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes state to Draft and reset the workflow.

        @return: Boolean True 
        """
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:            
            # Deleting the existing instance of workflow for Internal requestion
            wf_service.trg_delete(uid, 'ireq.m', s_id, cr)            
            wf_service.trg_create(uid, 'ireq.m', s_id, cr)
        return True    

    def cancel(self,cr,uid,ids,notes='',context=None):
        """ 
        Workflow function changes order state to cancel and writes note
	    which contains Date and username who do cancellation.

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        #if not notes:
        notes = ""
        user = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'purchase requisition Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ user
        self.write(cr, uid, ids, {'state':'cancel','inform':notes}, context=context)
        return True
    
    def confirmed_d(self,cr,uid,ids,context=None):
        """ 
        Workflow function checks the products lines, category and change order state to confirmed_d.

	    @return: True 
        """
        if [ir for ir in self.browse(cr, uid, ids) if ir.pro_ids ]:
            self.write(cr, uid, ids, {'state':'confirmed_d'}, context=context)
        else:
            raise osv.except_osv( _('No Products !'), _('Please make sure you fill the products ..'))
        for req in self.browse(cr, uid, ids):
            for line in req.pro_ids:
                if line.product_qty == 0.0:
                    raise osv.except_osv( _('Zero Products quantity !'), _('Please make sure you fill the products quantity..'))
        return True

    def view_quotation(self, cr, uid, ids, context=None):
        """ 
        Display existing quotations of given purchase requisition ids.
   
        @return: action to display quotations 
        """
        mod_obj = self.pool.get('ir.model.data')
        quote_ids = []
        for req in self.browse(cr, uid, ids, context=context):
            quote_ids += [quote.id for quote in req.q_ids]

        action_model, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'purchase_custom', 'act_internal_requstion_2_quotes'))
        action = self.pool.get(action_model).read(cr, uid, action_id, context=context)
        ctx = eval(action['context'])
        ctx.update({
            'search_default_purchase_id': ids[0]
        })
        if quote_ids and len(quote_ids) == 1:
            form_view_ids = [view_id for view_id, view in action['views'] if view == 'form']
            view_id = form_view_ids and form_view_ids[0] or False
            action.update({
                'views': [],
                'view_mode': 'form',
                'view_id': view_id,
                'res_id': quote_ids[0]
            })

        action.update({
            'context': ctx,
        })
        return action
    
    def confirmed_s(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to confirmed_s.
        
        @return: True 
        """
        self.write(cr, uid, ids, {'state':'confirmed_s'}, context=context)       
        return True
    
    def approve1(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to approve1.

        @return: True 
        """
        self.write(cr, uid, ids, {'state':'approve1'},context=context)
        return True
    
    def approve2(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to approve2.

        @return: True
        """
        self.write(cr, uid, ids, {'state':'approve2'}, context=context)
        return True

    def confirmed(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to confirmed.

	    @return: True 
        """
        self.write(cr, uid, ids, {'state':'confirmed'},context=context)
        return True

    def create_quote(self,cr, uid, ids, context=None):  #Calling from Create Qoutation button to create new qoute
        """
        Generates quotation  of internal requestion orders and links that quotation ID 
	    with current requestion order.

        @return: True
        """ 
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.pro_ids:         
                pq_id = self.pool.get('pur.quote').create(cr, uid, {'pq_ir_ref': obj.id,}, context=context)
                for product in obj.pro_ids:
                    prod_name = self.pool.get('product.product').browse(cr, uid,product.product_id.id, context=context).name
                    q_id = self.pool.get('pq.products').create(cr, uid, {
                    'name': prod_name,
                    'price_unit': 0.0,
                    'price_unit_tax': 0.0,
                    'price_unit_total': 0.0,
                    'product_id': product.product_id.id,
                    'product_qty': product.product_qty,
                    'pr_pq_id':pq_id,
                    'req_product': product.id,
                    'desc': product.desc,
                    })
            else:
                raise osv.except_osv(_('No Products !'), _('Please fill the product list first ..'))
        return q_id
    
    def create_purchase_order(self,cr, uid, ids, context=None):
        """
        Creates purchase order from quotation which is in done state 
        and then change the workflow state to done.

        @return: Boolean True
        """
        #print"================================================++++++"
        purchase_obj = self.pool.get('purchase.order')
        if[ir for ir in self.browse(cr, uid, ids) if purchase_obj.search(cr, uid, [('ir_id','=',ir.id)])]:
            raise osv.except_osv(_('Purchase Order(s) Exsits !'), _('The Purchase Order(s) from this purchase requesition was alreadry created..\n Please .. Check Purchase Orders List ..'))
        else:
            qoute_ids = [qoute.id for qoute in ir.q_ids if qoute.state == 'done']
            purchase_id = self.pool.get('pur.quote').make_purchase_order(cr, uid, qoute_ids)
            self.write(cr, uid, ids, {'state':'done'}, context=context)
            return purchase_id   

#
# Model definition
#
class ireq_products(osv.osv):
    """
    manage the products of the initial requition"""

    _name = "ireq.products"
    _description = 'Products of the Request for approval of a purchase'
    _columns = {
                'name': fields.char('Name', size=64 ,select=True,required=True,states={'done':[('readonly',True)]},),
                'product_id': fields.many2one('product.product','Item', change_default=True, required=True ,states={'done':[('readonly',True)]},),
                'price_unit': fields.float('Unit Price'),
                'product_qty': fields.float('Quantity', required=True, digits=(16,2),states={'done':[('readonly',True)]},),
                'product_uom': fields.many2one('product.uom', 'Item UOM', required=True,states={'done':[('readonly',True)]},),
                'pr_rq_id': fields.many2one('ireq.m', 'Request Ref',states={'done':[('readonly',True)]},),
                'desc': fields.text('Specification',states={'done':[('readonly',True)]},),
                'state': fields.selection([('draft','Draft'),('done','Done')], 'State', readonly=True),
               }
    _sql_constraints = [
        ('produc_uniq', 'unique(pr_rq_id,product_id)', 'Sorry You Entered Product Two Time You are not Allow to do this.... Please delete The Duplicts!'),
            ]
    _defaults = {
                'state': 'draft',
                'product_qty': 1.0,
                'price_unit': 0.0,
               }
    
    def onchange_product_id(self, cr, uid, ids,product,context=None):
        """ 
        Read product data when selecting a product.

        @return: dict contain product name and uom 
        """
	
        prod = self.pool.get('product.product').browse(cr, uid,product)
        return {'value': { 'name':prod.name,'product_uom':self.pool.get('product.product').browse(cr, uid,product).uom_po_id.id}}
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

