# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv
import time
from datetime import datetime,date,timedelta
from tools.translate import _

class enrich_report_wiz(osv.osv_memory):
    """ To manage enrich report wizard """
    _name = "enrich.report.wiz"

    _description = "Enrich Report Wizard"

    _columns = {
        'month': fields.selection([(str(n),str(n)) for n in range(1,13)],'Month', required=True,),
        'year': fields.integer('Year',size=32, required=True,),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
        'payment_enrich': fields.many2one('payment.enrich', 'Payment Enrich',required=True, ondelete='cascade'),
    }

    _defaults = {
        'year': int(time.strftime('%Y')),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        browse = self.browse(cr, uid, ids, context=context)[0]
        if browse.month != browse.payment_enrich.month:
            raise osv.except_osv(_("ValidateError"),_('The Enrich Month Must Equals To Month Of The Report!'))
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enrich_report.report',
            'datas': {
                'ids': [browse.payment_enrich.id],
                'model': 'payment.enrich',
            },
        }
