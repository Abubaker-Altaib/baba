# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields
import time
import netsvc
import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


#
# class rented Cars Request 
#

class rented_cars_request(osv.osv):

    def create(self, cr, user, vals, context=None):
        """
        Method creates new entry sequence for every Rented Cars
        @param vals: Dictionary contains the entered data
        @return: return a result 
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'rented.cars.request')
        return super(rented_cars_request, self).create(cr, user, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        """ 
	Mehtod overwrites copy method duplicates the value of the given id and updates the value of sequence fields.
	@param default: Dictionary of data    
	@return: Super create method
        """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'rented.cars.request'),
            
        })
        return super(rented_cars_request, self).copy(cr, uid, id, default, context)    
    
    def dep(self, cr, uid, ids,car_id):
        """ 
	Mehtod that returns the Id of the rented car owner.
	@param car_id: Id of car    
	@return: Dictionary of value
        """
        result=0
        if car_id:
            carr=self.pool.get('rented.cars').search(cr,uid,[('car_id','=',car_id)])
            carr2=self.pool.get('rented.cars').browse(cr,uid,carr)
            for record in carr2:
                result={'value': {'partner_id': record.partner_id.id}}
            return result 
       
    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed_d', 'Waiting for department manager To confirm'),
    ('confirmed_gm', 'Waiting for General department manager to approve '),
    ('boss', 'Waiting for General manager to Approve'),
    ('gm', 'Waiting for GM to approve'),
    ('process', 'Waiting for admin  affairs  manager to process'),
    ('section_process', 'Waiting for section  manager to process'),
    ('execute', 'Waiting for admin affairs officer'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]
    CAR_TYPE = [
    ('rented', 'عربة مؤجرة'),
    ('owned', 'عربة مملكوكة للشركة'),
    ]

    PAYMENT_SELECTION = [
    		('voucher', 'Voucher'),
    		('enrich', 'Enrich'), 
    			] 
  

    _name = "rented.cars.request"
    _description = 'Rented Cars Request'
    _columns = {
    'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the Rented Cars Request"),
    'date' :fields.date('Date of request',readonly=True),
    'partner_id':fields.many2one('res.partner', 'Partner',states={'done':[('readonly',True)]}),
    'car_id': fields.many2one('fleet.vehicle','Car',states={'done':[('readonly',True)]}),
    'date_of_rent':fields.date('Date of Rent',required=True,states={'process':[('readonly',True)],'section_process':[('readonly',True)],'done':[('readonly',True)]}),
    'date_of_return':fields.date('Date of Retrieved',required=True ,states={'process':[('readonly',True)],'section_process':[('readonly',True)],'done':[('readonly',True)]}),
    'employee_id': fields.many2one('hr.employee', 'Employee',states={'process':[('readonly',True)],'section_process':[('readonly',True)],'execute':[('readonly',True)],'done':[('readonly',True)]}),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ), 
    'department_id': fields.many2one('hr.department','Department',states={'done':[('readonly',True)]}),   
    'notes': fields.text('Notes', size=256,states={'done':[('readonly',True)]}),
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'car_rented_detial_ref':fields.char('Rented Details', size=64, readonly=True,),
    'car_type': fields.selection(CAR_TYPE,'CAR OWNED', required=False,size=64,states={'done':[('readonly',True)]}),
    'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',readonly=True,states={'execute':[('readonly',False)]}, select=True),
    'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'execute':[('readonly',False)]}),
    'cost':fields.integer('Cost',digits_compute= dp.get_precision('Account'),readonly=True, states={'execute':[('readonly',False)]}),


    }
    _sql_constraints = [
        ('Req_name_uniq', 'unique(name)', 'Rented Cars Request Reference must be unique !'), 
                        
        ]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'date': time.strftime('%Y-%m-%d'),
                'date_of_rent': time.strftime('%Y-%m-%d'),
                'date_of_return': time.strftime('%Y-%m-%d'),
        	'user_id': lambda self, cr, uid, context: uid,
                'state': 'draft',
                #'payment_selection': 'voucher',
		'car_rented_detial_ref' : '/',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'rented.cars.request', context=c),              

                }



    """ Workflow Functions"""
     
    def confirmed_d(self, cr, uid, ids, context=None):   
        """
	Workflow method changes the state to 'confirmed_d'.
	@return: Boolean True
        """          
        self.write(cr, uid, ids, {'state':'confirmed_d'})
        return True

    def confirmed_gm(self, cr, uid, ids, context=None):  
        """
	Workflow method changes the state to 'confirmed_gm'.
	@return: Boolean True
        """             
        self.write(cr, uid, ids, {'state':'confirmed_gm'})
        return True

    def boss(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'boss'.
	@return: Boolean True
        """  
        self.write(cr, uid, ids, {'state':'boss'},context=context)
        return True

    def gm(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'gm'.
	@return: Boolean True
        """  
        self.write(cr, uid, ids, {'state':'gm'},context=context)
        return True
    
    def process(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'process'.
	@return: Boolean True
        """  
        self.write(cr, uid, ids, {'state':'process'},context=context)
        return True

    def section_process(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'section_process'.
	@return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'section_process'},context=context)
        return True

    def execute(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'execute'.
	@return: Boolean True
        """  
        self.write(cr, uid, ids, {'state':'execute'},context=context)
        return True

    def done(self,cr,uid,ids,context=None):
        """
	Workflow method changes the state to 'done' and creates rented.cars record , 
	if car type is rent then updates fleet.vehicle that the car is active and set the car name in the rent request.
	@return: Boolean True
        """  
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        rented_cars_details_obj = self.pool.get('rented.cars')
        payment_enrich_obj = self.pool.get('payment.enrich')
        payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')
        for record in self.browse(cr, uid, ids):
	    if record.car_type =='rented' and not record.payment_selection :
                raise osv.except_osv(_('Invalid action !'), _('Sorry please select your payment method!'))
            elif record.payment_selection == 'enrich':
				#details = smart_str('Public Relation Request No:'+record.name+'\nProcedure For:'+record.procedure_for+'\nprocedure:'+record.procedure_id.name+'\nPurpose:'+record.purpose.name)
				details = 'Rented Car Request No:'+record.name
				enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					'enrich_id':record.enrich_category.id,
                        		'cost': record.cost,
					'date':time.strftime('%Y-%m-%d'),
					'state':'draft',
                        		'name':details,
					'department_id':record.department_id.id,

                            				}, context=context)
				update_car = self.pool.get('fleet.vehicle').write(cr,uid,[record.car_id.id] ,{'ownership':'rented','status':'active'})
        			self.write(cr, uid, ids, {'state':'done'})
            elif record.car_type =='owned' or record.payment_selection == 'voucher': 
		# Creating Rented Cars Details
            	details_id = rented_cars_details_obj.create(cr, uid, 		{                                                                           
					'car_id':record.car_id.id,
                                        'partner_id': record.partner_id.id, 
                                        'date_of_rent': record.date_of_rent,
					'date_of_return':record.date_of_return,
					'department_id':record.department_id.id,
					'employee_id':record.employee_id.id,
					'notes':record.name,
					'rented_request_id':record.id
                                         })
    	
		# Selecting  Name / Refernece of Cars Details  

        	rented_cars_details_ref = self.pool.get('rented.cars').browse(cr,uid,details_id)

		# Update Cars set Active After Rented
            	if record.car_type =='rented':
			update_car = self.pool.get('fleet.vehicle').write(cr,uid,[record.car_id.id] ,{'ownership':'rented','status':'active'})
        	self.write(cr, uid, ids, {'state':'done','car_rented_detial_ref':rented_cars_details_ref.name}) 
        return True


    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
	Workflow method changes the state to 'cancel' and writes nots about the cancellation.
	@return: Boolean True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Rented Cars Request Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """
	Method resets the car renting request  to 'draft' , deletes the old workflow and creates a new one.
	@return: Boolean True       
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'rented.cars.request', s_id, cr)            
            wf_service.trg_create(uid, 'rented.cars.request', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
	Method that overwrites unlink method to prevent the the deletion of records not in draft or cancel state,
	and create log message to the deleted record.
	@return: Super unlink method       
        """
        rented_request = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in rented_request:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry in order to delete a Rented Car request(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'rented.cars.request', id, 'request_cancel', cr)
            rented_request_name = self.browse(cr, uid, id, context=context).name
            message = _("rented cars request '%s' has been deleted.") % rented_request_name
            self.log(cr, uid, id, message)
        return super(rented_cars_request, self).unlink(cr, uid, unlink_ids, context=context)



