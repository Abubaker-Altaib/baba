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


class asset_pact_order(osv.osv):
      """
      Asset Pact record including basic information of the Pact."""

      def create(self, cr, user, vals, context=None):
        """
        
        """
        if ('name' not in vals) or (vals.get('name') == '/'):
            seq = self.pool.get('ir.sequence').get(cr, user, 'asset.pact.order')
            vals['name'] = seq and seq or '/'
            if not seq:
                raise  osv.except_osv(_('Warning'), _('No sequence defined!\nPleas contact administartor to configue sequence with code \'asset.pact.order\'') )
        new_id = super(asset_pact_order, self).create(cr, user, vals, context)
        return new_id


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
            'name': self.pool.get('ir.sequence').get(cr, uid, 'asset.pact.order'),
            'categories_ids':[],
            'pact_line_ids':[],
        })
        return super(asset_pact_order, self).copy(cr, uid, id, default, context)





      def action_create_custody_order(self ,cr ,uid ,ids ,order={},context=None):
          """This Function For Create Custody Order
              
              @para order : is a dictionary holds order data,

              @return order_id"""
          



          order_id =  self.create( cr , uid , order ,context=context)

          return order_id
              
                        
 







      def unlink(self, cr, uid, ids, context=None):
		"""
		
		"""
		pact_orders = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for pact_order in pact_orders:
		    if pact_order['state'] in ['draft', 'cancel']:
		        unlink_ids.append(pact_order['id'])
		    else:
		        raise osv.except_osv(_('Invalid action !'), _('In order to delete a Pact Order(s), it must be cancelled first!'))
		wf_service = netsvc.LocalService("workflow")
		for id in unlink_ids:
		    wf_service.trg_validate(uid, 'asset.pact.order', id, 'cancel', cr)
		return super(asset_pact_order, self).unlink(cr, uid, unlink_ids, context=context)


      






      _name = 'asset.pact.order'
      _description = 'Custody Request'
      _inherit = ['mail.thread']
      _track = {
        'state': {
            'asset_pact_order.mt_custody_order_state_change': lambda self, cr, uid, obj, ctx=None: True,
        },}



      _columns = {
         'name' : fields.char('Name' , size=32),
         'department_id' : fields.many2one('hr.department','Department', ),
         'user':  fields.many2one('res.users', 'Responsible', readonly=True,),
         'order_date' : fields.date('Date' ,),
         'purpose' : fields.char('Purpose',size=64, ),
         'source_document' : fields.many2one('stock.picking' , 'Source Document' ,),
         'custody_type' : fields.selection([('department','Administrative'),('personal' , 'Personal')], 'Custody Type',),
         'period_type' : fields.selection([('temp','Temparory'),('const' , 'Constant')], 'Period Type',),
         'expacted_return_date' : fields.date('Expected Date',),
         'categories_ids' : fields.one2many('custody.order.items' , 'custody_order_id' , 'Categories') ,
         'pact_line_ids' : fields.one2many('pact.order.line' , 'pact_order_id' , 'Pact Lines') ,
         
         'notes': fields.text('Notes'),
         'state' : fields.selection([('draft','Draft'),
                                     ('confirmed','Confirmed'),
                                     ('approved','Approved from Section Manager'),
                                     ('approve_dept','Approved from Department Manager'),
                                     ('approve_support','Approved from Techincal Manager'),
                                     ('assigned' , 'Assigned'),
                                     ('cancel','Cancelled')] , 'State' ),
                 
                 }

      _defaults = {
              'name':'/',
              'order_date': lambda *a: time.strftime('%Y-%m-%d'),
              'user': lambda self, cr, uid, context: uid,
              'state' : 'draft',
              


                 }
      _order = "order_date desc,name desc"



      _sql_constraints = [

                   ('check_expacted_return_date',"CHECK(expacted_return_date >= order_date)",_("Expacted Return Date must be bigger than Order Date!")) ,
                   ]   




      def confirm(self,cr,uid,ids,context=None):
          """ 
        Workflow function changes order state to confirmed.

            
        @return: Boolean True
        """
          for order in self.browse(cr, uid, ids, context=context): 
              
              if not order.categories_ids:  
                 raise osv.except_osv(_('Error !'), _('Please Fill the Categories'))
           
          self.write(cr,uid,ids,{'state' : 'confirmed' },context=context)
          return True

      def approve(self,cr,uid,ids,context=None):
          """ 
        Workflow function changes order state to approved.

            
        @return: Boolean True
        """
          self.write(cr,uid,ids,{'state' : 'approved' },context=context)
          return True
      def approve_dept(self,cr,uid,ids,context=None):
          """ 
        Workflow function changes order state to approve_dept.

            
        @return: Boolean True
        """
          self.write(cr,uid,ids,{'state' : 'approve_dept' },context=context)
          return True
      
      def approve_support(self,cr,uid,ids,context=None):
          """ 
        Workflow function changes order state to approve_suport.

            
        @return: Boolean True
        """ 
          if not isinstance(ids, list):
             ids = [ids] 
          pact_line_obj = self.pool.get('pact.order.line')
          emp_obj = self.pool.get('hr.employee')
          

          for order in self.browse(cr, uid, ids, context=context): 
              user_id = order.user.id
              user_name = order.user.name
              if not order.categories_ids:  
                 raise osv.except_osv(_('Error !'), _('Please Fill the Assets or Assign the Assets to Users.'))

                  
              
              if order.custody_type == 'personal':
                 emp_id = emp_obj.search(cr ,uid ,[('user_id', '=' , user_id ),('name','=',user_name)]  )
                 if not emp_id:
                       emp_id = [False]
              else :
                 emp_id = [False]

              for line in order.categories_ids:
                  for custody in range(line.quantity):
                      custody_id = pact_line_obj.create(cr ,uid , {'category_id' : line.category_id.id,
                                                                   'custody_type' : order.custody_type,
                                                                   'employee_id' : emp_id[0],
                                                                   'pact_order_id' : order.id ,} ,context=context)

          self.write(cr,uid,ids,{'state' : 'approve_support' },context=context)
          return True





      def assign(self,cr,uid,ids,context=None):
          employee_obj = self.pool.get('hr.employee')
          user_obj = self.pool.get('res.users')
          custody_obj = self.pool.get('account.asset.asset')
          asset_obj = self.pool.get('account.asset.asset')
          asset_log_obj = self.pool.get('asset.logs')
          parent_res = { }
          lines_res = { }
          for order in self.browse(cr, uid, ids, context=context): 
              

              if not order.categories_ids:  
                 raise osv.except_osv(_('Error !'), _('Please Fill the Assets or Assign the Assets to Users.'))

              if not order.pact_line_ids:  
                 raise osv.except_osv(_('Error !'), _('Please Fill the Assets or Assign the Assets to Users.'))

              #desire_quantity = 0 
 
              #for categ in order.categories_ids:
              #    desire_quantity += categ.quantity


              #if len(order.pact_line_ids) !=  desire_quantity :
              #   raise osv.except_osv(_('Error !'), _('The Desire Quantities and The Number of Assign Quantities Not Equal .'))



              for line in order.pact_line_ids:

                  custody_id = custody_obj.search(cr,uid,[('id' , '=' , line.custody_id.id )])
                  parent_res = {

                   'state' : 'open',
                   'custody_type' : order.custody_type ,
                   'current_employee' : line.employee_id.id ,
                   'period_type' : order.period_type,
                   'expacted_return_date' : order.expacted_return_date or False,
                   'department_id' : order.department_id.id,
                   'custody_location_id' : line.custody_location_id.id ,
                   'user_id' : line.employee_id.user_id.id,
                                }
                
                 
                  lines_res = {
                      'custody_log_id' : custody_id[0] ,
                      'department_id' : order.department_id.id,
                      'action_type' : 'recieve' ,
                      'action_date' : order.order_date ,
                      'employee_id' : line.employee_id.id or False,
                         }
                  
                  log_id = asset_log_obj.create(cr,uid,lines_res)
                  custody_obj.write(cr,uid,custody_id, parent_res ,context=context)
              self.write(cr,uid,ids,{'state' : 'assigned' },context=context)
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
            wf_service.trg_delete(uid, 'asset.pact.order', s_id, cr)            
            wf_service.trg_create(uid, 'asset.pact.order', s_id, cr)
        return True    



class custody_order_items(osv.osv) :

        
        def action_create_custody_order_line(self ,cr ,uid ,ids ,lines={},context=None):
          """This Function For Create Custody Order lines
              
              @para order : is a dictionary holds order data,
              @para lines : is a dictionary holds lines data,
              @return order_id"""
          


          line_id = self.create( cr , uid , lines ,context=context)

          return line_id

        _name = "custody.order.items"
        _columns = {


              'name' : fields.char('Name' , size=32),
              'custody_order_id' : fields.many2one('asset.pact.order' , 'Custody Order ID' ),
              'category_id' : fields.many2one('account.asset.category' , 'Category' ,),
              'quantity' : fields.integer('Quantity' , required=True,  ),

              

                  }

        _sql_constraints = [
                   ('category_code_uniq', 'unique(custody_order_id,category_id)',_("Categories Duplicated !")), 
                   ('check_quantity_bigger_than_zero',"CHECK (quantity > 0)",_("The Quantity Must Be Bigger than Zero"))  , 


                 ]
        _defaults = {


              'quantity' : 1 ,




                 }

class pact_order_line(osv.osv) :

        


        _name = "pact.order.line"
        _columns = {
              'name': fields.related('custody_id', 'code', type='char', relation='account.asset.asset', string='Serial Code', store=True , readonly=True),
              'pact_order_id' : fields.many2one('asset.pact.order' , 'Pact Order ID' ),
              'custody_id' : fields.many2one('account.asset.asset' , 'Custody' ,),
              'category_id' : fields.many2one('account.asset.category' , 'Category' ,),
              'custody_location_id' :fields.many2one('account.asset.location' , 'Location' ),
              'employee_id' : fields.many2one('hr.employee','Responsible',),
              'custody_type' : fields.selection([('department','Administrative'),('personal' , 'Personal')], 'Custody Type',),

                  }

        _sql_constraints = [
                   ('serial_code_uniq', 'unique(pact_order_id,custody_id)', 'Serial Code For Item must be unique !'), 
                 ]
        



