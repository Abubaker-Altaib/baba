# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from osv import osv ,fields


class salary_list_total(osv.osv_memory):
    _name = "salary.list.total"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
	    'month': fields.selection(_get_months,'Month', required=True),
	    'year': fields.integer('year',required=True ),
		}

    _defaults = {
        'year': int(time.strftime('%Y')),
		}


    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.payroll.main.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'salary_list_total',
            'datas': datas,
            }

