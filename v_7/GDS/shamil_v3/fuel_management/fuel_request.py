# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


#********************************************************
# This class To Manage The Fuel Request  
#********************************************************

from osv import fields,osv
import netsvc
import time
from tools.translate import _
import decimal_precision as dp
import pdb
from datetime import datetime,date,timedelta


class fuel_request(osv.osv):

    def create(self, cr, user, vals, context=None):
      	"""
        Create new entry sequence for every new fuel request Record

        @param vals: list of record to be process
        @return: return a result 
	    """

        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'fuel.request')
        return super(fuel_request, self).create(cr, user, vals, context) 


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
            'name': self.pool.get('ir.sequence').get(cr, uid, 'fuel.request'),
            'picking_no':''
        })
        return super(fuel_request, self).copy(cr, uid, id, default, context)

    def _check_fuel_qty(self, cr, uid, ids, context=None):
       """
       Constraints function to check fule request product    
        
       @return: Boolean True or False
       """
       for record in self.browse(cr, uid, ids): 
        if record.car_id.id >0:
	  search_result = self.pool.get('fleet.vehicle').browse(cr, uid,record.car_id.id)
	  if search_result.monthly_plan == True :
	   for lines in record.fuel_lines : 
	   	for fuel in search_result.fuel_lines:
                    if lines.product_id.id != fuel.product_id.id :
                        return False    	
        return True

    TYPE_SELECTION = [
         ('emergency', 'Emergency'),
         ('mission','Mission'),
         ]

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed_s', 'Department Manager Confirm'),
    ('confirmed_d', 'Admin Affairs Approve '),
    ('approved', 'Service Section Manager Process'),
    ('execute', 'Service Officer Exceute'),
    ('picking', 'In Progress'),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]
    PAYMENT_SELECTION = [
    		('stock', 'From Stock'),
    		('enrich', 'Enrich'), 
    			]

    _name = "fuel.request"
    _columns = {
    'alarm':fields.text('Alarm', size=10 ,),
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the fuel request,computed automatically when the Fuel  is created"),
    'date' : fields.datetime('Date',readonly=True),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'employee_ids': fields.many2many('hr.employee','fuel_reuest_emp_rel','request_id','emp_id' , 'Employee/Beneficiary', required=True, states={'approved':[('readonly',True)],'execute':[('readonly',True)],'done':[('readonly',True)]}),
    'date_of_travel':fields.datetime('Date of Travel',),
    'date_of_return':fields.datetime('Date of Return',),
    'fuel_lines':fields.one2many('fuel.request.lines', 'fuel_id' , 'Fuel',states={'done':[('readonly',True)]}),
    'purpose': fields.selection(TYPE_SELECTION, 'Purpose', required=True ,select=True,states={'approved':[('readonly',True)],'execute':[('readonly',True)],'done':[('readonly',True)]}),
    'car_id':  fields.many2one('fleet.vehicle', 'Car Name',required=False ,states={'done':[('readonly',True)]}),
    'car_number': fields.related('car_id', 'plate_no', type='char', relation='fleet.vehicle', string='Car Number', readonly=True),
    'notes': fields.text('Notes', size=256 ,),
    'description': fields.char('Description',size=256 ,states={'approved':[('readonly',True)],'execute':[('readonly',True)],'done':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'driver':  fields.related('car_id','driver_id', type='many2one' , relation='hr.employee' ,string='Driver',),
 #'department':  fields.related('car_id', 'department_id', type='many2one', relation='hr.department',store=True, string='Department', readonly=True ),
    'department': fields.many2one('hr.department', 'Department Name',),
    'picking_no': fields.char('Piciking No.', size=64,readonly=True),
    'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
    'payment_selection': fields.selection(PAYMENT_SELECTION,'Payment',states={'done':[('readonly',True)]}, select=True),
    'enrich_category':fields.many2one('payment.enrich','Enrich',readonly=True,states={'execute':[('readonly',False)]}),
    'parent_id':fields.integer('Parent',size=10,),
    'cost':fields.integer('Cost',digits_compute= dp.get_precision('Account'),readonly=True, states={'execute':[('readonly',False)]}),

    }
    _sql_constraints = [
        ('fuel_name_uniq', 'unique(name)', 'fuel request Reference must be unique !'),
		]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
        	    'user_id': lambda self, cr, uid, context: uid,
                'date': lambda *a: time.strftime('%Y-%m-%d'),
		        'purpose':'mission',
		        'payment_selection':'enrich',
                'state': 'draft',
                'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
                }
    _constraints = [
        (_check_fuel_qty, 
            'Your Car Fuel Does not Match With Your Requested One . ',
            ['Fuel Details']),]

     
    def confirmed_s(self, cr, uid, ids,alarm=' ',context=None):
        """ 
        Workflow Function to change state to confirmed_s and fuel lines.

        @param alarm: text of alarm
        @return: Boolean True
        """
        alarm = ""
        for lines in self.browse(cr, uid, ids):
	    if lines.purpose =='emergency':
                if not lines.fuel_lines:
                    raise osv.except_osv(_('No Fuel Plan !'), _('Please Insert Fuel Item Details ..'))  
                if not lines.department:
                    raise osv.except_osv(_('No Department  !'), _('Please Insert Department ..'))  
                elif not lines.employee_ids:
                    raise osv.except_osv(_('No Employee/Beneficiary  !'), _('Please Insert Employee/Beneficiary Details ..'))    
            else :  
                ex_date=self.pool.get('fuel.request').browse(cr, uid,ids)[0].date_of_travel
                req_date=self.pool.get('fuel.request').browse(cr, uid,ids)[0].date
                ex_date1=datetime.strptime(ex_date,'%Y-%m-%d').date()
                req_date1=datetime.strptime(req_date,'%Y-%m-%d').date()
                diff_day=(ex_date1-req_date1).days             
                if  diff_day<3:
                    alarm =alarm +'\n'+' Cancelled Becase Request Later : '+ex_date
                    self.write(cr, uid, ids, {'state':'confirmed_s','alarm':alarm})     
                     
        self.write(cr, uid, ids, {'state':'confirmed_s'})
        return True

    def confirmed_d(self, cr, uid, ids, context=None): 
        """ 
        Workflow Function to change state to confirmed_d.

        @return: Boolean True
        """            
        self.write(cr, uid, ids, {'state':'confirmed_d'})
        return True

    def approved(self,cr,uid,ids,context=None):
        """ 
        Workflow Function to change state to approve.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state':'approved'},context=context)
        return True
    
    def execute(self,cr,uid,ids,context=None):
        """ 
        Workflow Function to change state to execute.

        @return: Boolean True
        """
        """department_obj = self.pool.get('hr.department')
        for record in self.browse(cr, uid, ids):
            parent1=record.department.parent_id.id
            parent= department_obj.browse(cr,uid,parent1,context=context).parent_id.id
            if parent1==False or parent1==319:
                   parent= department_obj.browse(cr,uid,record.department.id,context=context).id
            elif parent1==1:
                   parent= department_obj.browse(cr,uid,record.department.id,context=context).parent_id.id
            #elif department_obj.browse(cr,uid,parent1,context=context).id==319:
             #      parent= parent1
            self.write(cr, uid, ids,{'parent_id':parent},context=context)"""
        self.write(cr, uid, ids, {'state':'execute'},context=context)
        return True

    def action_create_picking(self,cr,uid,ids,context=None):
        """ 
        Workflow Function to change state to picking and create picking.

        @return: Boolean True
        """
        pick_name = ''
	# Fuel Picking Objects
        fuel_picking_obj = self.pool.get('fuel.picking')
        fuel_picking_line_obj = self.pool.get('stock.move')
        fuel_request_lines_obj = self.pool.get('fuel.request.lines')
        payment_enrich_obj = self.pool.get('payment.enrich')
        payment_enrich_lines_obj = self.pool.get('payment.enrich.lines')
        for record in self.browse(cr, uid, ids):
	       if record.purpose =='mission' or record.purpose =='emergency' :
                if not record.fuel_lines:
                       raise osv.except_osv(_('No Fuel  !'), _('Please Fuel Item Details ..'))
                if record.payment_selection == 'enrich':
                    #details = smart_str('Public Relation Request No:'+record.name+'\nProcedure For:'+record.procedure_for+'\nprocedure:'+record.procedure_id.name+'\nPurpose:'+record.purpose.name)
                    details = 'Extra Fuel Request No:'+record.name+"\nPurpose:"+record.purpose
                    enrich_payment_lines_id = payment_enrich_lines_obj.create(cr, uid, {
					            'enrich_id':record.enrich_category.id,
                        		'cost': record.cost,
					            'date':time.strftime('%Y-%m-%d'),
					            'state':'draft',
                        		'name':details,
					            'department_id':record.department.id,
                            				}, context=context)
                    self.write(cr, uid, ids, {'state':'done'},context=context)
                elif record.payment_selection == 'stock' :    
                # Creating Piciking
                    pick_name = self.pool.get('ir.sequence').get(cr, uid, 'fuel.picking.out')
                    picking_id = fuel_picking_obj.create(cr, uid, {
                                'name': pick_name,
            					'origin': record.name,
            					'date': record.date,
            					'type': 'out',
           					    'state': 'draft',
						        'move_type':'direct',
            					'note': record.notes,
            					'department_id':record.department.id,
						        'fuel_request_id':record.id
                                         })
            	# Creating Picking Lines
                    for line in record.fuel_lines:
                        if not line.product_id.property_fuel_customer.id :
                            raise osv.except_osv(_('No Location  !'), _('Please Insert Fuel Destination Location ..'))
                        picking_line_id = fuel_picking_line_obj.create(cr, uid, {
                                                   'name': line.name,
            					   'fuel_picking_id': picking_id,
            					   'product_id': line.product_id.id,
            					   'product_qty': line.product_qty,
            					   'product_uom': line.product_uom.id,
						   #'product_uos_qty':line.product_qty,
            					   'state': 'draft',
            					   'location_id': line.product_id.property_fuel_extra.id ,
            					   'location_dest_id': line.product_id.property_fuel_customer.id ,
                                    'fuel_request_line_id': line.id,
                                         })
                        fuel_request_lines_obj.write(cr, uid, [line.id], {'move_id':picking_line_id})
                    self.write(cr, uid, ids, {'state':'picking','picking_no':pick_name})
        return True
  
    def move_lines_get(self, cr, uid, ids, *args):
        """ 
        To read stock moves of the fuel picking.
        @param args: extra arguments
        @return: dictionary of move lines
        """
        res = []
        new_amount=0
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.fuel_lines:
                move = line.move_id
                if move:
                        res.append(move.id)
        return res
    
    def test_state(self, cr, uid, ids, mode, *args):
        """
        To test state 
        if mode == 'finished':
                returns True if all lines are done, False otherwise
            if mode == 'canceled':
        @returns: Boolean True if there is at least one canceled line, False otherwise
        """
        assert mode in ('finished', 'canceled'), _("invalid mode for test_state")
        finished = True
        canceled = False
        notcanceled = False
        write_done_ids = []
        write_cancel_ids = []
        new_amount=0
        amount=0
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.fuel_lines:
                if self.pool.get('fuel.request.lines').test_finished(cr, uid, [line.id])==False:
                    finished = False
                    
                if self.pool.get('fuel.request.lines').test_cancel(cr, uid, [line.id])==True:
                    canceled = True
                else:
                    notcanceled = True
                
        if mode == 'finished':
            return finished
        elif mode == 'canceled':
            if notcanceled:
                return False
            return canceled
    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes order state to cancel and writes note

	    @param notes: contains information of who & when cancelling order.
        @return: Boolean True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Extra Fuel Request Cancelled at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes order state to Draft and reset the workflow.

        @return: True 
        """
        # Reset the fuel request to draft 
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'fuel.request', s_id, cr)            
            wf_service.trg_create(uid, 'fuel.request', s_id, cr)
        return True

# oN CHANGE #############################################################################
    """    def car_id_change(self, cr, uid,ids,car,context=None):
       fuel_line_obj = self.pool.get('fuel.request.lines')

       When you select car the id send to this method to read the default Fuel name and UOM And QTY
       @param cr: cursor to database
       @param user: id of current user
       @param ids: list of record ids to be process
       @param product: product_id 
       @return: return a result

       for record in self.browse(cr, uid, ids):   
	 lines_ids = [line.id for line in record.fuel_lines]
         fuel_line_obj.unlink(cr,uid,lines_ids,context=context)
         if car:
	   search_result = self.pool.get('fleet.vehicle').browse(cr, uid,car)
	   if search_result : 
	   	for fuel in search_result.fuel_lines:
			fuel_id = fuel_line_obj.create (cr, uid, {
					'name':fuel.name,
                                        'product_id': fuel.product_id.id, 
        
                                        'product_qty': search_result.fueltankcap,
					'product_uom':fuel.product_uom.id,
					'fuel_id':record.id,
                                         })

       return True        """

    def unlink(self, cr, uid, ids, context=None):
        """
        Delete the Fuel Request record if record in draft or cancel state,
        and create log message to the deleted record
        @return: super unlink method 
        """
        fuel_request = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in fuel_request:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry in order to delete a fuel extra request(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'fuel.request', id, 'request_cancel', cr)
            fuel_request_name = self.browse(cr, uid, id, context=context).name
            message = _("Fuel extra request '%s' has been deleted.") % fuel_request_name
            self.log(cr, uid, id, message)
        return super(fuel_request, self).unlink(cr, uid, unlink_ids, context=context)




# fuel request Lines
class fuel_request_lines(osv.osv):
    """
    To manage request lines """

    _name = "fuel.request.lines"
    _description = 'Type of Fuel and Qty'
    
    """def copy_data(self, cr, uid, id, default=None, context={}):
        if not default:
            default = {}
        default.update({'move_ids':[]})
        return super(fuel_request_lines, self).copy_data(cr, uid, id, default, context)
    """
    _columns = {
                'name': fields.char('Name', size=64 ,select=True,),
                'product_id': fields.many2one('product.product','Item',required=True),
                'product_qty': fields.float('Item Quantity', required=True, digits=(16,2)),
                'product_uom': fields.many2one('product.uom', 'Item UOM'),
                'fuel_id': fields.many2one('fuel.request', 'Fuel Request', ondelete='restrict'),
                'move_id': fields.many2one('stock.move', 'Reservation', readonly=True),
                'notes': fields.text('Notes', size=256 ,),
                'description': fields.text('Specification'),

               }
    _sql_constraints = [
        ('produc_uniq', 'unique(fuel_id,product_id)', 'Sorry You Entered Product Two Time You are not Allow to do this.... So We going to delete The Duplicts!'),
            ]  
    _defaults = {
                 'product_qty': 1.0
                 }  
    def product_id_change(self, cr, uid, ids,product):
       """
       On change product function to read the default name and UOM of product

       @param product: product_id 
       @return: return a result
       """
       if product:
           prod= self.pool.get('product.product').browse(cr, uid,product)
           return {'value': { 'name':prod.name,'product_uom':prod.uom_po_id.id}}

    def test_finished(self, cr, uid, ids, context=None):
        """ 
        Test whether the request lines are done or not.

        @return: True or False
        """
        for order in self.browse(cr, uid, ids, context=context):
             move = order.move_id
             if move.state not in ('done',):
                return False

        return True

    def test_cancel(self, cr, uid, ids, context=None):
        """ 
        Test whether the request lines are canceled or not.

        @return: Boolean True or False
        """
        
        for order in self.browse(cr, uid, ids, context=context):
            move = order.move_id
            if move.state not in ('cancel',):
                return False
            
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
