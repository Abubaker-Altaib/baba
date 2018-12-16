# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp import netsvc





class product_category(osv.Model):
      _inherit = "product.category"
      
      
      
      
      def create(self, cr, uid, data, context=None):
        category_id = super(product_category, self).create(cr, uid, data, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        
        if data['custody'] == True:
           asset_categ_id = self.pool.get('account.asset.category').create(cr,uid,{
               'name' : data['name'] ,
               'code' : str(category_id) + ' ' ,
               'product_category_id' : category_id ,
               'account_asset_id' : user.company_id.account_asset_id.id ,
               'account_depreciation_id' : user.company_id.account_depreciation_id.id ,
               'account_expense_depreciation_id' : user.company_id.account_expense_depreciation_id.id ,
               'journal_id' : user.company_id.journal_id.id ,
                                          })
        return category_id
    
    
      def write(self, cr, uid, ids, vals, context=None):
        rec = self.browse(cr,uid,ids)[0]
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if rec.custody :
            if not rec.asset_categ_ids:
               asset_categ_id = self.pool.get('account.asset.category').create(cr,uid,{
                   'name' : rec.name,
                   'code' : str(rec.id) + ' ' ,
                   'product_category_id' : ids[0] ,
                   'account_asset_id' : user.company_id.account_asset_id.id ,
                   'account_depreciation_id' : user.company_id.account_depreciation_id.id ,
                   'account_expense_depreciation_id' : user.company_id.account_expense_depreciation_id.id ,
                   'journal_id' : user.company_id.journal_id.id ,

                   
                                              })
        return super(product_category, self).write(cr, uid, ids, vals, context=context)
    
    
      _columns = {

       'custody' : fields.boolean('Asset Category' ,),
       'asset_categ_ids' : fields.one2many('account.asset.category','product_category_id','Asset Categories',),

       
                 }
      





class product_product(osv.Model):
      _inherit = "product.product"
      
      
      
      
      
      
        
        
        
        
      
    
    
    
        
      _columns = {

       'custody' : fields.boolean('Asset' ,),
       'asset_categ_id' : fields.many2one('account.asset.category','Asset Category'),
       'last_counter' : fields.integer('Last Counter' , readonly=True , default = 0 ),
       
                 }
      

      def onchange_categ_id(self, cr, uid, ids,categ_id,custody, context=None):
        # Update Asset Category When The Product is Custody
        values = []
        asset_cat_ids = []
        if categ_id :
           if custody :
              asset_cat_ids = self.pool.get('account.asset.category').search(cr,uid,[('product_category_id' , '=' , categ_id)])
              if asset_cat_ids :
                 return {'value' : {'asset_categ_id' : asset_cat_ids[0] } , 'domain' : { 'asset_categ_id' : [( 'id' , 'in' , asset_cat_ids )] }}

        return { 'value' : {'asset_categ_id' : False} ,'domain' : { 'asset_categ_id' : [( 'id' , 'in' , asset_cat_ids )] }}
                
        
        
        
        
class stock_location(osv.Model):
  
      def _check_location(self, cr, uid, ids, context=None):


        """ Checks if location usage and custody field.
            @return: True or False
        """


        for rec in self.browse(cr, uid, ids, context=context):

            if rec.custody == True and rec.usage != 'internal'  :
               return False

        return True






      _inherit = "stock.location"

      _columns = {

       'custody' : fields.boolean('Custody Location' , invisible=True),


                 }

      _constraints = [ 

        (_check_location, 'The Custody Location must be Internal Usage ',['name']),

                    ]





      

class stock_picking_in(osv.Model):


      _inherit = "stock.picking.in"

      _columns = {
       'release_order_id' : fields.many2one('custody.release.order' , 'Release Order ID' ,),
       'custodies_ids' : fields.many2many('account.asset.asset','custodies_picking_rel','picking_id','asset_id', 'Custodies')


                 }
      





class stock_picking(osv.Model):
  
     

      _inherit = "stock.picking"

      _columns = {
       'release_order_id' : fields.many2one('custody.release.order' , 'Release Order ID' ,),
       'custodies_ids' : fields.many2many('account.asset.asset','custodies_picking_rel','picking_id','asset_id', 'Custodies'),


                 }
      
      def action_done(self, cr, uid, ids, context=None):
        """
        inherit action_done function in stock picking class 
        and create custodies depend on some conditions 

        @return: True
        """

        super(stock_picking, self).action_done(cr, uid, ids, context=context)
        custody_ids = []
        picking_in_obj = self.pool.get('stock.picking.in')
        category_obj = self.pool.get('account.asset.category')
        custody_obj = self.pool.get('account.asset.asset')
        asset_history = self.pool.get('account.asset.history')
        product_obj = self.pool.get('product.product')
        asset_log_obj = self.pool.get('asset.logs')
        custody_order_obj = self.pool.get('asset.pact.order')
        custody_order_line_obj = self.pool.get('custody.order.items')
        for record in self.browse(cr,uid,ids):
            if record.type == 'in' :
             if not record.release_order_id :
	       if record.move_lines:
                  for move in record.move_lines:
                      if move.product_id.custody == True :

		              
                              last_counter = move.product_id.last_counter
		              if not move.product_id.asset_categ_id :
                                 raise  osv.except_osv(_('Bad Action'), _('To Supply Products into Custody Stock Please make sure it has corresponding catgories  ') )

		              for quantity in range(int(move.product_qty)):
				      custody_id = custody_obj.create(cr ,uid ,{
				                                                            'category_id' : move.product_id.asset_categ_id.id,
		                                                                    'ref' : record.id,
                                                                            'product_id' : record.product_id.id,
                                                                            'stock_location_id' : move.location_dest_id.id,
                                                                            'code' : str(move.product_id.default_code) + '&' + str(last_counter),
                                                                            'depreciation_rate' : move.product_id.asset_categ_id.depreciation_rate,
                                                                            'purchase_value' : move.price_unit, 
                                                                            'value_residual' : move.price_unit, 
				                                            'state' : 'draft' ,

				                                               })
                                      
                                      last_counter +=1
		                      log_line = {
						      'custody_log_id' : custody_id,
						      'department_id' : False,
						      'action_type' : 'purchase' ,
						      'action_date' : time.strftime('%Y-%m-%d') ,
						      'employee_id' :   False,
		                                     }
		                      log_id = asset_log_obj.create(cr,uid,log_line)
		                      custody_ids.append(custody_id)
                                      history_id = asset_history.create(cr,uid, {
                                                                              'name' : move.name,
                                                                              'type' : 'initial' ,
                                                                              'asset_id' : custody_id,
                                                                              'date' : time.strftime('%Y-%m-%d') ,
                                                                              'amount' : move.price_unit,
                                                                              'asset_value' : move.price_unit, 
                                                                              'state' : 'posted' ,
                       
                                                                                })






                              product_obj.write( cr, uid , [move.product_id.id] ,{'last_counter' : last_counter} )                                                   
            else :
                create_order = False
                for move in record.move_lines:

                      if move.product_id.custody == True :
		              #cat_ids = category_obj.search(cr,uid,[('product_ids' , '=' , move.product_id.id)])
		              if not move.product_id.asset_categ_id :
                                 raise  osv.except_osv(_('Bad Action'), _('To Supply Products into Custody Stock Please make sure it has corresponding catgories  ') )
                              if create_order == False :
                                 order_id = custody_order_obj.action_create_custody_order(cr ,uid ,ids ,{
		                                                          'order_date' : time.strftime('%Y-%m-%d') ,
		                                                          'source_document' : record.id,

		                                                                      },context=context)
                                 create_order = True

                              #if len(cat_ids) == 1:        
		              order_line_id = custody_order_line_obj.action_create_custody_order_line(cr ,uid ,ids ,{

		                                                          'custody_order_id' : order_id,
		                                                          'category_id' : move.product_id.asset_categ_id.id,
		                                                          'quantity' : move.product_qty,

		                                                          


		                                                                                },context=context)
#                               else : 
#                                  for cat_id in cat_ids:
#                                      order_line_id = custody_order_line_obj.action_create_custody_order_line(cr ,uid ,ids ,{
# 
# 		                                                          'custody_order_id' : order_id,
# 		                                                          'category_id' : cat_id,
# 		                                                          'quantity' : move.product_qty,
# 
# 		                                                          
# 
# 
# 		                                                                                },context=context)
                                  
        self.write(cr ,uid ,ids ,{'custodies_ids' : [(6 ,False ,custody_ids )] } )
        return True



