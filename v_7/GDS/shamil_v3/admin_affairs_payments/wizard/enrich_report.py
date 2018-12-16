# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv
import time
from datetime import datetime,date,timedelta


# Enrich Report Class

class enrich_report_wiz(osv.osv_memory):
    def _get_months(sel, cr, uid, context):
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    _name = "enrich.report.wiz"
    _description = "Enrich Report Wiz"

    _columns = {
        'month': fields.selection(_get_months,'Month', required=True,),
        'year': fields.integer('Year',size=32, required=True,),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
	'payment_enrich':fields.many2one('payment.enrich', 'Payment Enrich',required=True),
    }
    _defaults = {
                'year': int(time.strftime('%Y')),
 		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
                }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'payment.enrich',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enrich_report.report',
            'datas': datas,
            }
enrich_report_wiz()
    
