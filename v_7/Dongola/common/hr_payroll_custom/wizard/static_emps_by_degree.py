# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv

class static_degree(osv.osv_memory):
     _name = "static.degree"
     _columns = {
          'payroll_id' : fields.many2one('hr.salary.scale', 'Scale',required=True),
		  'degree_ids' : fields.many2many('hr.salary.degree','static_emp_degrees_rel', 'static_id', 'degree_id', 'Degrees', domain="[('payroll_id','=',payroll_id)]", required=True), 
               
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
            'report_name': 'degree_based',
            'datas': datas,
            }

   
static_degree()
