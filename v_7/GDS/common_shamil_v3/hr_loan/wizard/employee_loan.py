# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv
import time

class employee_loans(osv.osv_memory):
    _name = "employee.loan.report"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months
    _columns = {
 		'company_id': fields.many2one('res.company', 'Company',required=True ),
	        'loan_id': fields.many2one('hr.loan','Loan',required=True ),
		'employee_ids': fields.many2many('hr.employee','loan_empl_relation','loans_employees_id','loan_employe_id', 'Employees',required=True ),

   	}
    _defaults = {
       
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'employee.loan.report', context=c), 
        'employee_ids': False
	
    }

    def onchange_employee(self, cr, uid, ids, company_id,context={}):
		#employee_type domain
		emp_obj = self.pool.get('hr.employee')
		company_obj = self.pool.get('res.company').browse(cr, uid, company_id)
		contractors = company_obj.loan_contractors
		employee = company_obj.loan_employee
		recruit = company_obj.loan_recruit
		trainee = company_obj.loan_trainee
		employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
                employee_domain['employee_id']+=[('state', '=', 'approved'),('company_id','=',company_id)]
		domain = {'employee_ids':employee_domain['employee_id']}
		return {'domain': domain}

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.loan.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'employee.loan',
            'datas': datas,
            }




