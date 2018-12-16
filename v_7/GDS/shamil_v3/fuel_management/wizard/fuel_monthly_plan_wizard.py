# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv
import time
from tools.translate import _

# fuel monthly plan wizard

class fuel_monthly_plan_wizard(osv.osv_memory):
    """
    To manage fule monthly plane """

    _name = "fuel.monthly.plan.wizard"
    _description = "Fuel Monthly Plan"

    def _get_months(sel, cr, uid, context):
       """
        To read plane monthes .

        @return: list of months
       """
       months=[(str(n),str(n)) for n in range(1,13)]
       return months
    _rec_name="month"
    _columns = {
        'date': fields.date('Plan Date', required=True,), 
        'month': fields.selection(_get_months,'Month', required=True),
        'year': fields.char('Year',size=32, required=True),
        'type_plan':fields.selection([('constant_fuel','Constant Fuel'),('mission_extra','Mission Extra')], 'Plan Type',required=True),
        'type':fields.selection([('departments','Departments'),('general_dapartments','')], 'Plan Type',required=True),
        'dept_cat_id':fields.many2one('hr.department.cat', 'Department Category',),
        'company_id':fields.many2one('res.company', 'Company',required=True),
        'extra_fuel_lines': fields.one2many('extra.fuel.lines','monthly_plan_id','Extra Fuel',required=True),
        
    }
    _defaults = {
        'year': str(time.strftime('%Y')),
        'date': time.strftime('%Y-%m-%d'),
        'type_plan':'constant_fuel',
		}

    def get_child_dept(self,cr,uid,dept_id,context=None):
        """
        To get department 
        @param dept_id: department_id
        @return: department ids 
        """
        department_obj = self.pool.get('hr.department')
        reads = department_obj.read(cr, uid, [dept_id], ['id','child_ids'], context=context)
        child_ids=[]
        for record in reads:
           if record['child_ids']:
              child_ids=record['child_ids']
              for child in record['child_ids']:
                 child_ids+=self.get_child_dept(cr,uid,child,context=context)
                 

        return child_ids

    def compute_plan(self, cr, uid, ids, context=None):
        """
        To compute fule plane 

        @return: empty dictionary
        """
        fuel_plan_obj= self.pool.get('fuel.plan')
        fuel_qty_obj= self.pool.get('fuel.quantity')
        fuel_qty_line_obj= self.pool.get('fuel.qty.line')
        vehicle_obj= self.pool.get('fleet.vehicle')
        department_obj = self.pool.get('hr.department')
        department_extra_obj = self.pool.get('extra.fuel.lines')
        center_obj = self.pool.get('account.analytic.account')
        user_obj = self.pool.get('res.users')

        for record in self.browse(cr,uid,ids,context=context):
           check_plan = fuel_plan_obj.search(cr,uid,[('month','=',record.month),('year','=',record.year),('company_id','=',record.company_id.id),('type_plan','=','constant_fuel')],context=context)
           if check_plan and record.type_plan!='mission_extra':
	            raise osv.except_osv('ERROR', 'Fuel Plan For This Month Already Computed')
#           extra fuel quantity check
           for line in record.extra_fuel_lines:
               if line.product_qty <= 0:
                   raise osv.except_osv('Fuel quantity!!', 'Extra fuel quantity must be bigger than zero')
               if line.budget_depart<line.product_id.standard_price*line.product_qty and record.type_plan=='constant_fuel':
                     raise osv.except_osv('Department Budget', 'The Budget for this department is less than quntatiy') 
           domain = []
           user_id= user_obj.browse(cr,uid,[uid],context=context)[0]
           fuel_plan_dict = {
           	'date':record.date,
           	'month':record.month,
           	'year':record.year,
                'company_id':record.company_id.id,
                #'department_id':user_id.context_department_id and user_id.context_department_id.id,
                'department_id':1,
                'type_plan':record.type_plan,
				}
           plan_id = fuel_plan_obj.create(cr,uid,fuel_plan_dict,context=context)
           department_dict={
                 	'plan_id': plan_id,
			'fuel_type': 'extra_fuel',
                        
					}
           for line in record.extra_fuel_lines:
              vehicle_dict = []
              #department_extra_ids= department_extra_obj.search(cr,uid,[('id','=',line.id)],context=context)
              for extra in department_extra_obj.browse(cr,uid,[line.id],context=context):
                  department_dict.update({'department_id':extra.department_id_fuel.id})
                  extra_fuel_id = fuel_qty_obj.create(cr,uid,department_dict,context=context)
                  vehicle_dict={
                	   'qty_id': extra_fuel_id,
			          }
                  #for line in record.extra_fuel_lines:
                  vehicle_dict.update({
                	'product_id': line.product_id.id,
                	'product_qty': line.product_qty,
                	'product_uom': line.product_id.uom_id.id,
                	'price_unit': line.product_id.standard_price,
                	'name': u' وقود اضافي' + line.product_id.name,
                        'department_id': line.department_id_fuel.id,})
                  fuel_qty_line_obj.create(cr,uid,vehicle_dict,context=context) 
           if record.type=='general_dapartments':
              
                domain += [('cat_id','=',record.dept_cat_id.id),('company_id','=',record.company_id.id)]
           elif  record.type=='departments':   
                domain += [('company_id','=',record.company_id.id)]
           anltic_dep2=[]
           department_ids= department_obj.search(cr,uid,domain,context=context)
           for dept in department_obj.browse(cr,uid,department_ids,context=context):
              child_ids = [dept.id]
              #if record.type=='general_dapartments':
               #  child_ids +=self.get_child_dept(cr,uid,dept.id,context=context)
              vehicle_ids= vehicle_obj.search(cr,uid,[('department_id','in',tuple(child_ids)),('status','=','active'),('monthly_plan','=',True)],context=context)
              if vehicle_ids:
                 department_dict.update({
                 	'department_id': dept.id,  
			'fuel_type': 'fixed_fuel',
					})
                 fuel_qty_id= fuel_qty_obj.create(cr,uid,department_dict,context=context)

                 for vehicle in vehicle_obj.browse(cr,uid,vehicle_ids,context=context):
                    if vehicle.fuel_lines:       
                                     
                        vehicle_dict.update({
                    	    'vehicles_id': vehicle.id,
                	        'department_id': vehicle.department_id.id,
                	        'product_id': vehicle.fuel_lines[0].product_id.id,
                	        'product_qty': vehicle.fuel_lines[0].product_qty,
                	        'product_uom': vehicle.fuel_lines[0].product_id.uom_id.id,
                	        'price_unit': vehicle.fuel_lines[0].product_id.standard_price,
                	        'qty_id': fuel_qty_id,
                	        'name': vehicle.name,
			                     })
                        fuel_qty_line_obj.create(cr,uid,vehicle_dict,context=context)                     	
              
           
        return {}


class extra_fuel_lines(osv.osv_memory):
    """
    To manage extra fule lines  """

    _name = "extra.fuel.lines"
    _rec_name="product_id"
    _columns = {
        'product_id': fields.many2one('product.product', 'Fuel', required=True),
        'product_qty': fields.float('Quantity', required=True, digits=(16,2)),
        'department_id_fuel': fields.many2one('hr.department', 'Fuel Department',),
        'monthly_plan_id':fields.many2one('fuel.monthly.plan.wizard', 'Plan',),
        'budget_depart': fields.float('Budget Department', digits=(16,2)),

    }

    #_sql_constraints = [
     #   ('uniq_product', 'unique (product_id,monthly_plan_id)', 'The fuel type must be unique !')
    # ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
