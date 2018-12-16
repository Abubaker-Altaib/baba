# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import fields, osv

class employees_salary_report(osv.osv_memory):
    _name = "employees.salary.report"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
	    'month': fields.selection(_get_months,'Month', required=True),
	    'year': fields.integer('year',required=True ),
		}

    _defaults = {
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
		}


    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'employees.salary',
            'datas': datas,
            }
 
