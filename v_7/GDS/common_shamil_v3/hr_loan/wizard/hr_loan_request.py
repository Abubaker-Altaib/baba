# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import mx

#----------------------------------------
#add loan to employee
#----------------------------------------
class hr_employee_loan_request(osv.osv_memory):

    _name ='hr.employee.loan.request'
    _description = "Loan Request "
    _columns = {
        'company_id': fields.many2one('res.company','Company',required=True),
        'department_id': fields.many2one('hr.department', 'Department',required=True),
	'loan_id': fields.many2one('hr.loan', 'Loan',required=True ),
        'employee_id': fields.many2many('hr.employee','loann_employee','loan_empl','loans_id',"Employee"),
        'start_date' :fields.date("Start Date", required= True),
        'end_date' :fields.date("End Date"),
         }
    _defaults = {

        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee.loan.request', context=c), 
        'employee_id': False
    }
    def onchange_employee(self, cr, uid, ids, department_id,context={}):
		#employee_type domain
		emp_obj = self.pool.get('hr.employee')
		company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
		contractors = company_obj.loan_contractors
		employee = company_obj.loan_employee
		recruit = company_obj.loan_recruit
		trainee = company_obj.loan_trainee
		employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
                employee_domain['employee_id']+=[('state', '=', 'approved'),('department_id','=',department_id)]
		domain = {'employee_id':employee_domain['employee_id']}
		return {'domain': domain}

    def assign_emp_loan(self, cr, uid, ids, context):
        """
	Method that adds loan same information for group of employees in same
	department.

        @return: Dictionary 
        """
        for l in self.browse( cr, uid,ids):
           employee_loan_obj = self.pool.get('hr.employee.loan')
	   empl_list = [x.id for x in l.employee_id]
           for employee in empl_list:
               emp_loan_dict = {
                 'employee_id': employee,
                 'department_id': l.department_id.id,
                 'loan_id': l.loan_id.id,
                 'loan_amount': 0.0,
                 'start_date': l.start_date,
	                           }
               emp_loan_id =  employee_loan_obj.create(cr,uid,emp_loan_dict,context={})
               wf_service = netsvc.LocalService("workflow")
	       res = wf_service.trg_validate(uid,'hr.employee.loan',emp_loan_id, 'request', cr)
           return {}



