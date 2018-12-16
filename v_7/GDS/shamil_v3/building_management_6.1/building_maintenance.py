# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from osv import fields,osv
import time
import netsvc
from tools.translate import _
import decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments

#----------------------------------------
# Class building maintenance type
#----------------------------------------
class building_maintenance_type(osv.osv):
    _name = "building.maintenance.type"
    _description = 'building maintenance type'
    _columns = {
                'name': fields.char('Name', size=64, required=True ),
                'purchase': fields.boolean('Purchase requisition', help="By checking this field, You can create purchase requisition from the maintenance order."),
               }
    _defaults = {
        'purchase': True,
                }  

#----------------------------------------
# Class building maintenance order
#----------------------------------------
class building_maintenance(osv.osv):
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

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('officer', 'Waiting for admin  affairs section manager to confirm '),
    ('section_manger', 'Waiting for admin  affairs  dept manager to confirm '),
    ('dept_manger', 'Waiting for admin  affairs genral manager to approve'),
    ('execute_maintence', 'Waiting for Maintenece to Execute'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]
    CATEGORY_SELECTION = [
    ('building','Building'),
    ('station','Station'), 
    ]    
    

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the building maintenance "),
    'date' : fields.date('Date',required=True, readonly=True,),
    'maintenance_type':  fields.many2one('building.maintenance.type', 'Maintenance type', required=True, readonly=True,states={'draft':[('readonly',False)]}),
    'department_id':  fields.many2one('hr.department', 'Department', required=True , readonly=True,states={'draft':[('readonly',False)]}),
    'partner_id':fields.many2one('res.partner', 'Partner', readonly=True,states={'draft':[('readonly',False)]}),
    'cost': fields.float('Cost',digits_compute=dp.get_precision('Account'),readonly=True,states={'draft':[('readonly',False)],'execute_maintence':[('readonly',False)]}),    
    'building_id': fields.many2one('building.manager','Building'),
    'station_id': fields.many2one('building.manager','Station'),
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'product_category_id': fields.many2one('product.category', 'Product category' , readonly=True ,states={'draft':[('readonly',False)]}),
    'purchase_lines':fields.one2many('maintenance.purchase.line', 'building_maintenance_id' , 'Material lines' ,readonly=True,states={'draft':[('readonly',False)]}), 
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True  ),    
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'voucher_no': fields.char('Voucher number', size=64,readonly=True),
    'purchase_req_no': fields.char('Purchase Requisition', size=64,readonly=True),
    'notes': fields.text('Notes', size=256,states={'done':[('readonly',True)]} ), 
    'material_state': fields.selection([
            ("purchased", "Purchased"),
            ("2bpurchased", "To Be Purchased"),
            ("none", "Not Applicable")], "Material state",
            select=True, required=True, readonly=True, states={'draft':[('readonly',False)]}),
    'warranty_end_date' : fields.date('End date', readonly=True,help="The end date of maintenance warranty",states={'execute_maintence':[('readonly',False)]}),
        'building_category': fields.selection(CATEGORY_SELECTION,'Category', select=True),
        'line_ids': fields.one2many('building.item', 'building_id', 'Child Buildings'),
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

    """ Workflow Functions"""
     
    def officer(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            #if record.cost <= 0 :
  		#	   raise osv.except_osv(_('Invalid action !'), _('Please insert the correct Cost'))
	    if record.maintenance_type.purchase == True :
            	if not record.purchase_lines:
                	raise osv.except_osv(_('No items!'), _('Please fill the items line first..'))
        self.write(cr, uid, ids, {'state':'officer'})
        return True

    def section_manger(self, cr, uid, ids, context=None):             
        self.write(cr, uid, ids, {'state':'section_manger'})
        return True

    def dept_manger(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'dept_manger'},context=context)
        return True

    def execute_maintence(self,cr,uid,ids,context=None):
	""" Make purchase requisition order from Building Maintenance order
        :return: New created Purchase requisition Order 
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
                	raise osv.except_osv(_('No items!'), _('Please fill the items line first..'))
            	ireq_id = ireq_obj.create(cr,uid,{
                	'name':seq_obj,
                	'ir_ref':record.name,
                	#'pro_ids': [],
                	#'purpose': 'direct',
                    'building_mn_id':record.id, 
                	'cat_id': record.product_category_id.id,    
                	'department_id': record.department_id.id, 
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
        self.write(cr, uid, ids, {'state':'execute_maintence','material_state': purchase or 'none','purchase_req_no':seq_obj or '/'},context=context)
        return True

    def done(self,cr,uid,ids,context=None):
        account_journal_obj = self.pool.get('account.journal')   
        account_obj = self.pool.get('account.account')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        affairs_account_obj = self.pool.get('admin_affairs.account') 
        affairs_model_obj = self.pool.get('admin.affairs.model')

        for record in self.browse(cr, uid, ids):
		notes = _("Building Maitenance order: %s")%(record.name)
        	affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.maintenance')], context=context)
        	affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
        	if not affairs_account_ids:
                	raise osv.except_osv(_('Error'), _("Please enter the building maintenance accounting configuration"))
        	affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
        	accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','building.maintenance')], context=context)
        	account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
        	journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
        	journal_id = journal_ids[0]
        	account_id = account_ids[0]
        	analytic_id = affairs_account.analytic_id
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
        	voucher_number = self.pool.get('account.voucher').browse(cr,uid,voucher_id)


        copy_attachments(self,cr,uid,[record.id],'building.maintenance',voucher_id,'account.voucher', context)
        self.write(cr, uid, ids, {'state':'done','voucher_no':voucher_number.number},context=context)
        return True


    def cancel(self, cr, uid, ids, notes='', context=None):
        # Cancel Car Maintenance order 
        #if not notes:
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Building maintenance order Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        # Reset the Car Maintenance Request 
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            self.write(cr, uid, id, {'state':'draft'})
            wf_service.trg_delete(uid, 'building.maintenance', id, cr)
            wf_service.trg_create(uid, 'building.maintenance', id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        stat = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in stat:
            if t['state'] in ('draft'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a building maintenance order, you must first cancel it,and set to draft.'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True

    def onchange_maintenance_type(self, cr, uid, ids, maintenance_type,context=None):
        """This function change the material_state field,
        if the maintenance type can purchase, you will be able to create purchase requisition from this order
        @param maintenance_type: 'maintenance_type field
        """
        maintenance_type = self.pool.get('building.maintenance.type').browse(cr, uid, maintenance_type, context=context)
        return {'value': { 'material_state':maintenance_type.purchase and '2bpurchased' or 'none',}}
 
 
    def onchange_category(self, cr, uid, ids, product_category_id, purchase_lines, context=None):
        """
        This function Checks the products lines if there is a product it prohibits user to change it,
         and show him a warring message to make sure there are no two products related to different categories.
        ---------------------------------------------------
        :param values : dictionary brings the category value
        :return values and warning  
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
# ----------------------------------------------------
# maintenance purchase line class
# ----------------------------------------------------
class maintenance_purchase_line(osv.osv):
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
        line = self.browse(cr, uid, ids[0], context=context)
        if line.building_maintenance_id.product_category_id and line.product_id.categ_id.id != line.building_maintenance_id.product_category_id.id:
            return False
        return True
    
    def _check_products(self, cr, uid, ids, context=None):
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
    ---------------------------------------------------------------
        :param dict context: 'force_product_uom' key in context override
                             default onchange behaviour to force using the UoM
                             defined on the provided product
        """
        product = self.pool.get('product.product').browse(cr, uid,product)
        return {'value': { 'name':product.name,'product_uom':product.uom_po_id.id}}
       
maintenance_purchase_line()

#inherit purchase requestion to add relation id
class ireq_m(osv.osv):
    _inherit = "ireq.m"
    _columns = {
        'building_mn_id' : fields.many2one('building.maintenance','Request for maintenance No.', readonly=1, help="It referes to maintenance no."),
}
ireq_m()
