# coding: utf-8 
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from datetime import timedelta
from openerp import tools
import netsvc
from openerp.tools.translate import _
from openerp.osv import osv, fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT







class hr_holidays(osv.Model):
      _inherit = "hr.holidays"

      def holidays_validate(self, cr, uid, ids, context=None):
          """ Inherit Vaildate Method in HR Holidays """
          
          super(hr_holidays ,self).holidays_validate(cr, uid, ids, context=context)
          
          grant_order_obj = self.pool.get("granted.rights.order")
          grant_order_lines_obj = self.pool.get("granted.rights.order.lines") 
          department_obj = self.pool.get('hr.department')
          
          
          manager = False
          for rec in self.browse(cr,uid,ids):
	      if rec.holiday_status_id.alternative_emp:
		      dep_ids = department_obj.search(cr,uid,[('manager_id','=',rec.employee_id.id)])
		      #if rec.employee_id.id == department_obj.browse(cr,uid,rec.department_id.id).manager_id.id :
		      if dep_ids:
				 manager = True

		      
		      grant_date =  datetime.strptime(rec.date_to, '%Y-%m-%d %H:%M:%S')
		        
		      grant_date = grant_date + timedelta(days=1)


		      if rec.date_to >=  time.strftime('%Y-%m-%d'):
			      order_id = grant_order_obj.create( cr, uid,{
				                        
				                        'delegation_type' : 'holiday',
				                        'holiday_order_id' :rec.id,
				                        'employee_donor' : rec.employee_id.id,
				                        'employee_candidate' : rec.alternative_employee.id,
				                        'start_grant_date'  : rec.date_from,                      
				                        'end_grant_date'  : grant_date,
				                        'department_id' : rec.department_id.id,
				                        'is_a_amanger' :  manager,

				                                          })
			      
			      res = grant_order_obj.on_change_donor_employee(cr, uid, order_id , rec.employee_id.id , context=context)
			      for rec in res['value']['donor_groups_ids']:
				  rec.update({ 'order_id' : order_id})
				  grant_order_lines_obj.create( cr, uid,rec )
              
          return True
      
      
      
      
      
class granted_rights_order(osv.Model):
    
    
      def _check_donor_groups_ids(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
          if not record.donor_groups_ids:
             return False
          return True
    
      def default_get(self, cr, uid, fields, context=None):
           
        """ Inherit Default Get Method To Add Employee Donor """  
           
           
        res = super(granted_rights_order, self).default_get(cr, uid, fields, context=context)
           
        employee_obj = self.pool.get('hr.employee')
        department_obj = self.pool.get('hr.department')
        manager = False
        donor_emp_id = []
        
        if uid != 1 :

           donor_emp_id = employee_obj.search(cr ,uid, [('user_id' , '=' , uid )])
           deparment_id = employee_obj.browse(cr,uid,donor_emp_id[0]).department_id.id
              
           if donor_emp_id[0] == department_obj.browse(cr,uid,deparment_id).manager_id.id :
               manager = True
       
            
            
            
            
            
            
            
                      
           if donor_emp_id :
               res.update({   'employee_donor': donor_emp_id[0], 
                              'department_id' : deparment_id,
                              'is_a_amanger' :  manager,
                              })
        return res  
           
           
           
            
      STATE = [
         ('draft', 'Draft Request'),
         ('granted','Granted'),
         ('revoked', 'Revoked'),
         ]
      
      
      _name = "granted.rights.order"
      _description = "Granted Rights Order"
      
      _columns = {
          
          'name' : fields.char('Name' , readonly=True),
          'order_date' : fields.datetime('Order Date ' ),
          'holiday_order_id' : fields.many2one('hr.holidays' , 'Holiday Order' ),
          'employee_donor' : fields.many2one('hr.employee' , 'Employee Donor' , required=True ),
          'employee_candidate' : fields.many2one('hr.employee' , 'Employee Candidate' , required=True),
          'start_grant_date' : fields.date('Start Grant Date ' ),
          'end_grant_date' : fields.date('End Grant Date ' ),
          'department_id' : fields.many2one('hr.department' , 'Department' , required=True , readonly=True),
          'donor_groups_ids' : fields.one2many('granted.rights.order.lines' , 'order_id' , 'Groups' ,),
          'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True,),
          'is_a_amanger' : fields.boolean('Is a Manager' , readonly=True),
          'state' : fields.selection(STATE , 'State' ),
          'note' : fields.text('Note' ),
          'delegation_type' : fields.selection([('holiday','Holiday'),('mission','Mission'),('training','Training')],'Delegation Type'),
          'active' : fields.boolean('Active'),
          'mission_order_id' : fields.many2one('hr.employee.mission' , 'Mission Order' ),
          
          
          
          
          } 
      
      
      
      
      _defaults = {

              #'name': lambda self,cr,uid,ctx=None: self.pool.get('ir.sequence').get(cr, uid, 'granted.rights.order', context=ctx) or '/',              
              'order_date': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S'),
              'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
              'state' : 'draft',
              'is_a_amanger' : False,
              'delegation_type' : 'holiday',
              'active' : 1
              
                  }
      _order = 'order_date desc, id desc'
      
#       _constraints = [
#       (_check_donor_groups_ids ,'You cant create grant order without rights.' , ['donor_groups_ids'] ),
#                    ]
      _sql_constraints = [
        ('start_grant_date_less_than_end_grant_date', 'CHECK (start_grant_date <= end_grant_date)', 'The Start Grant Date must be less End Grant Date.')
    ]
    
    
    
      def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'donor_groups_ids':[],
            #'name': self.pool.get('ir.sequence').get(cr, uid, 'granted.rights.order'),
        })
        return super(granted_rights_order, self).copy(cr, uid, id, default, context)
    
    
    
    
    
    
    
    
    
      def check_scheduler(self, cr, uid, ids, context=None):
          """ 
          Check Scheduler """
          
          self.pool.get('rights.scheduler').check_rights_scheduler(cr, uid,context=context)
          
          return True
      
      
      
      
      def on_change_donor_employee(self, cr, uid, ids ,donor_emp_id , context=None):
        """ 
        To get Groups that assigned to donor Employee.

        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res ={}
        result = []
        
        user_id = self.pool.get('hr.employee').browse(cr,uid,donor_emp_id).user_id.id
        
               
        conditions = ""
        if user_id :
           conditions = "rel.uid in (%s)"%user_id
        cr.execute("""select distinct rel.gid as group_id, 
                                      rel.uid as user_id ,  
                                      grp.comment as comment
                            from  res_groups_users_rel rel
                                  left join  res_groups grp on (grp.id = rel.gid )
                                  left join res_users usr on (usr.id = rel.uid)
                            where 
                                """ + conditions )
        
        res = cr.dictfetchall()
        
        for record in res :
            result.append({ 'group_id' : record['group_id'],
                            'order_id' : ids , 
                            'granted' : True ,
                            'name' : record['comment'],
                             })
        return {'value': { 'donor_groups_ids': result }}




      def on_change_holiday_order(self, cr, uid, ids , holiday_order_id , context=None):
        """ 
        To get Start And End Date For Granted Rights.

        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res ={}
        result = []
        
        holiday_order = self.pool.get('hr.holidays').browse(cr,uid,holiday_order_id )
        
        return {'value': { 'start_grant_date': holiday_order.date_from, 
                           'end_grant_date': holiday_order.date_to }}

      def on_change_mission_order(self, cr, uid, ids , mission_order_id , context=None):
        """ 
        To get Start And End Date For Granted Rights.

        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res ={}
        result = []
        
        mission_order = self.pool.get('hr.employee.mission').browse(cr,uid,mission_order_id )
        
        return {'value': { 'start_grant_date': mission_order.start_date, 
                           'end_grant_date': mission_order.end_date }}
    
    
    
      
class granted_rights_order_lines(osv.Model):
    
      _name = 'granted.rights.order.lines'
      
      _columns = {
          
          'name' : fields.char('Description' , readonly=True),
          'order_id' : fields.many2one('granted.rights.order' , 'Order Ref'),
          'group_id' : fields.many2one('res.groups' , 'Group'),
          'granted' : fields.boolean('Granted' ,),
          'already_granted' : fields.boolean('Already Granted' ,),
          'active' : fields.boolean('Active' ,),
          
          
          
          
                 }
          
          
      _defaults = {
              'granted': True,
              'active' :True,
              
                  }
          
    
    
    



    
    
    
class hr_department(osv.Model):
    
      _inherit = 'hr.department'
      _columns = {


            'pervious_manger_id' : fields.many2one('hr.employee' , 'Pervious Manger' , ),
            'manager_user_id' : fields.many2one('res.users' , 'User' , ),

                 }
      
      def onchange_manager(self, cr, uid, ids, manager_id , context=None):
          """ 
         
         
          """ 
          
          res = {'value':{} } 
          if manager_id :  
             manager_user_id = self.pool.get('hr.employee').browse(cr,uid,manager_id).user_id.id     
             res['value']['manager_user_id'] = manager_user_id or False
                      
          return res   
        
        
        
      
      
class res_users(osv.Model):
    
      _inherit = 'res.users'
      _columns = {


            'department_ids' : fields.one2many('hr.department', 'manager_user_id' ,'Department IDs'),



                 }
 
