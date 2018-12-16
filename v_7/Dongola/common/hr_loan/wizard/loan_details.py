# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
import time

class loan_details(osv.osv_memory):
    _name = "loan.details"

    def _get_months(sel, cr, uid, context):
       months=[(n,n) for n in range(1,13)]
       return months

    _columns = {
         'company_id': fields.many2one('res.company', 'Company',required=True ),
         'month': fields.selection(_get_months,'Month', required=True),
         'year': fields.integer('Year', required=True),
   	}
    _defaults = {
        'year': int(time.strftime('%Y')),
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'loan.details', context=c), 
    }
  
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
            'report_name': 'loan.details',
            'datas': datas,
            }
