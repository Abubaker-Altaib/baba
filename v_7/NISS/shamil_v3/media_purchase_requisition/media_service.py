# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv,orm
import time
from tools.translate import _
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar


class media_order(osv.osv):
    """
    To Manage media service order and its operation """

    _inherit= "media.order"
    _columns={
        'product_category_id': fields.many2one('product.category', 'Product category'),
        'purchase_lines':fields.one2many('media.purchase.line', 'media_order_id' , 'Media purchase lines'), 
        'ireq_no': fields.char('Requisition number', size=64,readonly=True),
        'purchase_state': fields.selection([
            ("purchased", "Purchased"),
            ("2bpurchased", "To Be Purchased"),
            ("none", "Not Applicable")], "Purchase state",
            select=True, required=True, readonly=True),
    }
    _defaults = {
                'purchase_state': 'none',
                }
    
    def done(self, cr, uid,ids, context={}):
        """
        Workflow function to change media service order state to done,
        check media service order accounts and create account voucher 
        with meida service order total cost.
 
        @return: True
        """
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account')
        affairs_model_obj = self.pool.get('admin.affairs.model')
        if self.browse(cr,uid,ids[0],context).execution_type == 'internal':
            self.write(cr, uid, ids, {'purchase_state':'2bpurchased'},context=context)
        for record in self.browse(cr,uid,ids,context=context):
		if record.execution_type == 'external':
	   		if record.total_cost < 1 : 
				raise osv.except_osv(_('Error'), _("Please enter the Right Cost "))
			#Account Configuartion for all media order
           		affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','media.order')], context=context)
           		affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
           		if not affairs_account_ids:
                		raise osv.except_osv(_('Error'), _("Please enter Media Order accounting configuration"))
           		affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
           		accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','media.order')], context=context)
           		account_ids = account_obj.search(cr, uid, [('company_id','=',record.category_id.company_id.id),('code','=',str(affairs_account.code))], context=context)
           		journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.category_id.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
           		journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
           		account_id = account_ids and account_ids[0] or affairs_account.account_id.id
           		analytic_id = affairs_account.analytic_id
			#Define Department & company & analytic account for normal case
			dept = record.department_id.id
			analytic_account = record.category_id.analytic_id
			company = record.company_id.id
			#Account Configuartion per media order category 
        		category_accounts_ids = account_obj.search(cr, uid, [('company_id','=',record.category_id.company_id.id),('code','=',str(record.category_id.code))], context=context)
			if not category_accounts_ids : 
                		raise osv.except_osv(_('Error'), _("Please enter Media category accounting configuration"))
			cat_account_id = category_accounts_ids[0]
			if record.category_id.company_id.code == "HQ" and  record.company_id.code != "HQ":
				print "True we here"
				dept = record.category_id.department_id.id 
				analytic_account = record.category_id.department_id.analytic_account_id.id
				company = record.category_id.company_id.id
        # Creating Voucher 
           		voucher_id = voucher_obj.create(cr, uid, {
                        	'amount': record.total_cost,
                        	'type': 'ratification',
                        	'date': time.strftime('%Y-%m-%d'),
                        	'partner_id': record.partner_id.id, 
                        	'department_id': dept ,
                        	'state': 'draft',
				'company_id' : company ,
                        	'journal_id':journal_id , 
                        	'narration': 'Media order no :'+record.name,
                        	'amount_in_word':amount_to_text_ar(record.total_cost),
                            }, context={})
           		voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context) 
        #Creating voucher lines
           		voucher_line_dict={
                     		'name': record.name,
                     		'voucher_id':voucher_id,
		     		'account_id':cat_account_id ,
                     		'account_analytic_id':analytic_account,
                     		'amount':record.total_cost,
                     		'type':'dr',
                               }
           		voucher_line=voucher_line_obj.create(cr,uid,voucher_line_dict)
       	   		copy_attachments(self,cr,uid,[record.id],'media.order',voucher_id,'account.voucher', context)        
           		self.write(cr, uid, ids, {'voucher_no':voucher_number.number},context=context)
        self.changes_state(cr, uid, ids,{'state':'done'},context=context)
        return True
    
    def action_create_purchase(self, cr, uid, ids, context={}):
        """ 
        Make purchase requisition order from media service order.

        @return: New created Purchase requisition Order 
        """
        res = {}
        uom_obj = self.pool.get('product.uom')
        ireq_obj = self.pool.get('ireq.m')
        ireq_line_obj = self.pool.get('ireq.products')
        seq_obj = self.pool.get('ir.sequence').get(cr, uid, 'ireq.m')
        for media_order in self.browse(cr, uid, ids, context=context):
            if not media_order.purchase_lines:
                raise osv.except_osv(_('No items!'), _('Please fill the items line first..'))
            ireq_id = ireq_obj.create(cr,uid,{
                'name':seq_obj,
                'ir_ref':media_order.name,
                #'pro_ids': [],
                #'purpose': 'direct',
                'cat_id': media_order.product_category_id.id,    
                'department_id': media_order.department_id.id, 
                'ir_date':time.strftime('%Y-%m-%d'), 
                'user': uid,                                  
                'company_id': media_order.company_id.id,                                  
                                           })
            for line in media_order.purchase_lines:
                ireq_line_obj.create(cr, uid, {
                                 'name': line.name, 
                                 'product_id': line.product_id.id, 
                                 'product_qty': line.product_qty, 
                                 'product_uom':line.product_uom.id, 
                                 'pr_rq_id':ireq_id, 
                                 'desc': line.desc, 
                                 },context=context) 
            self.write(cr, uid, [media_order.id], {'purchase_state':'purchased','ireq_no':seq_obj},context=context)
        return True

    def onchange_category_check_purchase_line(self, cr, uid, ids, product_category_id, purchase_lines, context=None):
        """
        To checks the products lines if there is a product it prohibits user to change it,
        and show warring message to make sure there are no two products related to different categories.

        @param values : dictionary brings the category value
        @return: values and warning  
        """
        res={}
        if purchase_lines:
            for pro in purchase_lines:
                if (pro[2] and pro[2]['product_id'] != False):
                    product_id = pro[2]['product_id'] # Take the first product in products lines
                    product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                     
                    values = {'product_category_id': product_category_id} 
                    values.update({'product_category_id': product.categ_id.id}) # Update the category value by the old one
                    if (product_category_id != product.categ_id):
                        warning={'title': _('Warning'), 'message': _('The selected cateogry is not related to ordered products, The ordered  product have this category: %s') % product.categ_id.name}
                        return {'value':values,'warning':warning}
        return {}        


class media_purchase_line(osv.osv):
    """
    To manage media purchase line """

    _name = "media.purchase.line"
    _description = 'Media purchase line'
    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'product_id': fields.many2one('product.product','Product', required=True, domain=[('type', '<>', 'service')]),  
                'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
                'product_uom': fields.many2one('product.uom', 'Item UOM', required=True),
                'media_order_id': fields.many2one('media.order', 'Media order Ref', ondelete='cascade',),
                'desc': fields.text('Specification',states={'done':[('readonly',True)]},),
               }
    
    _defaults = {
                'product_qty': 1.0,
               }
     
    _sql_constraints = [
        ('produc_uniq', 'unique(media_order_id,product_id)', 'Sorry You Entered Product Two Time, Please delete The duplicate!'),
        ('produc_qty_positive', 'check(product_qty > 0)', 'The product qty must be greater than 0.'),    
            ]
    def _check_product_categ(self, cr, uid, ids, context=None):
        """
        Constraint function to check products category to make sure that they 
        belong to the same category.

        @return: Boolean True or False
        """
        line = self.browse(cr, uid, ids[0], context=context)
        if line.media_order_id.product_category_id and line.product_id.categ_id.id != line.media_order_id.product_category_id.id:
            return False
        return True
    
    def _check_products(self, cr, uid, ids, context=None):
        """
        Constraint function to check products

        @return: Boolean True or False
        """
        line = self.browse(cr, uid, ids[0], context=context)
        prod = self.search(cr, uid, [ ('product_id', '=', line.product_id.id), ('media_order_id', '=', line.media_order_id.id)])
        if len(prod) > 1:
            return False
        return True
    
    _constraints = [
        (_check_product_categ,
          'All products must be in the same Category. ', 
          ['product_id']),
        (_check_products,
          'product must be unique ',
           ['product_id']),]
    _defaults = {
                'product_qty': 1.0,
               }
    
    def onchange_product_id(self, cr, uid, ids,product,context=None):
        """
        On change product function to read product name and uom.

        @param product: product ID
        @param dict context: 'force_product_uom' key in context override
                             default onchange behaviour to force using the UoM
                             defined on the provided product
        @return: Dictionary of product name and uom
        """
        product = self.pool.get('product.product').browse(cr, uid,product)
        return {'value': { 'name':product.name,'product_uom':product.uom_po_id.id}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:      
