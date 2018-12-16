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
from openerp import netsvc





class add_items_operation_wizard(osv.osv_memory):
          


      _name = "add.items.operation.wizard"
      _columns = {

         'operation_date' : fields.date('Operation Date'),
         'custody_ids' : fields.one2many('custody.lines','wizard_id',"Items")
 



                }


      _defaults = {

              'operation_date' : time.strftime('%Y-%m-%d')

                   }



      def create_custodies(self ,cr ,uid ,ids ,context=None):
          """ 

             This Function create Custodies Which it doesnt get by Purchase Procedure

          """
          custody_obj = self.pool.get('account.asset.asset')
          asset_log_obj = self.pool.get('asset.logs')
          for rec in self.browse(cr,uid,ids):
              if rec.custody_ids :
                 for custody in rec.custody_ids:
                     for count in range(custody.quantity):
                         custody_id = custody_obj.create( cr ,uid ,{

                                          'category_company_id' : custody.category_company_id.id,
                                          'category_id' : custody.category_id.id,
                                          'version_id' : custody.version_id.id ,
                                          'state' : 'draft' ,





                                                                     })
                         log_line = {
					      'custody_log_id' : custody_id,
					      'department_id' : False,
					      'action_type' : 'add' ,
					      'action_date' : rec.operation_date ,
					      'employee_id' :   False,
                                             }
                         log_id = asset_log_obj.create(cr,uid,log_line)
              else:
                 raise  osv.except_osv(_('Bad Action'), _('Make Sure You filled the items corretly...') )




          return True








      

class custody_lines(osv.osv_memory):







      _name = 'custody.lines'
      _columns = {
              'wizard_id' : fields.many2one('add.items.operation.wizard','Wizard ID'),
              'category_company_id' : fields.many2one('custody.company' , 'Company' ),
              'category_id' : fields.many2one('account.asset.category' ,'Parent Category' ,),
              'version_id' : fields.many2one('custody.category.models' , 'Version'),
              'quantity' : fields.integer('Quantity' ),
                 }


      _defaults = {
                          'quantity' : 1 ,


                 }



      _sql_constraints = [  ('check_quantity_bigger_than_zero',"CHECK (quantity>0)",_("The Quantity Must Be Bigger than Zero"))]

      def onchange_company(self , cr, uid , ids , category_company_id ,context=None) :
          """
           Onchange company put the restrict domain on category field

	  @return: 
			"""
          category_ids = []
          for category_id in self.pool.get("custody.company").browse(cr,uid,category_company_id).category_ids :
              if category_id :
                 category_ids.append(category_id.id)
          return { 'domain' : { 'category_id' : [( 'id' , 'in' , category_ids )] }}

