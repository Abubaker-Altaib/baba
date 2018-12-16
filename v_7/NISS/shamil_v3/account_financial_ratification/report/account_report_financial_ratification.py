# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.tools.translate import _
from report import report_sxw
from account_custom.common_report_header import common_report_header  

class account_financial_ratification(report_sxw.rml_parse, common_report_header):
    
    _name = 'report.account.account.financial.ratification'

    def __init__(self, cr, uid, name, context=None):
        super(account_financial_ratification, self).__init__(cr, uid, name, context=context)
        self.auditLog = {'precomplete':0,'precomplete_date':0,'preclose':0,'preclose_date':0,'preapprove':0,'preapprove_date':0,'close':0,'close_date':0,'prepost':0,'prepost_date':0,'posted':0,'posted_date':0}
        self.localcontext.update({
            'get_users':self._get_users,
            'auditLog_fn':self._auditLog_fn,
        })
        self.context = context

    def _get_users(self, key):
        return self.auditLog[key]

    def _auditLog_fn(self, voucher_id):
        self.cr.execute("SELECT p.name,timestamp,aud.method FROM 	res_users usr \
                LEFT JOIN res_partner p on(p.id = usr.partner_id)\
                INNER JOIN audittrail_log aud ON aud.user_id = usr.id\
                WHERE aud.res_id = %s AND  aud.object_id = ( SELECT id FROM ir_model WHERE model='account.voucher' ) \
                ORDER BY  timestamp desc",(voucher_id,))
        res = self.cr.dictfetchall()
        for r in res:
            if r['method'] == 'precomplete' and self.auditLog['precomplete'] == 0:
                self.auditLog['precomplete'] = r['name']
                self.auditLog['precomplete_date'] =r['timestamp']

            if r['method'] == 'preclose' and self.auditLog['preclose'] == 0:
                self.auditLog['preclose'] = r['name']
                self.auditLog['preclose_date'] =r['timestamp']
            if r['method'] == 'prepost' and self.auditLog['prepost'] == 0:
                self.auditLog['prepost'] = r['name']
                self.auditLog['prepost_date'] =r['timestamp']

            if r['method'] == 'preapprove' and self.auditLog['preapprove'] == 0:
                self.auditLog['preapprove'] = r['name']
                self.auditLog['preapprove_date'] =r['timestamp']

            if r['method'] == 'close' and self.auditLog['close'] == 0:
                self.auditLog['close'] = r['name']
                self.auditLog['close_date'] =r['timestamp']

            if r['method'] == 'posted' and self.auditLog['posted'] == 0:
                self.auditLog['posted'] = r['name']
                self.auditLog['posted_date'] =r['timestamp']
                
report_sxw.report_sxw('report.account.account.financial.ratification', 'account.voucher', 'addons/account_financial_ratification/report/account_report_financial_ratification.rml', parser=account_financial_ratification, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
