# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
import time
import datetime
from dateutil.relativedelta import relativedelta


#----------------------------------------
#employee retirement
#----------------------------------------
class employee_retirement(osv.osv_memory):
    _name = "employee.retirement"
    _columns = {
	    'company_id': fields.many2one('res.company', 'Company'),
            'dismissal_type' : fields.many2one('hr.dismissal', 'Termination Reason', required=True),
	    'date': fields.date('Date', required=True),
   		 }

    _defaults= {
      'date':time.strftime('%Y-%m-%d'),
           } 

    def check_emp_retirement(self,cr,uid,ids,context={}):
       """Retrieve employees who should retirement if they achieved retirement age.
       @return: Dictionary 
       """
       employee_obj = self.pool.get('hr.employee')
       employee_termination_obj = self.pool.get('hr.employment.termination')
       for retirement in self.browse(cr,uid,ids,context=context):
          domain = [('state','=','approved')]
          termination_ids = []
          if retirement.company_id:
             domain+=[('company_id','=',retirement.company_id.id)]
          emp_ids= employee_obj.search(cr,uid,domain,context=context)
          if emp_ids:
             for employee in employee_obj.browse(cr,uid,emp_ids,context=context): 
                if  employee.birthday:    
                   dt_birth = datetime.datetime.strptime(employee.birthday, "%Y-%m-%d")
                   age_pension = employee.company_id.age_pension or 0
                   retirement_date = str(dt_birth + relativedelta(years=age_pension))
                   if age_pension:
                      if retirement.date >= retirement_date :
                         check=employee_termination_obj.search(cr,uid,[('employee_id','=',employee.id),('dismissal_type','=',retirement.dismissal_type.id)],context=context)
                         if not check:
                            emp_retire_dict = {
				      #'company_id':employee.company_id.id,
				      'employee_id': employee.id,
				      'dismissal_date' :retirement_date, 
				      'birth_date':employee.birthday,
				      'dismissal_type':retirement.dismissal_type.id,
				     }
                            termination_id = employee_termination_obj.create(cr, uid, emp_retire_dict,context=context) 
                            termination_ids.append(termination_id)
       res= { 
			'name': 'Termination',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'hr.employment.termination',
			'type': 'ir.actions.act_window',
			'domain': [('id','in',termination_ids)],
		}
       return res

