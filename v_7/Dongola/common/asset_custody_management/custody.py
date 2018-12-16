# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################



import time
import tools
from openerp.osv import fields, osv
from openerp import netsvc
#from django.utils.encoding import smart_str, smart_unicode
import decimal_precision as dp
from tools.translate import _
import sys  





class account_asset_location(osv.Model):

    """ Add Property Field In order to Complete Convert the Assets """


    _inherit = 'account.asset.location'
    _columns = {
        'property_customer_location': fields.property('stock.location', type='many2one',relation='stock.location',string="Customer Location",
            view_load=True,  domain=[('usage','=','customer')], ),
    }





class custody_category_models(osv.Model):
      _name = 'custody.category.models'
      _columns = {

       'name' : fields.char('Model Name' , size=64 ),
       'category_id' : fields.many2one('account.asset.category','Category ID'),

                 }
      
      _sql_constraints = [
        ('name_category_uniq', 'unique(name,category_id)', 'Category ID must be unique !'), 
                 ]






class custody_category(osv.Model):



      _inherit = 'account.asset.category'
      
      _columns = {


       'image' : fields.binary('Image' ),
       'model_ids' : fields.one2many('custody.category.models','category_id','Models'),
       'product_category_id' : fields.many2one('product.category','Product Category'),
       'products_ids' : fields.one2many('product.product','asset_categ_id','Products',),
                 }
      





class custody_company(osv.Model) :


      _name = 'custody.company'
      _columns = {

       'name' : fields.char('Company Name' , size=64 ),
       'logo' : fields.binary('Logo' ),
       'web_site' : fields.char('Website' , size=64 ),
       'category_ids' : fields.many2many('account.asset.category','custody_company_category_rel','company_id','category_id','Categories'),

                 }











class custody_custody(osv.Model):


      def name_get(self, cr, uid, ids, context=None):
	if context is None:
	    context = {}
	if isinstance(ids, (int, long)):
           ids = [ids]
	res = []
        reload(sys)  
        sys.setdefaultencoding('utf-8')
        for record in self.browse(cr,uid,ids,context=context):
	       name = str(record.category_company_id.name) +'-'+str(record.category_id.name)+'-'+str(record.version_id.name)+'-' +str(record.code)
	       res.append((record.id, name))
	return res




      def _custody_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):

          """ function for concatate Asset Name """
          res = {}
          reload(sys)  
          sys.setdefaultencoding('utf-8')
          for record in self.browse(cr,uid,ids,context=context):
	      name = str(record.category_company_id.name) +'-'+str(record.category_id.name)+'-'+str(record.version_id.name)+'-' +str(record.code) 
              res[record.id] = name 

      	  return res

      def _custody_load_image_fnc(self, cr, uid, ids, prop, unknow_none, context=None):

          res ={}
          for rec in self.browse(cr ,uid ,ids):
              if rec.category_id.id:

	      	 category_image = self.pool.get('account.asset.category').browse(cr , uid , [rec.category_id.id])[0].image
		 self.write(cr ,uid , [rec.id] ,  { 'image_medium' : category_image } , context=context)

          return res


      _inherit = 'account.asset.asset'
      _columns = {
              'full_name' : fields.function(_custody_name_get_fnc, type="char", string='Full Name' ,store=True),
              'category_company_id' : fields.many2one('custody.company' , 'Company of Category' ),
              'code' : fields.char( 'Serial Code' , size=64  ,),
              'category_id' : fields.many2one('account.asset.category' ,'Parent Category' ,),
              'version_id' : fields.many2one('custody.category.models' , 'Version'),
              'current_employee' : fields.many2one('hr.employee' , 'Current User' ,),
              'user_id' :  fields.many2one('res.users' , 'User' ,),
              'load_category_image' : fields.function(_custody_load_image_fnc, type="char", string='Company'),
              'image_medium' : fields.binary('Company' ),
              'department_id' : fields.many2one('hr.department' , 'Department' ),
              'stock_location_id' : fields.many2one('stock.location' , 'Stock Location' ),
              'custody_specification' : fields.selection([('admin','Administrative'),('techn' , 'Techincal')], 'Custody Specification ',),
              'create_release_order' : fields.boolean('Order Created' ,readonly=True),
              'period_type' : fields.selection([('temp','Temparory'),('const' , 'Constant')], 'Period Type',),
              'expacted_return_date' : fields.date('Expected Date',),
              'product_id' : fields.many2one( 'product.product' , 'Product' ,),
              'ref' : fields.many2one( 'stock.picking' , 'Reference' ,),
              'custody_location_id' :fields.many2one('account.asset.location' , 'Location' ),
              'log_ids' : fields.one2many('asset.logs','custody_log_id','Log ID' ),
              'state': fields.selection([('draft','Draft'),('open','Assigned'),('close','Close'),('released','In Stock'),
                                   ('suspend','suspend'),('sold','Sold'),('abandon','Damage')],
                                    'Status', required=True,)
              #'state' : fields.selection([('new','New') , ('released','In Stock') , ('assigned', 'Assigned') , ('damage','Damage')] , 'State'),
                 }

      _defaults = {


         
             'name' : '/',
             'state' : 'draft',

                }
      _sql_constraints = [
        ('serial_code_uniq', 'unique(code)', 'Serial Code For Item must be unique !'), 
                 ]


      









      




      def unlink(self, cr, uid, ids, context=None):
		"""
		
		"""
		state = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		if state :
		   raise osv.except_osv(_('Invalid action !'), _('Sorry You Cant delete this Item!'))
		
		return super(custody_custody, self).unlink(cr, uid, unlink_ids, context=context)




      def onchange_company(self , cr, uid , ids , category_company_id ,context=None) :
          """
           Onchange company put the restrict domain on category field

	  @return: 
			"""
          category_ids = []
          if category_company_id:
             for category_id in self.pool.get("custody.company").browse(cr,uid,category_company_id).category_ids :
                  if category_id :
                     category_ids.append(category_id.id)

          return { 'domain' : { 'category_id' : [( 'id' , 'in' , category_ids )] }}


      def onchange_category(self , cr, uid , ids , category_id ,context=None) :
          """
           Onchange category load the image to item 

	  @return: 
			"""
          category_image = self.pool.get('account.asset.categorys').browse(cr , uid , category_id).image
          self.write(cr , uid , ids , { 'image_medium' : category_image } ,context=context )

          return True

      def onchange_employee(self , cr, uid , ids , employee_id ,context=None) :
          """
           Onchange employee select crosspond user

	  @return: 
			"""

          if employee_id:
             for rec in self.browse(cr,uid,ids):

                 self.write(cr , uid , ids , { 'user_id' : rec.current_employee.user_id.id } ,context=context )
                
          return True

      def create_release_order(self , cr, uid , ids ,context=None) :
	"""
	Button function to create release order for custody
 
	@return: release Request Id
	"""        
	release_obj = self.pool.get('custody.release.order')
	release_lines_obj = self.pool.get('custody.release.lines')
	wf_service = netsvc.LocalService("workflow") 

	for record in self.browse(cr,uid,ids):
	     
	    if record.state != 'open' :
	          raise  osv.except_osv(_('Bad Action'), _('You Cant Release the custody in stock ...') )
	    
	    order_id = release_obj.create(cr, uid, {
	                                                          'department_id' : record.department_id.id, 
	                                                           })
	    release_lines_obj.create(cr, uid, { 'release_order_id': order_id,
	                                        'custody_id': record.id,
	                                        'name' : record.code ,
	                                        'employee_id': record.current_employee.id or False, 
	                                        'release_date': time.strftime('%Y-%m-%d') ,})

	    wf_service.trg_validate(uid, 'custody.release.order', order_id, 'draft_confirm', cr)
        self.write(cr ,uid ,ids , { 'create_release_order' : True })
        return order_id

class asset_logs(osv.Model):
      _name = 'asset.logs'
      _columns = {
              'custody_log_id' : fields.many2one('account.asset.asset','Custody ID'),
              'department_id' : fields.many2one('hr.department','Department', readonly=True ),
              'action_type' : fields.selection([('purchase','Purchased'),('add','Added'),('recieve','Recieved'),('release','Released'),('reassign','Reassigned'),('damage','Damage')], 'Action Type' , readonly=True ),
              'action_date' : fields.date('Action Date ' , readonly=True ),
              'employee_id' : fields.many2one('hr.employee','Responsible', readonly=True ),

                 }

