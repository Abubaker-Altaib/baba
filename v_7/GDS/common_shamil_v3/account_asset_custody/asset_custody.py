# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class asset_custody(osv.osv):
	"""
	To manage custody operations
	"""
	_name = 'asset.custody'
	USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
	def create(self, cr, user, vals, context=None):
		"""
		Override to add constrain of sequance
		@param vals: Dictionary of values
		@return: super of asset_custody
		"""
		if ('name' not in vals) or (vals.get('name') == '/'):
			seq = self.pool.get('ir.sequence').get(cr, user, 'asset.custody')
			vals['name'] = seq and seq or '/'
			if not seq:
				raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'asset.custody\'') )
			#if vals['temporary_custody']=='True':
			 #   print vals['temporary_custody'],"fffffffffffffffffffffff"
			  #  lines=vals['asset_lines']
		   
			   
		new_id = super(asset_custody, self).create(cr, user, vals, context)
		return new_id

	def unlink(self, cr, uid, ids, context=None):
		"""
		Perfrom deleting custody orders in state 'draft', 'cancel'
		and prohibit user from deleting records in other states
		@return super unlink function ofasset_custody
		"""
		exchange_orders_line = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for order in self.browse(cr, uid, ids, context):
			if order.state not in ['draft']:
				raise osv.except_osv(_('Error !'), _('You can not delete a order not in draft state'))
		return super(asset_custody, self).unlink(cr, uid, unlink_ids, context=context)

	def _get_type(self, cr, uid,context=None):

		""" Determine the asset's type"""

		custody_type = 'request'
		if context:
			if context.has_key('type'): custody_type = context['type']
		return custody_type	

	def changes_state(self, cr, uid, ids, vals,context=None):
		""" 
		Changes order state 
		@param vals: dict that will be used in write method
		@return: True
		"""     
		for order in self.browse(cr, uid, ids, context=context):
			if order.type == 'return':
				if not order.asset_line and order.state not in  ('canceled'):
					raise  osv.except_osv(_('Warning'), _('You cannot %s without asset line'%vals['state']) )
				self.write(cr, uid, [order.id], vals)
			self.pool.get('asset.custody.line').write(cr, uid, [x.id for x in order.asset_line], vals,context=context)

			if order.type == 'released':
				if not order.asset_line and order.state not in  ('canceled'):
					raise  osv.except_osv(_('Warning'), _('You cannot %s without asset line'%vals['state']) )
				self.write(cr, uid, [order.id], vals)
			self.pool.get('asset.custody.line').write(cr, uid, [x.id for x in order.asset_line], vals,context=context)

			if order.type == 'request':
				if not order.asset_line and order.state not in  ('canceled'):
					raise  osv.except_osv(_('Warning'), _('You cannot %s without asset line'%vals['state']) )
				self.write(cr, uid, [order.id], vals)
			self.pool.get('asset.custody.line').write(cr, uid, [x.id for x in order.asset_line], vals,context=context)
		return True

	def confirm(self,cr,uid,ids,context=None):
	   
 
		"""
		@ Code for data migration .
		@ Check quantity and produce line according to .
		
		"""
		for order in self.browse(cr, uid, ids, context=context):
			if not order.serial_no:  # If data migration 
				custody_line_obj=self.pool.get('asset.custody.line')
				order_id = order.id
				for custody_line in order.asset_line:
			 		if custody_line.qty>1:
						qty=custody_line.qty
						for qty in range(0,qty-1):  
							custody_line_obj.copy(cr, uid, custody_line.id,default={'custody_id':order_id,'qty': 1}, context=context)
						custody_line_obj.write(cr, uid, custody_line.id,{'qty': 1}, context=context)

		"""
		Workflow function to change the custody state to confirm
		@return: True
		"""         
		self.changes_state(cr, uid, ids,{'state': 'confirmed'},context=context)           
		return True

	def approve(self,cr,uid,ids,context={}):
		"""
		Workflow function to change the custody state to approve.
		@return: True
		"""
		asset_obj = self.pool.get('account.asset.asset')
		#custody_rec = self.browse(cr, uid, ids, context=context)[0]
		#custody_asset_id = custody_rec.asset_id.id
  
		#asset_obj.write(cr,uid,custody_asset_id,{'employee_id':custody_rec.employee_to.id, })
		self.changes_state(cr, uid, ids,{'state': 'approved'},context=context)
		return True
	
	def cancel(self,cr,uid,ids,context=None):
		""" 
		Workflow function changes custody state to canceled 
			@return: Boolean True
		"""   
		for order in self.browse(cr, uid, ids, context=context):
			self.pool.get('asset.custody.line').write(cr, uid, [x.id for x in order.asset_line], {'state':'canceled'},context=context)
			self.write(cr, uid, ids, {'state':'canceled'})   
		return True 

	
	STATE_SELECTION = [
		('draft', 'Draft'),
		('transfer', 'Transfer'),
		('confirmed', 'Confirmed'),
 
		('recived', 'Recived'),
		('canceled', 'Canceled'),
	   ]


	_columns = {
	'name' : fields.char('Reference',readonly=True ,),
	'date': fields.date(string='Date', required=True , readonly=True , states={'draft':[('readonly', False)]}),

	#'return_date': fields.date(string='Return Date'),
	#'request_date': fields.date(string='Request Date'),
	'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',  select=True,help='Department Which this request will executed it'),
	'date_done': fields.date(string='Done Date',readonly=True),
		'show_released': fields.boolean('Show released'),
		'temporary_custody': fields.boolean('Temporary Custody Exist'),
		'stock': fields.boolean('stock Transfer',readonly=True ),
		'office': fields.many2many('office.office', string='office'),
		'cat_id': fields.many2one('product.category', string='category'),
		'product_id': fields.many2one('product.product', string='product'),
		'employee_id': fields.many2one('hr.employee', string='Destination Employee'),
		'employee_id1': fields.many2one('hr.employee', string='Delivered Employee'),
		'employee_enter': fields.many2one('hr.employee', string='Responsilbe'),
		'employee_id2': fields.many2one('hr.employee', string='Recieving Employee'),
		'department_id' : fields.many2one('hr.department',' Source Department'),
	'time_scale' : fields.selection([('constant','constant'),('temporary','temporary')], string='time'),
	'request_date': fields.date(string='Request date', ),
	'return_date': fields.date(string='Return_date', ),
	'action_type' : fields.selection([('recieve','Recieved'),('release','Released'),('damage','Damage')], string='Action Type', readonly=True ),
	'type' : fields.selection([('request','Request'),('return','Return')], string='Action Type', readonly=True ),

		'state': fields.selection(STATE_SELECTION, 'State', readonly=True, select=True),
	'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type'),	
		'note' : fields.text('Note',),
	'asset_line':fields.one2many('asset.custody.line','custody_id', 'Asset Line'),
	'history_line':fields.one2many('history.custody.line','custody_id', 'History Line'),
		'return_type_id': fields.many2one('custody.return.type','Return Type', select=True, states={'confirmed':[('readonly', True)]}),
		'serial_no': fields.related('asset_line', 'serial_no', type='char', string='Serial', ),
		'employee_to': fields.related('asset_line', 'employee_to', type='many2one', string='Destination Employee', relation='hr.employee', readonly=True),	
		'department_to': fields.related('asset_line', 'department_to', type='many2one', string='Destination Department', relation='hr.department',  ),	
		'stock_journal': fields.many2one('stock.journal', 'Journal'),
	}

	_defaults = {
	'state' : 'draft',	
	'type' : _get_type,
	'temporary_custody' : True,
	#'executing_agency' :lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).executing_agency,		
	'date' : time.strftime('%Y-%m-%d'),
	#'request_date' : time.strftime('%Y-%m-%d'),
		 }

	_order = "date desc"

	

   
	def find_custody(self,cr,uid,ids,context=None):
		"""
		 FILL HISTORY LINE  DEPEND ON DATA INTERED TO USE IN 
		 RELEASE CUSTODIES.
		"""

		history_line_obj = self.pool.get('history.custody.line')
		custody_line_obj = self.pool.get('asset.custody.line')
		product_obj = self.pool.get('product.product')
		product_category_obj = self.pool.get('product.category')
		department_obj = self.pool.get('hr.department')
 
 
		for custody in self.browse(cr, uid, ids):
			custody_id=custody.id
			custody_line_ids=[]
			custody_type=custody.custody_type

			if custody.history_line:
			   unlink_ids=[]
			   for line in custody.history_line:
				unlink_ids.append(line.id)
			   history_line_obj.his_unlink(cr,uid,unlink_ids,context=None)

			if custody_type=='management':
				department_id=0
				department_ids=[]
				department_id=custody.department_id.id
				department_ids= department_obj.search(cr, uid, [('id', 'child_of', department_id)])
			custody_line_ids = custody_line_obj.search(cr,uid,[('department_to','in',department_ids),('custody_type','=',custody_type), ])
			if custody.office:
				  office_ids=[]
				  office=custody.office
			for office in office:
				office_id=office.id
				office_ids.append(office_id) 
				custody_line_ids = custody_line_obj.search(cr,uid,[('id','in',custody_line_ids),('office','in',office_ids), ])

			if custody_type=='personal':
			   employee_id=0
			   employee_id=custody.employee_id.id
			custody_line_ids = custody_line_obj.search(cr,uid,[('employee_to','=',employee_id),('custody_type','=',custody_type), ])
		   
			if custody.product_id :
				product_ids=custody.product_id
				pro_ids=[]
				for product in product_ids:
					product_id=product.id
					pro_ids.append(product_id) 
				custody_line_ids = custody_line_obj.search(cr,uid,[('id','in',custody_line_ids),('product_id','in',pro_ids), ])
	  
		if  custody.cat_id and not custody.product_id:
				cat_ids=custody.cat_id
				cat_all_ids=[]
				cat_childs=[]

				for cat in cat_ids:
					cat_id=cat.id
 
					cat_childs=  product_category_obj.search(cr, uid, [('id', 'child_of', cat_id)])
					cat_all_ids.append(cat_childs)
		 
					
				pro_ids = product_obj.search(cr,uid,[('categ_id','in',cat_all_ids[0]) ])  
				custody_line_ids = custody_line_obj.search(cr,uid,[('id','in',custody_line_ids),('product_id','in',pro_ids)])  
 
				for custody_id in custody_line_ids:
					custody_line_id = custody_line_obj.search(cr,uid,[('id','=',custody_id) ])
					custody_h=custody_line_obj.browse(cr,uid,custody_line_id)
					for custody_h in custody_h:
						if custody.show_released==False:
							if custody_h.state_rm =='custody':
	  
								cus_line_id = history_line_obj.create(cr, uid , {
						 'custody_id': custody.id,
					 	 'custody_line_id':custody_h.id,
						 'employee_to':  custody_h.employee_to.id,
						 'custody_type':custody_h.custody_type,
							 'executing_agency':custody.executing_agency,
						 'main_type': custody_h.main_type.id,
						 'department_to':custody_h.department_to.id,
						 'office': custody_h.office.id,
						 'request_date': custody_h.request_date,
						 'return_date': custody_h.return_date,
						 'product_id': custody_h.product_id.id,
						 'state_rm': custody_h.state_rm,
				 })
 

				if custody.show_released==True:
					 cus_line_id = history_line_obj.create(cr, uid , {
					 'custody_id': custody.id,
					 'custody_line_id':custody_h.id,
					 'employee_to':  custody_h.employee_to.id,
					 'custody_type':custody_h.custody_type,
						 'executing_agency':custody.executing_agency,
					 'main_type': custody_h.main_type.id,
					 'department_to':custody_h.department_to.id,
					 'office': custody_h.office.id,
					 'request_date': custody_h.request_date,
					 'return_date': custody_h.return_date,
					 'product_id': custody_h.product_id.id,
					 'state_rm': custody_h.state_rm,
 





								   
					}) 
				 
		
		return True

	def recived(self,cr,uid,ids,context=None):
		"""
		Workflow function to change the custody state to recived
		@return: True
		"""
		asset_obj = self.pool.get('account.asset.asset')
		asset_log_obj = self.pool.get('asset.log')
		custody_line_obj = self.pool.get('asset.custody.line')
		history_custody_obj = self.pool.get('as.custody.line')
		asset_obj=self.pool.get('account.asset.asset')
		stock_picking_obj=self.pool.get('stock.picking')
		stock_move_obj=self.pool.get('stock.move')


		for order in self.browse(cr, uid, ids, context=context):
			'''REQUEST '''
			if order.type=="request":
				order_id = order.id
				asset_id=False
				if  not order.stock:  # DATA MIGRATION
					for custody_line in order.asset_line:
						if not custody_line.asset_id:
						# CREATE ASSET ITEM
							asset_id = asset_obj.create(cr, uid , {
										 'name':custody_line.product_id.name,
										 'category_id':'1',
										 'asset_type':'custody',
										 'office_id': custody_line.office.id,
										 'chassis': custody_line.chassis,
										 'number': custody_line.number,
										 'machine_no': custody_line.machine_no,
										 'model': custody_line.model,
										 'fuel': custody_line.fuel,
										 'vechile':True,
										 'serial': custody_line.serial_no,
										 'department_id': custody_line.department_to.id,
										 'employee_id': custody_line.employee_to.id  ,
										 'request_date': custody_line.custody_id.date,
										 'return_date': custody_line.return_date ,
										 'product_id':custody_line.product_id.id,
										 'main_type': custody_line.product_id.categ_id.id,
							 			 'time_scale': 'constant' , 
										 'executing_agency': custody_line.executing_agency,
										 'custody_type' : custody_line.custody_type,
										 'state_rm' :custody_line.state_rm,
							},context=context) 
					        asset_log_obj.create(cr, uid , {
										 'asset_id':asset_id,
										 'date': custody_line.custody_id.date,
										 'employee_id': custody_line.employee_to.id  ,
										 'office_id': custody_line.office.id,
										 'department_id': custody_line.department_to.id,
										 'state' : 'added',
							},context=context) 
						custody_line_obj.write(cr, uid,custody_line.id , {'asset_id':asset_id}, context=context)


				  
		self.changes_state(cr, uid, ids,{'state': 'recived'},context=context)
		#raise  osv.except_osv(_('msg'), _('An asset had been Altered.') )       
		return True



	def action_cancel_draft(self, cr, uid, ids, context=None):
		""" 
		Workflow function changes custody order state to draft.
		@param *args: Get Tupple value
		@return: True
		"""
		if not len(ids):
			return False
		wf_service = netsvc.LocalService("workflow")
		for order_id in ids:
			# Deleting the existing instance of workflow for order
			wf_service.trg_delete(uid, 'asset.custody', order_id, cr)
			wf_service.trg_create(uid, 'asset.custody', order_id, cr)
		for (id, name) in self.name_get(cr, uid, ids):          
			message = _("Custody order '%s' has been set in draft state.") % name
			self.log(cr, uid, id, message)
		self.changes_state(cr, uid, ids,{'state': 'draft'},context=context)     
		return True


	def create_line(self, cr, uid, ids, context=None):
            for order in self.browse(cr, uid, ids, context=context):
            	line_id = self.pool.get('asset.custody.line').create(cr, uid ,{
 							 'custody_id': order.id,
							# 'office_id': order.office.id,
							 'department_to': order.department_to.id,
							 'employee_to': order.employee_id.id  ,
							 'custody_type': order.custody_type , 
							 'executing_agency': order.executing_agency , 
							 'time_scale': 'constant' , 
							 'qty': 1, 
 

 
 
				},context=context)     
		return line_id

#----------------------------------------------------------
# Asset lines
#----------------------------------------------------------

class asset_custody_line(osv.osv): 
	_name = "asset.custody.line"

	STATE_SELECTION = [
		('draft', 'New'),
		('released', 'Released'),
		('assigned', 'Assigned'),
        ('damage', 'Damage'),
	   ]	
	USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
	_columns = {
	'asset_id': fields.many2one('account.asset.asset', string='Asset'),
	'vechile': fields.boolean('Vechile'),
    'model': fields.char('Model'),
    'chassis': fields.char('Chassis'),
    'machine_no': fields.char('Machine'),
    'number': fields.char('Number'),
	'fuel' : fields.selection([('diesel','Diesel'),('gasoline','Gasoline')], string='fuel'),
		'state_rm': fields.selection(STATE_SELECTION, 'State',  select=True),
		'return_type': fields.many2one('custody.return.type', string='Type of Return'),
	#'employee_id': fields.related('asset_id','employee_id',type='many2one',relation='hr.employee',string='Employee', store=True),
		#'department_id': fields.related('asset_id','department_id',type='many2one',relation='hr.department',string='Department', store=True,),  
		'employee_from': fields.many2one('hr.employee', string='Source Employee'),
	'employee_to': fields.many2one('hr.employee', string='Destination Employee'),
		'department_from' : fields.many2one('hr.department',' Source Department'),

	'department_to' : fields.many2one('hr.department','Destination Department'),
	'product_id' : fields.many2one('product.product','Product'),
	'location_from':fields.many2one('account.asset.location', string='Source Location'),
	'location_to':fields.many2one('account.asset.location', string='Destination Location'),
		'custody_id': fields.many2one('asset.custody','Asset', readonly=True),
		'serial_no': fields.char('Bar-Code', size=32 ,help="Bar-Code the Asset"),
		'state': fields.char('State', readonly=True, select=True),
	'p_id': fields.char('Military_ID'),
	'referance': fields.char('Referance', size=32 ,help="Stock Referance"),
	'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type'),	
	'main_type': fields.many2one('product.category', string='type'),
		'office': fields.many2one('office.office','office' ),
	#'model':fields.many2one('model.model', string='Model'),
		'qty': fields.integer('Quantity'),
		'time_scale' : fields.selection([('constant','constant'),('temporary','temporary')], string='time'),
	'request_date': fields.date(string='Request date',   ),
	'return_date': fields.date(string='Return_date',  ),
	'date': fields.date(string='Date of creation',readonly=True),
	'date_done': fields.date(string='Done Date',readonly=True),
	'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',  select=True,help='Department Which this request will executed it'),
	}
	_defaults = {
	'state_rm' : 'draft',	
 
	 
		 }
	 

	def on_change_data(self, cr, uid, ids,department_to,office_id,product_id,executing_agency,custody_type,employee_to, context=None):
		domain = {}
		asset_obj = self.pool.get('account.asset.asset')
 
 
		


		asset_ids=[]
                if custody_type=='management':
			asset_ids = asset_obj.search(cr,uid, [
			('department_id' ,'=', department_to),
			('office_id' ,'=',office_id),	
			('product_id' ,'=',product_id),
			('executing_agency' ,'=', executing_agency),
			('custody_type' ,'=',custody_type) ,
		])  

		else :
 		    asset_ids = asset_obj.search(cr,uid, [(
			'employee_id' ,'=',employee_to ),
			('product_id' ,'=',product_id),
			('executing_agency' ,'=', executing_agency),
			('custody_type' ,'=',custody_type) ,
		])  
		return {'domain':{'asset_id':[('id','in',asset_ids)]}}

	def on_change_asset(self, cr, uid, ids, asset_id, context=None):
		asset_custody_obj = self.pool.get('asset.custody')
		request_ids = asset_custody_obj.search(cr,uid,[('type','=','request')])
		asset_custody_line_obj = self.pool.get('asset.custody.line')
		if asset_id:
			record_id = asset_custody_line_obj.search(cr,uid,[('asset_id','=',asset_id),('custody_id','in',request_ids)])
			record = asset_custody_line_obj.browse(cr,uid,record_id)[0]
			return {'value': {'department_to':record.department_to and record.department_to.id or False,'employee_to':record.employee_to and record.employee_to.id or False, 'serial_no': record.serial_no or None}}
		return {}

#------------------------------------------------------------------------------
	def on_change_employee(self, cr, uid, ids, employee_id, context=None):
		domain = {}
		asset_custody_obj = self.pool.get('asset.custody')
		request_ids = asset_custody_obj.search(cr,uid,[('type','=','request')])
		asset_custody_line_obj = self.pool.get('asset.custody.line')
		this_obj = self.browse(cr,uid,ids)
		if employee_id:
			asset_ids=[]
			custody_lines_id = asset_custody_line_obj.search(cr,uid,[('employee_to','=',employee_id),('custody_id.type','=','request')])
			for line in asset_custody_line_obj.browse(cr,uid,custody_lines_id):
				asset_ids.append(line.asset_id.id)  
			domain = {'asset_id':[('product_id','!=', False),('stock_location_id','!=',False),('id','in',asset_ids)]}
		return{'value': {'employee_to':employee_id}, 'domain': domain}
#----------------------------------------------------------------------------
	def on_change_department(self, cr, uid, ids, department_id, context=None):
		domain = {}
		asset_custody_obj = self.pool.get('asset.custody')
		request_ids = asset_custody_obj.search(cr,uid,[('type','=','request')])
		asset_custody_line_obj = self.pool.get('asset.custody.line')
		this_obj = self.browse(cr,uid,ids)
		if department_id:
                        department_ids= department_obj.search(cr, uid, [('id', 'child_of', department_id)])
			asset_ids=[]
			custody_lines_id = asset_custody_line_obj.search(cr,uid,[('department_to','=',department_id),('custody_id.type','=','request')])
			for line in asset_custody_line_obj.browse(cr,uid,custody_lines_id):
				asset_ids.append(line.asset_id.id)  
			domain = {'asset_id':[('product_id','!=', False),('stock_location_id','!=',False),('id','in',asset_ids)]}
		return{'value': {'department_to':department_ids}, 'domain': domain}

#-----------------------------RETURN----------------------------------------------

	def custody_return(self,cr, uid, ids, context=None):
		custody_obj = self.pool.get('asset.custody')
		location_obj = self.pool.get('stock.location')
		type_obj = self.pool.get('custody.return.type')

		type_ids=[]
		location_ids_all=[]
		stock_journal=[]

		location_ids_all=location_obj.search(cr, uid,[('scrap_location','=',True)])
		type_ids= type_obj.search(cr, uid,[('location_id','in',location_ids_all)])
		type_id=type_ids[0]



		type_for_journal=type_obj.search(cr, uid,[('id','in',type_ids)])
 
		for  type_for_journal in  type_obj.browse(cr, uid, type_for_journal): 
			 stock_journal=type_for_journal.stock_journal.id
 

		for custody_line in self.browse(cr, uid, ids): 

			emp_id= custody_line.employee_to.id
			custody_type= custody_line.custody_type
			executing_agency= custody_line.executing_agency
			main_type= custody_line.main_type.id
			location_to= custody_line.location_to.id
			department_to= custody_line.department_to.id
			office= custody_line.office.id
			 
				
			model= custody_line.model.id
			asset_id= custody_line.asset_id.id
			referance= custody_line.referance
			if custody_line.state_rm=='removed':
				raise  osv.except_osv(_('Warning'), _('This custody was already removed.') )
			cus_id = custody_obj.create(cr, uid , {
				 'type': 'return',
								 'date': time.strftime('%Y-%m-%d'),
				 'return_type_id': type_id,
								 'custody_type': custody_type ,
							 'exist' : 'True',
							 'stock_journal' : stock_journal,
								 'asset_line' : [],
							   
				}) 
			cus_line_id = self.create(cr, uid , {
				 'custody_id': cus_id,
				 'employee_to':  emp_id,
				 'custody_type':custody_type,
					 'executing_agency':executing_agency,
				 'main_type': main_type,
				 'department_to':department_to,
				 'office': office,
				 'model':  model,
				 'asset_id':asset_id,
				 'referance':referance,
					# 'location_from': location_from,
					 'location_to': location_to,

							   
				}) 
		return True
#-----------------------------REMOVE----------------------------------------------

	def custody_remove(self,cr, uid, ids, context=None):
		custody_obj = self.pool.get('asset.custody')
		location_obj = self.pool.get('stock.location')
		type_obj = self.pool.get('custody.return.type')
		for custody_line in self.browse(cr, uid, ids): 
			executing_agency= custody_line.executing_agency
		type_ids= type_obj.search(cr, uid,[('remove','=',True),('executing_agency','=',executing_agency)])
 
		type_id=type_ids[0]
		
		for custody_line in self.browse(cr, uid, ids): 

			emp_id= custody_line.employee_to.id
			custody_type= custody_line.custody_type
			executing_agency= custody_line.executing_agency
			main_type= custody_line.main_type.id
			department_to= custody_line.department_to.id
			office= custody_line.office.id
			model= custody_line.model.id
			asset_id= custody_line.asset_id.id
			referance= custody_line.referance
			location_to= custody_line.location_to.id
				
			if custody_line.state_rm=='moved':
				raise  osv.except_osv(_('Warning'), _('This custody was already returned back.') )
		
			cus_id = custody_obj.create(cr, uid , {
				 'type': 'return',
							 'exist' : 'True',
								 'date': time.strftime('%Y-%m-%d'),
				 'return_type_id': type_id,
								 'custody_type': custody_type ,
					 'remove':'True',
								 'asset_line' : [],
							   
				}) 
			cus_line_id = self.create(cr, uid , {
				 'custody_id': cus_id,
				 'employee_to':  emp_id,
				 'custody_type':custody_type,
					 'executing_agency':executing_agency,
				 'main_type': main_type,
				 'department_to':department_to,
				 'office': office,
				 'model':  model,
				 'asset_id':asset_id,
				 'referance':referance,
					 'location_to': location_to,

							   
				}) 
		return True


asset_custody_line()
#-------------------------CLASS OF HISTORY USED TO RETURN PREVIOUS CUSTODIES ---------------------#
class history_custody_line(osv.osv): 
	_name = "history.custody.line"

	STATE_SELECTION = [
		('custody', 'custody'),
 
		('released', 'released'),
		('removed', 'removed'),
 
		 
	   ]
	USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
	_columns = {
	'asset_id': fields.many2one('account.asset.asset', string='Asset'),
		'state_rm': fields.selection(STATE_SELECTION, 'State', select=True),
		'return_type_id': fields.many2one('custody.return.type','Return Type', select=True, states={'confirmed':[('readonly', True)]}),
	#'employee_id': fields.related('asset_id','employee_id',type='many2one',relation='hr.employee',string='Employee', store=True),
		#'department_id': fields.related('asset_id','department_id',type='many2one',relation='hr.department',string='Department', store=True,),  
		'employee_from': fields.many2one('hr.employee', string='Source Employee'),
	'employee_to': fields.many2one('hr.employee', string='Destination Employee'),
		'department_from' : fields.many2one('hr.department',' Source Department'),
	'custody_line_id' : fields.many2one('asset.custody.line','Custody'),
		'decision' : fields.selection([('replace','replace'),('ultimate','ultimate')], string='Action' ),
	'department_to' : fields.many2one('hr.department','Destination Department'),
	'product_id' : fields.many2one('product.product','Product'),
	'location_from':fields.many2one('account.asset.location', string='Source Location'),
	'location_to':fields.many2one('account.asset.location', string='Destination Location'),
		'custody_id': fields.many2one('asset.custody','Asset', readonly=True),
		'serial_no': fields.char('Bar-Code', size=32 ,help="Bar-Code the Asset"),
		'state': fields.char('State', readonly=True, select=True),
	'p_id': fields.char('Military_ID'),
	'referance': fields.char('Referance', size=32 ,help="Stock Referance"),
	'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type'),	
	'main_type': fields.many2one('product.category', string='type'),
		'office': fields.many2one('office.office','office' ),
	#'model':fields.many2one('model.model', string='Model'),
		'qty': fields.integer('Quantity'),
		'time_scale' : fields.selection([('constant','constant'),('temporary','temporary')], string='time'),
	'request_date': fields.date(string='Request date',   ),
	'return_date': fields.date(string='Return_date',  ),
	'date': fields.date(string='Date of creation',readonly=True),
	'date_done': fields.date(string='Done Date',readonly=True),
	'check': fields.boolean(string='Check'),
	'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency',  select=True,help='Department Which this request will executed it'),
	}
		
	 
	def his_unlink(self, cr, uid, unlink_ids, context=None):
		"""
		 
		"""
		unlink_ids = unlink_ids
		return super(history_custody_line, self).unlink(cr, uid, unlink_ids, context=context)

history_custody_line()   
#----------------------------------------------------------
# ADD REPAIR FIELD TO LOCATION
#----------------------------------------------------------
class stock_location(osv.osv):
	_name = "stock.location"  
	_inherit="stock.location"
	USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
	_columns = {
		'repair_location': fields.boolean('Repair', size=32),
		'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),

		 
	}
stock_location()
	
#----------------------------------------------------------
# STOCK WIZARD INHERITANCE
#----------------------------------------------------------

#----------------------------------------------------------
# Custody Return Type
#----------------------------------------------------------
class custody_return_type(osv.osv):
	_name = "custody.return.type"
	_columns = {
		'name': fields.char('Return Type', size=32, required=True),
		'user_id': fields.many2one('res.users', 'Responsible'),
		
	}
	_defaults = {
		'user_id': lambda s, c, u, ctx: u
	}

custody_return_type()	




#----------------------------------------------------------
# Custody Configuration(Office & Types & Models)
#----------------------------------------------------------
class custody_configuration(osv.osv):
	_name = "custody.configuration"
	USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
	_columns = {
	#'type_line':fields.one2many('type.type','type_id', 'Type Line'),
	'office_line':fields.one2many('office.office','office_id', 'office Line'),
	#'model_line':fields.one2many('model.model','model_id', 'model Line'),
	'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),

	
	}
	 

custody_configuration()	

class office_office(osv.osv):
	_name = "office.office"
	USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
	_columns = {
	'office_id': fields.many2one('custody.configuration', string='office'),
	'name': fields.char('office', size=32 ,help=""),
	'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
 
	 
	}
	 

office_office()	



class account_asset_asset(osv.osv):
	_inherit = "account.asset.asset"
 
	USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]
	STATE_SELECTION = [
		('custody', 'custody'),
 
		('released', 'released'),
		('removed', 'removed'),
 
		 
	   ]		 
	_columns = {
	'office_id': fields.many2one('office.office', string='office'),
	'custody_lines':fields.one2many('as.custody.line','asset_id', 'Custody Line'),
    'vechile': fields.boolean('Vechile'),
    'model': fields.char('Model'),
    'chassis': fields.char('Chassis'),
    'machine_no': fields.char('Machine'),
    'number': fields.char('Number'),
	'time_scale' : fields.selection([('constant','constant'),('temporary','temporary')], string='time'),
	'fuel' : fields.selection([('diesel','Diesel'),('gasoline','Gasoline')], string='fuel'),
	'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', select=True,help='Department Which this request will executed it'),
	'custody_type': fields.selection([('personal','Personal'),('management','Management')], string='Custody Type'),	
	'product_id' : fields.many2one('product.product','Product'),
	'department_id' : fields.many2one('hr.department','Product'),
	'main_type': fields.many2one('product.category', string='Category'),
	'employee_id': fields.many2one('hr.employee', string='Category'),
	'request_date': fields.date(string='Request date', ),
	'return_date': fields.date(string='Return_date', ),
        'state_rm': fields.selection(STATE_SELECTION, 'State',  select=True),
	}
	 

account_asset_asset()


class as_custody_line(osv.osv): 
	_name = "as.custody.line"
 
	_columns = {

	'asset_id': fields.many2one('account.asset.asset','Asset'),
	'employee_to': fields.many2one('hr.employee', string='Destination Employee'),
	'department_to' : fields.many2one('hr.department','Destination Department'),
	'type' : fields.selection([('request','Request'),('return','Return')], string='Action Type', readonly=True ),
	'serial_no': fields.char('Bar-Code', size=32 ,help="Bar-Code the Asset"),
	'referance': fields.many2one('asset.custody','custody' ),
	'office_id': fields.many2one('office.office','office' ),
	'request_date': fields.date(string='Request date',   ),
	'date': fields.date(string='Date of creation'),
 
 
	}
	





