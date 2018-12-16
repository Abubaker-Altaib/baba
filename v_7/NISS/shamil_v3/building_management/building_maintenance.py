# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,orm
import time
from openerp import netsvc
from openerp.tools.translate import _
from admin_affairs.copy_attachments import copy_attachments as copy_attachments

class building_maintenance_type(orm.Model):
    """
    To manage building maintenance type"""

    _name = "building.maintenance.type"
    _description = 'building maintenance type'
    _columns = {
                'name': fields.char('Name', size=64, required=True ),
                'purchase': fields.boolean('Purchase requisition', help="By checking this field, You can create purchase requisition from the maintenance order."),
               }
    _defaults = {
        'purchase': True,
                }  


class building_maintenance(orm.Model):
    """
    To manage building maintenance """


    PAYMENT_SELECTION = [
    		('voucher', 'Voucher'),
    		('enrich', 'Enrich'), 
    			]  

    _name = "building.maintenance"
    _description = 'building maintenance order'
  
    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every new building maintenance order Record
        @param vals: record to be created
        @return: return a result that create a new record in the database
          """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'building.maintenance')
        return super(building_maintenance, self).create(cr, user, vals, context) 

    def onchange_building_id(self,cr,uid,ids,building_id,context=None):
       """
       Onchange building fuction to delete building maintenance lines.

       @param building_id: building ID
       @return: Boolean True
       """
       for building in self.browse(cr,uid,ids,context=context):
            if building.maintenance_lines:
               delete = self.pool.get('building.maintenance.line').unlink(cr,uid,[line.id for line in building.maintenance_lines], context=context)
       return True

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the building maintenance "),
    'date' : fields.date('Date',required=True, states={'done': [('readonly', True)]}),
    'maintenance_type':  fields.many2one('building.maintenance.type', 'Maintenance type', states={'confirmed':[('required',True)],'done':[('required',True)],'done': [('readonly', True)]}),
    'partner_id':fields.many2one('res.partner', 'Partner', readonly=True,states={'confirmed':[('readonly',False)]}),
    'department_id':fields.many2one('hr.department', 'Department',readonly=True,required=True,states={'draft':[('readonly',False)]}),
    'cost': fields.float('Cost',readonly=True, required=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),    
    'building_id': fields.many2one('building.building','Building', required=True, states={'done': [('readonly', True)]}),
    'company_id': fields.many2one('res.company','Company',required=True, states={'done': [('readonly', True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True ),    
    'state': fields.selection([('draft', 'Draft'),
                               ('cancel', 'Cancelled'),
                               ('confirmed', 'Confirmed'),
                               ('done', 'Done'),
                                ],'State', readonly=True, select=True),
    'notes': fields.text('Notes', size=256 ), 
    'warranty_end_date' : fields.date('Warranty end date', help="The end date of maintenance warranty", states={'done': [('readonly', True)]}),
    'maintenance_lines':fields.one2many('building.maintenance.line', 'maintenance_id' , 'maintenance Lines', readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)]}),
    'product_category_id': fields.many2one('product.category', 'Product category' , readonly=True ,states={'draft':[('readonly',False)]}),
    'purchase_lines':fields.one2many('maintenance.purchase.line', 'building_maintenance_id' , 'Material lines' ,readonly=True,states={'draft':[('readonly',False)]}), 
    'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
    'purchase_req_no': fields.char('Purchase Requisition', size=64,readonly=True),
    'material_state': fields.selection([
            ("purchased", "Purchased"),
            ("2bpurchased", "To Be Purchased"),
            ("none", "Not Applicable")], "Material state",
            select=True, required=True, readonly=True, states={'draft':[('readonly',False)]}),
    'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',readonly=True,states={'confirmed':[('readonly',False)]}, select=True),
    'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'confirmed':[('readonly',False)]}),
}

    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'building maintenance reference must be unique !'),
        ]
    
    _defaults = {
                'name':'/',
                'date':time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'building.maintenance', context=c),
                'state': 'draft',
                'user_id': lambda self, cr, uid, context: uid,
                'material_state':'none',
		'purchase_req_no':'/'
		
                }
    
    _sql_constraints = [
        ('qty_check', 'check(qty > 0)', 'Item quantity must be bigger than zero!'),
        ]
 
    def _check_cost(self, cr, uid, ids, context=None):
        """
        Constrain function to check cost.

        @retuen: Boolean True or False
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.state in ['confirmed','done'] and order.cost <= 0:
                return False
        return True
    
    _constraints = [
        (_check_cost, 'Alert! , Cost must be greater than zero', ['cost']),
    ]


     
    def confirmed(self, cr, uid, ids, context=None):
        """ 
        Workflow function changes state to confirmed and check
        maintenance order lines.

        @return: Boolean True
        """
        for order in self.browse(cr, uid, ids, context=context):
            if not order.maintenance_lines:
                raise orm.except_orm(_('Error !'), _('You can not confirm this order without maintenance lines.'))
	    if order.maintenance_type.purchase == True and not order.purchase_lines:
                raise orm.except_orm(_('No items!'), _('Please fill the items line first..'))
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True


    def is_roof(self, cr, uid, ids, context=None):  
        """
           Workflow method that checks wether the amount of maintenance request has a financial roof  or not .
           @return: Boolean True Or False
        """
        affairs_model_obj = self.pool.get('admin.affairs.model')
        payment_roof_obj = self.pool.get('admin.affaris.payment.roof')            
        for record in self.browse(cr, uid, ids):
            affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.maintenance')], context=context)
            if not affairs_model_ids :
                return True
            if affairs_model_ids :
                payment_roof_ids = payment_roof_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0]),('name','=','service')], context=context)
                if not payment_roof_ids : 
                    return True
                affairs_payment = payment_roof_obj.browse(cr, uid, payment_roof_ids[0], context=context)
                if record.cost > affairs_payment.cost_to :
                    return False
        return True

    def done(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes state to done and create account
        voucher.

        @return: Boolean True
        """
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model')
        payment_enrich_obj = self.pool.get('payment.enrich')
        payment_enrich_lines_obj = self.pool.get('payment.enrich.lines') 
        for record in self.browse(cr, uid, ids):
            if record.payment_selection == 'enrich':
				    paid = (record.enrich_category.paid_amount + record.cost)
				    residual = (record.enrich_category.residual_amount - record.cost)
				    #enrich_payment_id = cr.execute("""update payment_enrich set paid_amount=%s , residual_amount=%s where id =%s""",(paid,residual,record.enrich_category.id))
				    #details = smart_str('Service Request No:'+record.name+'\n'+record.service_category.name)
				    details = 'Building Maitenance No:'+record.name
				    enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					            'enrich_id':record.enrich_category.id,
                        		'cost': record.cost,
					            'date':record.date,
                        		'name':details,
					            'department_id':record.department_id.id,
                            				}, context=context)
            elif record.payment_selection != 'enrich' :
                notes = _("Building Maitenance order: %s")%(record.name)
                affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.maintenance')], context=context)
                affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
                if not affairs_account_ids:
                	    raise orm.except_orm(_('Error'), _("Please enter the building maintenance accounting configuration"))
                affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
                accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.maintenance')], context=context)
                account_ids = account_obj.search(cr, uid, [('company_id','=',record.building_id.company_id.id),('code','=',str(affairs_account.code))], context=context)
                journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.building_id.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
                journal_id = affairs_account.journal_id.id
                account_id = affairs_account.account_id.id
                analytic_id = affairs_account.analytic_id.id
		# Creating Voucher / Ratitication
                voucher_id = voucher_obj.create(cr, uid, {
                                        'amount': record.cost,
                                        'type': 'ratification',
                                        'date': time.strftime('%Y-%m-%d'),
                                        'partner_id': record.partner_id.id, 
                                        'journal_id': journal_id,
                                        'department_id': record.department_id.id,
                                        'state': 'draft',
					                    'note':record.name,
					                    'narration':notes ,
                                 	    'company_id':record.company_id.id,
                                         })

            	# Creating Voucher / Ratitication Lines
                vocher_line_id = voucher_line_obj.create(cr, uid, {
                                        'amount': record.cost,
					                    'account_id':account_id,
					                    'account_analytic_id':analytic_id ,
                                        'voucher_id': voucher_id,
                                        'type': 'dr',
                                        'name':'Building Maintenace order: ' + record.name,
                                         })
                #voucher_number = self.pool.get('account.voucher').browse(cr,uid,voucher_id)
                #################### update workflow state###############
                voucher_state = 'draft'
                if record.company_id.affairs_voucher_state : 
                    voucher_state = record.company_id.affairs_voucher_state 
                if voucher_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
                    voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
                copy_attachments(self,cr,uid,[record.id],'building.maintenance',voucher_id,'account.voucher', context)
                self.write(cr, uid, ids, {'voucher_no':voucher_id},context=context)
        self.write(cr, uid, ids, {'state':'done'},context=context)
        return True

    def execute_maintence(self,cr,uid,ids,context=None):
        """ Make purchase requisition order from Building Maintenance order.
            @return: Boolean True 
        """
        purchase = ''
	seq_obj = ''
        uom_obj = self.pool.get('product.uom')
        ireq_obj = self.pool.get('ireq.m')
        ireq_line_obj = self.pool.get('ireq.products')
        for record in self.browse(cr, uid, ids, context=context):
	    if record.maintenance_type.purchase == True :
		purchase = 'purchased'
                seq_obj = self.pool.get('ir.sequence').get(cr, uid, 'ireq.m')
            	if not record.purchase_lines:
                	raise orm.except_orm(_('No items!'), _('Please fill the items line first..'))
            	ireq_id = ireq_obj.create(cr,uid,{
                	'name':seq_obj,
                	'ir_ref':record.name,
                	#'pro_ids': [],
                	#'purpose': 'direct',
                    'building_mn_id':record.id, 
                	'cat_id': record.product_category_id.id,    
                	#'department_id': record.department_id.id, 
                	'ir_date':time.strftime('%Y-%m-%d'), 
                	'user': uid,                                  
                	'company_id': record.company_id.id,                                  
                                           })
            	for line in record.purchase_lines:
                	ireq_line_obj.create(cr, uid, {
                                 'name': line.name, 
                                 'product_id': line.product_id.id, 
                                 'product_qty': line.product_qty, 
                                 'product_uom':line.product_uom.id, 
                                 'pr_rq_id':ireq_id, 
                                 'desc': line.desc, 
                                 },context=context) 
        self.write(cr, uid, ids, {'material_state': purchase or 'none','purchase_req_no':seq_obj or '/'},context=context)
        return True

    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes state to cancel and writes note.

	    @param notes: contains information of cancelling operation.
        @return: Boolean True
        """
        notes = ""
        user_name = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Building maintenance order Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ user_name
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes state to Draft and reset the workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for building_id in ids:
            self.write(cr, uid, building_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'building.maintenance', building_id, cr)            
            wf_service.trg_create(uid, 'building.maintenance', building_id, cr)
        return True

    def copy(self, cr, uid, ids, default=None, context=None):
        """
        Override copy function to edit default value.

        @param default : default vals dict 
        @return: id of the newly created record  
        """
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, ids, context=context)
        if ('name' not in default) or (picking_obj.name == '/'):
            seq_obj_name = 'building.maintenance'
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        return super(building_maintenance, self).copy(cr, uid, ids, default, context)

    def unlink(self, cr, uid, ids, context=None):
        """ 
        Ovrride to add constain on deleting the records. 

        @return: super unlink method
        """
        if context is None:
            context = {}
        for maintenance in self.browse(cr, uid, ids, context=context):
            if maintenance.state == 'done':
                raise orm.except_orm(_('Error!'), _('You cannot remove the maintenance order which is in done state!'))
       
        return super(building_maintenance, self).unlink(cr, uid, ids, context=context)

    def onchange_maintenance_type(self, cr, uid, ids, maintenance_type,context=None):
        """
        On chnage maintenance_type function to change the material_state field, if the maintenance 
        type can purchase, you will be able to create purchase requisition from this order.

        @param maintenance_type: 'maintenance_type field
        @return: Dictionary of 
        """
        maintenance_type = self.pool.get('building.maintenance.type').browse(cr, uid, maintenance_type, context=context)
        return {'value': { 'material_state':maintenance_type.purchase and '2bpurchased' or 'none',}}

    def onchange_category(self, cr, uid, ids, product_category_id, purchase_lines, context=None):
        """
        This function Checks the products lines if there is a product it prohibits user to change it,
        and show him a warring message to make sure there are no two products related to different 
        categories.

        @param product_category_id: category ID
        @param purchase_lines: list of product line IDs
        @param values : dictionary brings the category value
        @return: Dictionary of values and warning  
        """
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


class building_maintenance_line(orm.Model):
    """
    To manage building maintenance line"""

    _name = "building.maintenance.line"
    _description = 'building maintenance line'

    def onchange_qty(self,cr,uid,ids,building_id,item_id,context=None):
       """ 
        On change product quantity function to add domain.

        @param building_id: building ID
        @param item_id: product ID
        @return: Dictionary of domain 
       """
       domain= {}
       if building_id and not item_id:
            building = self.pool.get('building.building').browse(cr,uid,building_id,context=context)
            domain={'item_id':[('id','in',[item.item_id.id for item in building.item_ids])]}
       return {'domain': domain}

    def check_qty(self, cr, uid,ids,context=None):
        """ 
        To check maintenance product quantity.

        @return: Boolean True 
        """
        for line in self.browse(cr,uid,ids,context=context):
           if line.maintenance_id.building_id:
              item_qty = sum(item.qty for item in line.maintenance_id.building_id.item_ids if item.item_id.id == line.item_id.id)
              if line.qty > item_qty:
                 raise orm.except_orm(_('Error !'),_('sorry you can not exceed item quantity of the selected building %s' % (item_qty)))
        return True
           
    _columns = {
                'name': fields.char('Description', size=256),
                'qty': fields.float('Quantity',digits=(16,2), required=True),        
                'item_id': fields.many2one('item.item', 'Item', required=True),
                'maintenance_id': fields.many2one('building.maintenance', 'Maintenance order', required=True),
               }
    _defaults = {
                'qty':1,       
                }
    _sql_constraints = [
        ('qty_check', 'check(qty > 0)', 'Item quantity must be bigger than zero!'),
        ]
    _constraints = [
        (check_qty, 'sorry you can not exceed item quantity of the selected building', ['qty']),
                    ]

    def onchange_item_id(self, cr, uid, ids, item_id ):
        """ 
        On change product function to read product data when selecting a product.
         
        @param item_id: product ID
        @return: Dictionary contain product 
        """
        if not item_id:
            return {'value': {'name': '',}}
        item_name = self.pool.get('item.item').name_get(cr, uid, [item_id ] )[0][1]
        result = {'name':item_name,}
        return {'value': result}


class maintenance_purchase_line(orm.Model):
    """
    To manage maintenance purchase line"""

    _name = "maintenance.purchase.line"
    _description = 'maintenance purchase line'
    _columns = {
                'name': fields.char('Name', size=64, required=True),
                'product_id': fields.many2one('product.product','Product', required=True, domain=[('type', '<>', 'service')]),  
                'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
                'product_uom': fields.many2one('product.uom', 'Item UOM', required=True),
                'building_maintenance_id': fields.many2one('building.maintenance', 'Building maintenance', ondelete='cascade',),
                'desc': fields.text('Specification',states={'done':[('readonly',True)]},),
               }
    
    _defaults = {
                'product_qty': 1.0,
               }
     
    _sql_constraints = [
        ('produc_uniq', 'unique(building_maintenance_id,product_id)', 'Sorry you entered product two time, Please delete The duplicate!'),
        ('produc_qty_positive', 'check(product_qty > 0)', 'The product quantity must be greater than 0.'),    
            ]
    def _check_product_categ(self, cr, uid, ids, context=None):
        """
        Constraints function to check product category

        @return: Boolean True or False
        """
        line = self.browse(cr, uid, ids[0], context=context)
        if line.building_maintenance_id.product_category_id and line.product_id.categ_id.id != line.building_maintenance_id.product_category_id.id:
            return False
        return True
    
    def _check_products(self, cr, uid, ids, context=None):
        """
        Constraints function to check product 

        @return: Boolean True or False
        """
        line = self.browse(cr, uid, ids[0], context=context)
        prod = self.search(cr, uid, [ ('product_id', '=', line.product_id.id), ('building_maintenance_id', '=', line.building_maintenance_id.id)])
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
        onchange handler of product_id.
       
        @param product: product ID 
        @param dict context: 'force_product_uom' key in context override
                             default onchange behaviour to force using the UoM
                             defined on the provided product
        @return: Dictionary of product name and uom
        """
        product = self.pool.get('product.product').browse(cr, uid,product)
        return {'value': { 'name':product.name,'product_uom':product.uom_po_id.id}}


class ireq_m(orm.Model):
    """
    To add field to purchse initial requisition """

    _inherit = "ireq.m"
    _columns = {
        'building_mn_id' : fields.many2one('building.maintenance','Request for maintenance No.', readonly=1, help="It referes to maintenance no."),
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    

