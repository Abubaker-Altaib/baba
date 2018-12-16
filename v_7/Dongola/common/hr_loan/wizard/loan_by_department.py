# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields, orm
import time

class loan_by_department(osv.osv_memory):
    _name = "loan.by.department"
    _columns = {
	        'department_id': fields.many2many('hr.department','loan_department_rel','department_id','loan_id', 'Departments',required=True ),
		    'company_id': fields.many2one('res.company', 'Company',required=True ),
		    'loan_id': fields.many2one('hr.loan', 'Loan',required=True ),
		    'start': fields.date("Start", required= True),
	            'to_date' : fields.date("To" ,required= True),
   	}
    _defaults = {
       
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'loan.by.department', context=c), 
	
    }

    _sql_constraints = [
       	 	('date_check', 'CHECK ( start < to_date)', "The start date must be anterior to the to date."),
    ]

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee.loan',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'loan.by.department',
            'datas': datas,
            }
