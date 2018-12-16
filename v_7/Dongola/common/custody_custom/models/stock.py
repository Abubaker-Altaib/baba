
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
import time
from admin_affairs.model.email_serivce import send_mail







class stock_picking_out(osv.Model):






        
#       def _check_items_purpose(self, cr, uid, ids, context=None): 
#         """ 
#         Constrain function to check the category of items tp prevent the changing of order when it contains custodies.
# 
#         @return: Boolean True or False  
#         """
#         check_order_categ = False
#         check_order_items = False
#         for rec in self.browse(cr, uid, ids, context=context):
#             if rec.category_id:
#                 print "rec rec rec",rec
#                 if rec.category_id.custody == True:
#                    check_order_categ = True
#                    
#                 for line in rec.move_lines:
#                     if line.product_id.custody:
#                         check_order_items = True
#                 if rec.period_type == 'consum' and ( check_order_categ == True or check_order_items == True ):
#                    return False
#         return True
    
    
      def _check_min_date(self, cr, uid, ids, context=None): 
          """ 
            Constrain function to check the planned execution Date
            return True
            @return: Boolean True or False  
            """
            #pro_obj=self.pool.get('product.product')
          for rec in self.browse(cr, uid, ids, context=context):
                
              if rec.min_date < rec.date:
                 return False
            
          return True
      
      
      
      def _check_category_against_period_type(self, cr, uid, ids, context=None): 
          """ 
            Constrain function to check the planned execution Date
            return True
            @return: Boolean True or False  
            """
            #pro_obj=self.pool.get('product.product')
          for rec in self.browse(cr, uid, ids, context=context):
                
              if rec.period_type == 'consum' and  rec.category_id.custody:
                 return False
             
              if rec.period_type in ['const','temp'] and  not rec.category_id.custody:
                 return False
          return True
      
      
      
      
      def write(self, cr, uid, ids, vals, context=None):
          """
          Inherit Write Mehtod to Put Constraint function to check the category of items tp prevent the changing of order when it contains custodies. """
          
          
          res = super( stock_picking_out , self).write(cr, uid, ids, vals, context)
          check_order_categ = False
          check_order_items = False
          if type(ids) != list:
		ids =  [ids]
          for rec in self.browse(cr, uid,ids):
                  
		  if rec.category_id:
		            if rec.category_id.custody == True:
		               check_order_categ = True
		                
		            for line in rec.move_lines:
		                if line.product_id.custody:
		                    check_order_items = True
		            if rec.period_type == 'consum' and ( check_order_categ == True or check_order_items == True ):
		               raise osv.except_osv(_('Conflict Error'), _('You have Conflict Between The Category of Items and Purpose of the Order and  Items ...'))
          return res
          
          
          
          
          
          
          
      _inherit = "stock.picking.out"
      _columns = {
         'purpose' : fields.char('Purpose',size=64, ),
         'custody_type' : fields.selection([('department','Administrative'),('personal' , 'Personal')], 'Custody Type',),
         'period_type' : fields.selection([('consum' , 'Consumable'),('temp','Temparory'),('const' , 'Constant'),], 'Period Type',),
         'expacted_return_date' : fields.date('Expected Date',),
         
         'signed' : fields.boolean('Signed' ,),
         'custody_line_ids' : fields.one2many('custody.order.lines' , 'order_id' , 'Custody Lines') ,
         'order_type': fields.selection([('admin', 'Adminsitrative'),
                                        ('tech', 'Techincal'),
            ],
            'Order Type', select=True,),
           

                 }



      _constraints = [
        (_check_min_date, 'Min Date must be bigger than Order Date ',['min_date']),
        (_check_category_against_period_type, 'You have Conflict Between The Category of Items and Purpose of the Order and  Items ...',['min_date']),

                     ]
      
      _sql_constraints = [

                   ('check_expacted_return_date',"CHECK(expacted_return_date >= date)",_("Expacted Return Date must be bigger than Order Date!")) ,
                   ('check_min_date',"CHECK(min_date >= date)",_("Min Date must be bigger than Order Date!")) ,

                   ]   

      


      
    
      def onchange_category_id(self, cr, uid ,ids,category_id,move_lines,context=None):
          res = super(stock_picking_out,self).onchange_category_id(cr, uid ,ids,category_id,move_lines,context=None)
          if category_id:
              categ_rec = self.pool.get('product.category').browse(cr,uid,[category_id])[0]
              if not res:
                 res = {'value' : { }}
              if categ_rec.custody:
                    res['value']['period_type'] = 'const'
              else :
                    res['value']['period_type'] =  'consum'
              if categ_rec.technical:
                   res['value']['order_type'] = 'tech'
              else :
                   res['value']['order_type'] = 'admin'
                   
          return res
          

      def draft_complete(self, cr, uid, ids, *args):
        """ Confirms picking directly from draft state.
        @return: True
        """
    
        
        
        rec = self.browse(cr,uid,ids)[0]
        
        if (rec.period_type != 'consum' and not rec.custody_line_ids) :
           raise osv.except_osv(_('No Custodies Line '), _('This Order For Exchange Asset From Stock . Please Fill the Custody Lines ...'))
        if rec.custody_line_ids:             
             for line in rec.custody_line_ids:
                 self.pool.get('custody.order.lines').write( cr, uid, [line.id], {'order_state' : 'complete'})
        


        return super(stock_picking_out,self).draft_complete(cr, uid, ids, *args)
    
    
    
    
    
    
    
    
      def draft_force_assign(self, cr, uid, ids, context=None):
          
          """ inherit to draft_force_assign to make custody id readable """
           
           
           
          custody_lines_obj = self.pool.get('custody.order.lines')
           
          rec = self.browse(cr,uid,ids)[0]
          wf_service = netsvc.LocalService('workflow')

          
          
          
          if rec.custody_line_ids:             
             for line in rec.custody_line_ids:
                 custody_lines_obj.write(cr,uid,[line.id], {'order_state'  : 'complete'  })
          
          wf_service.trg_validate(uid, 'stock.picking', rec.id,
                    'button_confirm', cr)
          if rec.order_type == 'admin' :     
                   send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_administrative_user', "New Stock Exchange Order", self.message,context=context)
          else:
                   send_mail(self, cr, uid, ids[0] , 'purchase_ntc.group_technical_user', "New Stock Exchange Order", self.message,context=context)
          return super(stock_picking_out,self).draft_force_assign(cr, uid, ids, context=context)


    
      def action_assign(self, cr, uid, ids, context=None):
        """ inherit to action_assign to check picking type """
        


        rec = self.browse(cr,uid,ids)[0]
        for line in rec.move_lines :
            if ((line.product_id.custody == True) and not rec.custody_line_ids) :
                raise osv.except_osv(_('No Custodies Line '), _('This Order For Exchange Asset From Stock . Please Fill the Custody Lines ...'))
            
        if rec.custody_line_ids :
          for custody in rec.custody_line_ids:
            if not custody.custody_id :
                   raise osv.except_osv(_('Custodies Line Not Selected'), _('Please Fill The Custodies Field '))
               
        flag_admin = self.pool.get('res.users').has_group(cr, uid, 'purchase_ntc.group_administrative_user')
        flag_tech = self.pool.get('res.users').has_group(cr, uid, 'purchase_ntc.group_technical_user')
        
        if flag_admin and rec.order_type == 'tech':
            raise osv.except_osv(_('Permission Denied'), _('You Havent Rights to Sign on this Order Because its Technical Order'))
        if flag_tech and rec.order_type == 'admin':
            raise osv.except_osv(_('Permission Denied'), _('You Havent Rights to Sign on this Order Because its Administrive Order'))
        
        
        return super(stock_picking_out,self).action_assign(cr, uid, ids, context)
    
    
      
          
          
      def create_custody_line(self,cr,uid,ids,context=None):
          """ 
        Function For Create Custodies Lines .

            
        @return: Boolean True
          """ 
          if not isinstance(ids, list):
             ids = [ids] 
          custody_line_obj = self.pool.get('custody.order.lines')
          emp_obj = self.pool.get('hr.employee')
          category_obj = self.pool.get('account.asset.category')

          for order in self.browse(cr, uid, ids, context=context): 
              
              if not order.move_lines:  
                 raise osv.except_osv(_('Error !'), _('Please Fill the Products Firstly.'))

                  
              
              if order.custody_line_ids:
                 raise osv.except_osv(_('Error !'), _('The Custody Lines already Created.'))
              emp_id = emp_obj.search(cr ,uid ,[('user_id', '=' , uid )]  )
              if not emp_id:
                     emp_id = [False]
              else :
                 emp_id = [False]
              
              for line in order.move_lines:
                if line.product_id.custody:
                  if not line.product_id.asset_categ_id:
                     raise osv.except_osv(_('Category Not Found !'), _('The Items havent asset category.'))
                  
                  for quantity in range(int(line.product_qty)):
		              custody_id = custody_line_obj.create(cr ,uid , {  'category_id' : line.product_id.asset_categ_id.id,

		                                                           'employee_id' : emp_id[0],
		                                                           'order_id' : order.id 

                                                                      ,} ,context=context)

          
          return True

      def sign_custody_lines(self ,cr ,uid ,ids ,context=None):
          """ 
          Function For Sign Custodies Lines to Employees or Department.

            
           @return: Boolean True
          """ 
          picking_obj = self.pool.get('stock.picking')
          employee_obj = self.pool.get('hr.employee')
          user_obj = self.pool.get('res.users')
          custody_obj = self.pool.get('account.asset.asset')
          asset_obj = self.pool.get('account.asset.asset')
          asset_log_obj = self.pool.get('asset.logs')
          parent_res = { }
          lines_res = { }

          for order in picking_obj.browse(cr, uid, ids, context=context): 





              if not order.custody_line_ids:  
                 raise osv.except_osv(_('Error !'), _('Please Create The Custody Lines First.'))

              

              


              for line in order.custody_line_ids:
                  if not line.custody_id:  
                     raise osv.except_osv(_('Error !'), _('Please Make Sure You Filled All Custodies Data First.'))
                  custody_id = custody_obj.search(cr,uid,[('id' , '=' , line.custody_id.id )])
                  user = False
                  if line.employee_id.user_id:
                      user = line.employee_id.user_id.id
                  parent_res = {

                   'state' : 'open',
                   'custody_type' : order.custody_type ,
                   'current_employee' : line.employee_id.id ,
                   'period_type' : order.period_type,
                   'expacted_return_date' : order.expacted_return_date or False,
                   'stock_location_id' : line.custody_location_id.property_customer_location.id,
                   'department_id' : order.department_id.id,
                   'custody_location_id' : line.custody_location_id.id ,
                   'user_id' : user,
                                }
                
                 
                  lines_res = {
                      'custody_log_id' : custody_id[0] ,
                      'department_id' : order.department_id.id,
                      'action_type' : 'recieve' ,
                      'action_date' : time.strftime('%Y-%m-%d') ,
                      'employee_id' : line.employee_id.id or False,
                         }
                  
                  log_id = asset_log_obj.create(cr,uid,lines_res)
                  custody_obj.write(cr,uid,custody_id, parent_res ,context=context)

          self.write(cr,uid,ids,{'signed' : True})        


          return True














class stock_picking(osv.Model):











      def _check_min_date(self, cr, uid, ids, context=None): 
          """ 
            Constrain function to check the planned execution Date
            return True
            @return: Boolean True or False  
            """
            #pro_obj=self.pool.get('product.product')
          for rec in self.browse(cr, uid, ids, context=context):
                
              if rec.min_date < rec.date:
                 return False
            
          return True
    
    

      _inherit = "stock.picking"
      _columns = {
          'purpose' : fields.char('Purpose',size=64, ),
         'custody_type' : fields.selection([('department','Administrative'),('personal' , 'Personal')], 'Custody Type',),
         'period_type' : fields.selection([('consum' , 'Consumable'),('temp','Temparory'),('const' , 'Constant'),], 'Period Type',),
         'expacted_return_date' : fields.date('Expected Date',),
         'signed' : fields.boolean('Signed' ,),
         'custody_line_ids' : fields.one2many('custody.order.lines' , 'order_id' , 'Custody Lines') ,
         'order_type': fields.selection([('admin', 'Adminsitrative'),
                                        ('tech', 'Techincal'),
            ],
            'Order Type', select=True,),
           


                 }

      
      


      _constraints = [
        (_check_min_date, 'Min Date must be bigger than Order Date ',['min_date']),
    ]
      
      
      
      
              
      _sql_constraints = [

                   ('check_expacted_return_date',"CHECK(expacted_return_date >= date)",_("Expacted Return Date must be bigger than Order Date!")) ,
                   ('check_min_date',"CHECK(min_date >= date)",_("Min Date must be bigger than Order Date!")) ,

                   ]     
        
        
      def draft_force_assign(self, cr, uid, ids, *args):
          
          """ inherit to draft_force_assign to make custody id readable """
           
           
           
          custody_lines_obj = self.pool.get('custody.order.lines')
           
          rec = self.browse(cr,uid,ids)[0]
          
          
          
          
          if rec.custody_line_ids:             
             for line in rec.custody_line_ids:
                 custody_lines_obj.write(cr,uid,[line.id], {'order_state'  : 'complete'  })
          
          
          return super(stock_picking_out,self).draft_force_assign(cr, uid, ids, *args)



      def draft_complete(self, cr, uid, ids, *args):
        """ Confirms picking directly from draft state.
        @return: True
        """
    
        
        
        rec = self.browse(cr,uid,ids)[0]
        
        if (rec.period_type != 'consum' and not rec.custody_line_ids) :
           raise osv.except_osv(_('No Custodies Line '), _('This Order For Exchange Asset From Stock . Please Fill the Custody Lines ...'))

        return super(stock_picking,self).draft_complete(cr, uid, ids, *args)
    
    
      def action_assign(self, cr, uid, ids, context=None):
        """ inherit to action_assign to check picking type """
        

        rec = self.browse(cr,uid,ids)[0]
        for line in rec.move_lines :
            if (( line.product_id.custody == True) and not rec.custody_line_ids) :

               raise osv.except_osv(_('No Custodies Line '), _('This Order For Exchange Asset From Stock . Please Fill the Custody Lines ...'))

        if rec.custody_line_ids :
		  for custody in rec.custody_line_ids:
		    if not custody.custody_id :
		           raise osv.except_osv(_('Custodies Line Not Selected'), _('Please Fill The Custodies Field '))
        
        return super(stock_picking,self).action_assign(cr, uid, ids, context)  
            


    
      def action_done(self, cr, uid, ids, context=None):
        """
        inherit action_done function in stock picking class 
        and create custodies depend on some conditions 

        @return: True
        """

        super(stock_picking, self).action_done(cr, uid, ids, context=context)

        custody_order_obj = self.pool.get('asset.pact.order')
        
        for rec in self.browse(cr,uid,ids):
            if rec.type == 'out':
               if rec.location_id.custody == True :
		    res = {


		       'department_id' : rec.department_id.id,
		       'purpose' : rec.stock_journal_id.name


		         }

		    
		    order_id = custody_order_obj.search(cr ,uid ,[('source_document' , '=' , rec.id)])
		    custody_order_obj.write(cr,uid,order_id,res)

        return True







class custody_order_lines(osv.osv) :

        


        _name = "custody.order.lines"
        _columns = {
              'name': fields.related('custody_id', 'code', type='char', relation='account.asset.asset', string='Serial Code', store=True , readonly=True),
              'order_id' : fields.many2one('stock.picking.out' , 'Order' ),
              'custody_id' : fields.many2one('account.asset.asset' , 'Custody' ,),
              'category_id' : fields.many2one('account.asset.category' , 'Category' ,),
              'custody_location_id' :fields.many2one('account.asset.location' , 'Location' ),
              'employee_id' : fields.many2one('hr.employee','Responsible',),
              'custody_type' : fields.related('order_id', 'custody_type' ,  type='char' , store=True ,   readonly=True,),
              'order_state' : fields.related('order_id', 'state' ,  type='char' , store=True ,   readonly=True,),
                  }

        _sql_constraints = [
                   ('serial_code_uniq', 'unique(order_id,custody_id)', 'Serial Code For Item must be unique !'), 
                 ]
        




