# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##########################################################################

from openerp.osv import fields,osv
import time
import netsvc
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

#----------------------------------------
# Class car maintenance request
#----------------------------------------
class car_maintenance_request(osv.Model):
    _name = "car.maintenance.request"
    _description = 'Car Maintenance Request'

    
    def create(self, cr, user, vals, context=None):
        """
           Method that creates a new sequence entry as a name for each new car maintenance request.
           @param vals: Dictionary of the entered data
           @return: Super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'car.maintenance.request')
        return super(car_maintenance_request, self).create(cr, user, vals, context) 

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):

        """ 
           Functional field function that calculates the total cost of all faults.
           @param field_name: list contains name of fields that call this method
           @param arg: extra arguement
           @return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in record.faults:
                val += line.price_subtotal
            res[record.id] = val 
        return res   
    
    MAINTENANCE_TYPE_SELECTION = [
    ('regular', 'Regular'),
    ('emergency', 'Emergency'),
    ('other', 'Other'),
 ]  
    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed_d', 'Waiting for requesting party manager To approve'),
    ('confirmed_gd', 'Waiting for department manager to confirm '),
    ('approved_of', 'Waiting for admin affairs Service Manager'),
#    ('approved_of2', 'Waiting for admin affairs Service Manager'),
    ('officer_of', 'Waiting for admin affairs officer'),
    ('confirmed_gm', 'Waiting for admin  affairs  general manager to confirm'),
    ('approved', 'Waiting for admin  affairs manager to approve'),
    ('execute', 'Waiting for maintenance engineer to execute '),   
    ('check', 'Waiting for the completion of maintenance'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]

    PAYMENT_SELECTION = [
    		('voucher', 'Voucher'),
    		('enrich', 'Enrich'), 
    			]    

    _order = "name desc"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the car maintenance "),
    'date' : fields.date('Request Date',required=True, readonly=True,),
    #'department_id':  fields.related('car_id', 'department_id', type='many2one', relation='hr.department',store=True, string='Department',readonly=True,states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_gd':[('readonly',False)],}),
    'department_id':fields.many2one('hr.department', 'Department', states={'approved':[('readonly',True)],'approved_of':[('readonly',True)],'execute':[('readonly',True)], 'check':[('readonly',True)], 'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'partner_id':fields.many2one('res.partner', 'Partner'),
      
    'car_id':  fields.many2one('fleet.vehicle', 'Car Name', required=True, readonly=True,states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_gd':[('readonly',False)],}),
#    'category_id':  fields.many2one('maintenance.category', 'Car Type'),
    'car_number': fields.related('car_id', 'license_plate', type='char', relation='fleet.vehicle', string='Car Number', readonly=True),
    'driver':  fields.related('car_id','employee_id', type='many2one' , relation='hr.employee' ,string='Driver',required=False , readonly=True),
    'maintenance_date':fields.date('Maintenance Date',required=True,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'base_mileage':fields.related('car_id', 'cmil', type='float', relation='fleet.vehicle', string='Current Mileage', readonly=True,help="The last recorded mileage"),
    'next_mileage':fields.float('Next Mileage',digits=(16,3),help="The next mileage", readonly=True,states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_gd':[('readonly',False)],}),
    'maintenance_type': fields.selection(MAINTENANCE_TYPE_SELECTION, 'Maintenance Type', required=True, readonly=True,states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_gd':[('readonly',False)],}), 
    'notes': fields.text('Notes', size=256 , readonly=True,states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'confirmed_gd':[('readonly',False)],}), 
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'faults':fields.one2many('car.faults', 'fault_id' , 'Car Faults', readonly=True,states={'draft':[('readonly',False)],'execute':[('readonly',False)],'confirmed_d':[('readonly',False)],'check':[('readonly',False)],'officer_of':[('readonly',False)],}),
    'total_amount': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Amount' , store = True),    
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True  ),    
    'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
    'allowance_computed': fields.boolean('Allowance Computed' ,),
    'next_maintenance_date':fields.date('Next Maintenance Date',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'start_maintenance_date':fields.date('Start Maintenance Date',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'end_maintenance_date':fields.date('End Maintenance Date',states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',readonly=True,states={'check':[('readonly',False)]}, select=True),
    'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'check':[('readonly',False)]}),
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'car maintenance reference must be unique !'),
        ]
    
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': lambda *a: time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'car.maintenance.request', context=c),
                'state': 'draft',
                'user_id': lambda self, cr, uid, context: uid,
                'allowance_computed' : lambda *a: 0,
                
                }

    """ Workflow Functions"""
     
    def confirmed_d(self, cr, uid, ids, context=None):
        """
           Workflow method that changes the state to 'confirmed_d'.
           @return: Boolean True
        """  
        #for record in self.browse(cr, uid, ids):
            #if not record.faults:
                #raise orm.except_orm(_('No Faults  !'), _('Please Fault Item Details ..'))                         
        self.write(cr, uid, ids, {'state':'confirmed_d'})
        return True

    def confirmed_gd(self, cr, uid, ids, context=None): 
        """
           Workflow method that changes the state to 'confirmed_gd'.
           @return: Boolean True
        """             
        self.write(cr, uid, ids, {'state':'confirmed_gd'})
        return True
    
    def is_emergency(self, cr, uid, ids, context=None):   
        """
           Workflow method that checks wether the maintenance request is for emergency or not.
           @return: Boolean True Or False
        """           
        for record in self.browse(cr, uid, ids):
            if record.maintenance_type != "emergency":
                return False
        return True

    def is_roof(self, cr, uid, ids, context=None):  
        """
           Workflow method that checks wether the amount of maintenance request has a financial roof  or not .
           @return: Boolean True Or False
        """
        affairs_model_obj = self.pool.get('admin.affairs.model')
        payment_roof_obj = self.pool.get('admin.affaris.payment.roof')            
        for record in self.browse(cr, uid, ids):
            if record.maintenance_type == "emergency":
        	affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','car.maintenance')], context=context)
		if not affairs_model_ids : 
		        return True	
        	payment_roof_ids = payment_roof_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0]),('name','=','service')], context=context)
        	affairs_payment = payment_roof_obj.browse(cr, uid, payment_roof_ids[0], context=context)
                if record.total_amount > affairs_payment.cost_to :
                	return False
        return True

    def is_regular(self, cr, uid, ids, context=None):  
        """
           Workflow method that checks wether the maintenance type is regular or not .
           @return: Boolean True Or False
        """            
        for record in self.browse(cr, uid, ids):
            if record.maintenance_type != "regular":
                return False
        return True
    
    def confirmed_gm(self,cr,uid,ids,context=None):
        """
           Workflow method that changes the state to 'confirmed_gm'.
           @return: Boolean True 
        """            
        self.write(cr, uid, ids, {'state':'confirmed_gm'},context=context)
        return True
    
    def approved(self,cr,uid,ids,context=None):
        """
           Workflow method that changes the state to 'approved'.
           @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'approved'},context=context)
        return True

    def approved_of(self,cr,uid,ids,context=None):
        """
           Workflow method that changes the state to 'approved_of'.
           @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'approved_of'},context=context)
        return True

    """def approved_of2(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'approved_of2'},context=context)
        return True"""

    def officer_of(self,cr,uid,ids,context=None):
        """
           Workflow method that changes the state to 'officer_of'.
           @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'officer_of'},context=context)
        return True

    def execute(self,cr,uid,ids,context=None):     
        """
           Workflow method that changes the state to 'execute'.
           @return: Boolean True 
        """           
        self.write(cr, uid, ids, {'state':'execute'},context=context)      
        return True

    def check(self,cr,uid,ids,context=None):
        """
           Workflow method that changes the state to 'check' and checks the Faults have been entered and that it has prices.
           @return: Boolean True 
        """
        payment_enrich_obj = self.pool.get('payment.enrich')
        payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')   
        for record in self.browse(cr, uid, ids):
            if not record.faults:
                raise osv.except_osv(_('No Faults  !'), _('Please Fault Item Details ..'))
	    if record.payment_selection == 'enrich':
				paid = (record.enrich_category.paid_amount + record.total_amount)
				residual = (record.enrich_category.residual_amount - record.total_amount)
				#enrich_payment_id = cr.execute("""update payment_enrich set paid_amount=%s , residual_amount=%s where id =%s""",(paid,residual,record.enrich_category.id))
				#details = smart_str('Service Request No:'+record.name+'\n'+record.service_category.name)
				details = 'Car Maintenance No:'+record.name
				enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					'enrich_id':record.enrich_category.id,
                        		'cost': record.total_amount,
					'date':record.date,
                        		'name':details,
					'department_id':record.department_id.id,

                            				}, context=context)
				self.write(cr, uid, ids, {'allowance_computed':True},context=context)
	    elif record.payment_selection == 'voucher':
				self.write(cr, uid, ids, {'allowance_computed':False},context=context) 
            for fault in record.faults:
                fault.write({'added_by_supplier':False}) 
                if fault.price_unit == 0.0:
                    raise osv.except_osv(_('No Price !'), _('Please make sure you enter prices for all items'))
        self.write(cr, uid, ids, {'state':'check'},context=context)                                 
        return True    

    def done(self,cr,uid,ids,context=None):
        """
           Workflow method that changes the state to 'done' and updates next_mileage of fleet vehicle.
           @return: Boolean True 
        """    
        for record in self.browse(cr, uid, ids):
            
            self.pool.get('fleet.vehicle').write(cr, uid,[record.car_id.id] ,{'cmil':record.next_mileage})        
        self.write(cr, uid, ids, {'state':'done'},context=context) 
        return True

    def modify_maintenance_request(self,cr,uid,ids,context=None):
        """
           Method that deletes the old Maintenance request's workflow and creat a new one in the 'check' state.
           @return: Boolean True 
        """  
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            wf_service.trg_delete(uid, 'car.maintenance.request', s_id, cr)            
            wf_service.trg_create(uid, 'car.maintenance.request', s_id, cr)
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'draft', cr) 
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'confirmed_d', cr)
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'confirmed_gd', cr) 
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'approved_of', cr) 
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'officer_of', cr) 
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'confirmed_gm', cr)
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'approved', cr)  
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'execute', cr)  
            res = wf_service.trg_validate(uid, 'car.maintenance.request',s_id, 'check', cr)    
            #self.write(cr, uid, s_id, {'state':'dept_confirm'})
        return True


    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """
           Method changes state of To 'cancel' and write notes about the cancellation.
	   @param notes: contains information of who & when cancelling the car maintenance request.
           @return: Boolean True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Car Maintenance Request Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
           Method resets the Car Maintenance Request  record to 'draft' , deletes the old workflow and creates a new one.
           @return: Boolean True       
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'car.maintenance.request', s_id, cr)            
            wf_service.trg_create(uid, 'car.maintenance.request', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
           Method that overwrites unlink method to prevent the the deletion of  Car Maintenance Request record not in 'draft' state.
           @return: Super unlink method       
        """
        stat = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in stat:
            if t['state'] in ('draft'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a car maintenance request, \
							you must first cancel it,and set to draft.'))
        return super(car_maintenance_request, self).unlink(self, cr, uid, unlink_ids, context=context)

    def create_financial_voucher(self,cr,uid,ids,context=None):
        """
           Method that transfers the cost of maintenance to the voucher and creates a ratification for car's maintenance request .
           @return: Dictionary of values
        """
        names = ''
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        for request in self.browse(cr, uid, ids, context=context):
            for pro in request.faults:
                    names += pro.name+'\n'
	    notes = _("Car Maintenance : %s \nMaintenance Type: %s.\nSpare Part: %s.")%(request.name,request.maintenance_type , names)
    	    config_id = self.pool.get('admin_affairs.account').search(cr, uid, [('company_id','=',request.company_id.id)], context=context)
	    if not config_id :
  			raise osv.except_osv(_('Invalid action !'), _('Please insert the Company Configruation Account For Car Maintenance'))
	    account_config = self.pool.get('admin_affairs.account').browse(cr,uid,config_id[0])
            # Creating Voucher / Ratitication
            voucher_id = voucher_obj.create(cr, uid, {
                 'amount': request.total_amount,
                 'type': 'ratification',
                 'date': time.strftime('%Y-%m-%d'),
                 'partner_id': request.partner_id.id, 
                 'department_id': request.department_id.id,
                 'journal_id': account_config.maintenance_jorunal_id.id,
                 'state': 'draft',
                 'notes': request.notes,
                 'narration': notes,
                                    }, context=context)
            voucher_line_dict = {
                             'voucher_id':voucher_id,
			     'account_id':account_config.maintenance_account_id.id,
			     'account_analytic_id':account_config.maintenance_analytic_id.id or 		request.department_id.analytic_account_id.id ,
                             'amount':request.total_amount,
                             'type':'dr',
                             'name':request.department_id.name,
                               }
            voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
            #################### update workflow state###############
            voucher_state = 'draft'
            if record.company_id.affairs_voucher_state : 
                voucher_state = record.company_id.affairs_voucher_state 
            if voucher_id:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
                voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
            # Selecting Voucher Number / Refernece 
            #voucher_number = voucher_obj.browse(cr,uid,voucher_id,context=context).number
            self.write(cr, uid, request.id,{'voucher_no':voucher_id},context=context)
        return True

###################class Faults 

class car_faults(osv.Model):    
    _name = "car.faults"
    _description = 'Type of Fault'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        """ 
           Functional field function that calculates the cost of each car fault line ( quantity*price ).
           @param field_name: List contains name of fields that call this method
           @param arg: Extra arguement
           @return: Dictionary of values
        """
        context.update({'ids':ids})
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * line.product_qty or 0.0
            res[line.id] = price
        return res
       
    _columns = {
                'name': fields.char('Name', size=64 ,select=True,),
                'product_id': fields.many2one('product.product','Item',required=True,readonly=True,states={'draft':[('readonly',False)],'execute':[('readonly',False)],'check':[('readonly',False)],}),
                'product_qty': fields.float('Item Quantity', required=True, digits=(16,2),readonly=True,states={'draft':[('readonly',False)],'execute':[('readonly',False)],'check':[('readonly',False)],}),
                'product_uom': fields.many2one('product.uom', 'Item UOM',readonly=True,states={'draft':[('readonly',False)],'execute':[('readonly',False)],'check':[('readonly',False)],}),
                'fault_id': fields.many2one('car.maintenance.request', 'car maintenance request', ondelete='cascade'),
                'price_unit': fields.float('Unit Price', digits_compute=dp.get_precision('Account'),readonly=True ,store = True,states={'draft':[('readonly',False)],'confirmed_d':[('readonly',False)],'execute':[('readonly',False)],'check':[('readonly',False)],'officer_of':[('readonly',False)],}),   
                'price_subtotal': fields.function(_amount_line, method=True, string='Sub total',digits_compute=dp.get_precision('Account'),readonly=True, store = True),
                'added_by_supplier': fields.boolean('Added by supplier', help="By checking the Added by supplier field, you determine this product as adding by supplier",readonly=True,),               
                'state':fields.related('fault_id', 'state', type='char', relation='car.maintenance.request', string=' State', readonly=True,),
                
                            
                'notes': fields.text('Notes', size=256 ,),

               }
    _sql_constraints = [
        ('produc_uniq', 'unique(fuel_id,product_id)', 'Fault must be unique!'),
            ] 
     
    _defaults = {
                 'product_qty': 1.0,
                 'added_by_supplier':True,
                'state': 'draft',
                 
                 }  


    def product_id_change(self, cr, uid, ids,product,context=None):
        """
           Method that reads the default name and UOM of the given product id.
           @param product: Id of product 
           @return: Dictionary of values
        """
        if product:
            prod= self.pool.get('product.product').browse(cr, uid,product)
            return {'value': { 'name':prod.name,'product_uom':prod.uom_po_id.id}}




#----------------------------------------
# Class car maintenance roof
#----------------------------------------
#class car_maintenance_roof(osv.Model):

    """def _check_roof_cost(self, cr, uid, ids, context=None): 
       
           Method checks that amount of roof's upper and lower limit are greater than zero ro not 
           and wether the roof's upper limit is greater than the lower limit or not.
           @return: Boolean True Or False
                
       for record in self.browse(cr, uid, ids): 
        if record.cost_from <= 0.0 or record.cost_to <=0.0 or record.cost_to <= record.cost_from:
                        return False    	
        return True     

    ROOF_SELECTION = [
    ('affaris', 'Admin Affaris'),
    ('gm', 'Director of human resources, financial and administrative'),
 	]  
    _name = "car.maintenance.roof"
    _description = 'Car Maintenance Roof'
    _columns = {
                'name': fields.selection(ROOF_SELECTION, 'Name', required=True,),
                'cost_from': fields.float('Cost From', digits_compute=dp.get_precision('Account'),required=True),
                'cost_to': fields.float('Cost To', digits_compute=dp.get_precision('Account'),required=True),
               }
    _constraints = [
        (_check_roof_cost, 
            'Your Roof Cost is WRONG ... please insert the right cost',
            ['Roof Cost ']),]"""




