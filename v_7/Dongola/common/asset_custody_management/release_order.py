# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import tools
from osv import osv, fields, orm
import decimal_precision as dp
from tools.translate import _
import netsvc


class custody_release_order(osv.osv):
      """
      Release record including basic and history information of the particular custody."""
      def create(self, cr, user, vals, context=None):
        """
        
        """
        if ('name' not in vals) or (vals.get('name') == '/'):
            seq = self.pool.get('ir.sequence').get(cr, user, 'custody.release.order')
            vals['name'] = seq and seq or '/'
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'asset.pact.order\'') )
        new_id = super(custody_release_order, self).create(cr, user, vals, context)
        return new_id



      def unlink(self, cr, uid, ids, context=None):
		"""
		
		"""
		release_orders = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for release_order in release_orders:
		    if release_order['state'] in ['draft', 'cancel']:
		        unlink_ids.append(release_order['id'])
		    else:
		        raise osv.except_osv(_('Invalid action !'), _('In order to delete a Release Order(s), it must be cancelled first!'))
		wf_service = netsvc.LocalService("workflow")
		for id in unlink_ids:
		    wf_service.trg_validate(uid, 'custody.release.order', id, 'cancel', cr)
		return super(custody_release_order, self).unlink(cr, uid, unlink_ids, context=context)


      







      _name = 'custody.release.order'

      _inherit = ['mail.thread', 'ir.needaction_mixin']


      _columns = {
         'name' : fields.char('Name' , size=32),
         'department_id' : fields.many2one('hr.department','Department', readonly=True),
         'location_id' : fields.many2one('stock.location','Location',),
         'create_picking' : fields.boolean('Picking Created' ,readonly=True),
         'custody_lines' : fields.one2many('custody.release.lines' , 'release_order_id' , 'release Lines') ,

         'state' : fields.selection([('draft','Draft'),('confirm','Confirmed'),('verify' , 'Verified'),('release', 'Released'),('cancel','Cancelled')] , 'State' ),
                 }

      _defaults = {
              'state' : 'draft',
              'name':'/',
              'create_picking' : False,
                 }


      _order = "name desc"

      def confirm(self,cr,uid,ids,context=None):
          for order in self.browse(cr, uid, ids, context=context):
              if not order.custody_lines:
                 raise osv.except_osv(_('Error !'), _('You Can not Confirm this order without items'))
          self.write(cr,uid,ids,{'state' : 'confirm' },context=context)
          return True



      def verify(self,cr,uid,ids,context=None):
          custody_obj = self.pool.get('account.asset.asset')
          asset_log_obj = self.pool.get('asset.logs')
          picking_obj = self.pool.get('stock.picking')

          for order in self.browse(cr, uid, ids, context=context):
              if order.create_picking == False :
                     raise osv.except_osv(_('Invalid action !'), _('It Should be Create Picking Firstly!'))
              else:
                      pick_id = picking_obj.search(cr,uid,[('type' , '=' , 'in'),('release_order_id' , '=' , order.id)])
                      if not pick_id:
                         raise osv.except_osv(_('Invalid action !'), _('It Should be Create Picking Firstly Please Contact to System Adminisitrator!'))
                     
                      if len(pick_id) == 1:
                         pick_rec = picking_obj.browse(cr,uid,pick_id)

                         if pick_rec[0].state != 'done':
                            raise osv.except_osv(_('Process not Complete !'), _('To Release these custodies from customer it should be receive the Incoming Shipment No.("%s" ) ') % (pick_rec[0].name))       
                         for line in order.custody_lines:
                              if line.damage :
                                 custody_id = custody_obj.search(cr,uid,[('id' , '=' , line.custody_id.id )])
                                 custody_obj.write(cr,uid,custody_id,{
                                                                      'state' : 'abandon' ,
                                                                      'current_employee' : False  ,
                                                                      'period_type' : False,
                                                                      'expacted_return_date' : False,
                                                                      'custody_location_id' : False ,
                                                                      'department_id' :  False, 
                                                                      'create_release_order' :  False, 
                                                                       'user_id' : False , },context=context )
            
            
            
            	                 lines_res = {
            					      'custody_log_id' : custody_id[0] ,
            					      'department_id' : order.department_id.id,
            					      'action_type' : 'damage' ,
                                      'action_date' : line.release_date ,
            					      'employee_id' : line.employee_id.id or False,
                                                         
            						 }
                              
                                 asset_log_obj.create(cr,uid,lines_res)
                              else:
                                 custody_id = custody_obj.search(cr,uid,[('id' , '=' , line.custody_id.id )])
                                 res = {
                                                                     'state' : 'released' ,
                                                                     'current_employee' :  False  ,
                                                                     'stock_location_id' : order.location_id.id,
                                                                     'period_type' : False,
                                                                     'expacted_return_date' : False,
                                                                     'custody_location_id' : False ,
                                                                     'department_id' :  False, 
                                                                     'create_release_order' :  False, 
                                                                     'user_id' : False , } 
                                 custody_obj.write(cr,uid,custody_id,res, context=context) 
                                 lines_res = {
            					      'custody_log_id' : custody_id[0] ,
            					      'department_id' : order.department_id.id,
            					      'action_type' : 'release' ,
                                                          'action_date' : line.release_date ,
            					      'employee_id' : line.employee_id.id or False,
            						 }
                              
                                 asset_log_obj.create(cr,uid,lines_res)

          self.write(cr,uid,ids,{'state' : 'verify' },context=context)
          return True


      def cancel(self,cr,uid,ids,context=None):
		""" 
		Workflow function changes order state to cancel.

		    
		@return: Boolean True
		"""
	      
		self.write(cr, uid, ids, {'state':'cancel'}, context=context)
		return True

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
		    wf_service.trg_delete(uid, 'custody.release.order', s_id, cr)            
		    wf_service.trg_create(uid, 'custody.release.order', s_id, cr)
		return True   
      
      def action_prepare_incoming_shipment(self ,cr ,uid ,ids ,context=None):
          """ 
		Function For Prepare Incoming Shipment .

		    
		@return: Picking ID
		"""
          warning = {}
          picking_obj = self.pool.get('stock.picking.in')
          move_obj = self.pool.get('stock.move')
          product_temp_obj = self.pool.get('product.product')
          custody_obj = self.pool.get('account.asset.asset')
          category_obj = self.pool.get('account.asset.category')
          for order in self.browse(cr, uid, ids, context=context):
              create_order = False
              pick_id = False
              pick = {}
              moves = []
              product = []
              for line in order.custody_lines:
                  if not line.custody_id.custody_location_id.property_customer_location.id:
                     raise osv.except_osv(_('Invalid action !'), _('Please Make Sure You are Assigned Customer Location in Asset Location View!'))
                  if not line.custody_id.ref :
                    categ_id = line.custody_id.category_id.id
                    product_id = product_temp_obj.search(cr,uid,[('asset_categ_id','=', categ_id)])
                  else :
                     if not line.custody_id.product_id:
                        raise osv.except_osv(_('Data Entry Error !'), _('This Custody Have an Error When it Entry ... Please Call Adminsitrator !'))
                     product_id =  line.custody_id.product_id.id
                
                  product = product_temp_obj.browse(cr,uid,product_id)
                  if product:

                               if create_order == False:
                                  
                                  pick =  {
                                                             'origin' : 'Return Custody Order No.(' + order.name + ')' ,
                                                             'type' : 'in',
                                                             'release_order_id' : order.id,






                                                             }
                                  self.write(cr ,uid ,ids , { 'create_picking' : True })
                               create_order = True
                               move = {
                                'name': product.name or '',
							    'product_id': product.id,
							    'product_qty': 1.0 ,
							    'product_uos_qty': 1.0,
							    'product_uom': product.product_tmpl_id.uom_id.id,
							    'product_uos': product.product_tmpl_id.uom_id.id,
							    'date': time.strftime('%Y-%m-%d'),
							    'date_expected': time.strftime('%Y-%m-%d'),
							    'location_id': line.custody_id.custody_location_id.property_customer_location.id,
							    'location_dest_id': order.location_id.id,
							    #'picking_id': pick_id,
							    'state': 'draft',
							    'type':'in',
							    'price_unit': product.standard_price, }
                               moves.append(move)
                     
          
              
          return pick,moves 
      
      def action_create_incoming_shipment(self ,cr ,uid ,ids , pick , moves , context=None):
          """ 
        Function For Creating Incoming Shipment .

            
        @return: Picking ID
        """
          picking_obj = self.pool.get('stock.picking.in')
	  move_obj = self.pool.get('stock.move')
          pick_id = False
          if pick and moves:

             pick_id = picking_obj.create(cr,uid,pick)
	     for move in moves:
		 move['picking_id'] = pick_id
		 move_id = move_obj.create(cr ,uid ,move)
          
          return pick_id
          
      def action_make_incoming_shipment(self ,cr ,uid ,ids , context=None):
          """
          
          
          
          """
          pick,  moves = self.action_prepare_incoming_shipment(cr,uid,ids,context=context)
          
          pick_id = self.action_create_incoming_shipment(cr ,uid ,ids ,pick ,moves ,context=context)
          
          return True
          
          

class custody_release_lines(osv.osv) :

        
        _name = "custody.release.lines"
        _columns = {
              'name' : fields.char('Serial Code' , size=32 ,readonly=True),
              'release_order_id' : fields.many2one('custody.release.order' , 'Release Order ID' ),
              'custody_id' : fields.many2one('account.asset.asset' , 'Custody' ,readonly=True),
              'employee_id' : fields.many2one('hr.employee','Responsible',readonly=True),
              'release_date' : fields.date('Release Date' ,readonly=True),
              'damage' : fields.boolean('Damage'),

                  }

        _sql_constraints = [
        ('serial_code_uniq', 'unique(release_order_id,name)', 'Serial Code For Item must be unique !'), 
                 ]




