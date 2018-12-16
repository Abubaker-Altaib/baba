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


      _columns = {
         'name' : fields.char('Name' , size=32),
         'department_id' : fields.many2one('hr.department','Department', readonly=True),
         
         'custody_lines' : fields.one2many('custody.release.lines' , 'release_order_id' , 'release Lines') ,
         'state' : fields.selection([('draft','draft'),('confirm','Confirmed'),('verify' , 'Verify'),('release', 'Released'),('cancel','Cancelled')] , 'State' ),
                 }

      _defaults = {
              'state' : 'draft',
              'name':'/',
                 }


      _order = "name desc"

      def confirm(self,cr,uid,ids,context=None):
          for order in self.browse(cr, uid, ids, context=context):
              if not order.custody_lines:
                 raise osv.except_osv(_('Error !'), _('You Can not Confirm this order without items'))
          self.write(cr,uid,ids,{'state' : 'confirm' },context=context)
          return True



      def verify(self,cr,uid,ids,context=None):
          custody_obj = self.pool.get('custody.custody')
          asset_log_obj = self.pool.get('asset.logs')
          for order in self.browse(cr, uid, ids, context=context):
              for line in order.custody_lines:
                  if line.damage :
                     custody_id = custody_obj.search(cr,uid,[('id' , '=' , line.custody_id.id )])
                     custody_obj.write(cr,uid,custody_id,{
                                                          'in_stock' : True ,
                                                          'current_user' : False  ,
                                                          'department_id' :  False, },context=context )



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
                                                         'in_stock' : True ,
                                                         'current_user' :  False  ,
                                                         'department_id' :  False, } 
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

      

class custody_release_lines(osv.osv) :

        
        _name = "custody.release.lines"
        _columns = {
              'name' : fields.char('Serial Code' , size=32 ,readonly=True),
              'release_order_id' : fields.many2one('custody.release.order' , 'Release Order ID' ),
              'custody_id' : fields.many2one('custody.custody' , 'Custody' ,readonly=True),
              'employee_id' : fields.many2one('hr.employee','Responsible',readonly=True),
              'release_date' : fields.date('Release Date' ,readonly=True),
              'damage' : fields.boolean('Damage'),

                  }

        _sql_constraints = [
        ('serial_code_uniq', 'unique(release_order_id,name)', 'Serial Code For Item must be unique !'), 
                 ]




