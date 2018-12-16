# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import fields, osv

class salary_scale_report(osv.osv_memory):
    _name = "salary.scale.report"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
        'payroll_id': fields.many2one('hr.salary.scale', 'Salary Scale',required=True),
        'degree_ids' : fields.many2many('hr.salary.degree','salary_rep_degrees_rel', 'report_id', 'degree_id', 'Degrees', domain="[('payroll_id','=',payroll_id)]", required=True), 
		}


    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.salary.scale',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'salary.scale',
            'datas': datas,
            }
 
