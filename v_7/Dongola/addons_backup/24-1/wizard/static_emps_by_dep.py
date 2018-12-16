# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv

class statistics_department(osv.osv_memory):
     _name = "statistics.department"
     _columns = {
       'company_id' : fields.many2one('res.company', 'Company',required=True),
	   'department_ids' : fields.many2many('hr.department','statistics_emp_rel', 'statistics', 'dept_id','Departments',  domain="[('company_id','=',company_id)]", required=True), 
               
      		    }
     _defaults = {
    	'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'statistics.department', context=c),
    }
     def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids':[],
             'model': 'hr.employee',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'statistics_emps',
            'datas': datas,
            }

   
statistics_department()
