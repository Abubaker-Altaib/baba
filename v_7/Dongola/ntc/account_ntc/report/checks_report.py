# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, orm
from openerp.tools.translate import _
from report import report_sxw
from account_custom.common_report_header import common_report_header
from datetime import datetime
import time

class check_report(report_sxw.rml_parse, common_report_header):

    _description = "Not Delivered Checks and Exchanges"

    
    globals()['total_amount']=0.0
    def __init__(self, cr, uid, name, context=None):
        super(check_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'line':self.get_data,
            'total':self.get_total,
        })
        self.context = context

    def get_data(self,data):
        journal= data['form']['journal_type']
        globals()['total_amount']=0.0
        check_log_pool = self.pool.get('check.log')

        value = []
        domain=[('status','=','active'), ('check_delivered', '=', False), ]
        if journal == 'bank':
            domain +=[('journal_id.type', '=', 'bank')]
        if journal == 'cash':
            domain +=[('journal_id.type', '=', 'cash')]
        check_ids= check_log_pool.search(self.cr, self.uid, domain)

        for check in  check_log_pool.browse(self.cr, self.uid, check_ids):
            globals()['total_amount'] += check.name.amount and check.name.amount or 0.0
            if check.name:
                value.append({
                    'partner': check.name.partner_id.name,
                    'date': check.name.date,
                    'amount': check.name.amount,
                    'check_no': check.check_no
                    })

        

        return value

    def get_total(self,data):
    
        return globals()['total_amount']

report_sxw.report_sxw('report.account.delivered.check.ntc', 'check.log', 'addons/account_ntc/report/checks_report.rml', parser=check_report, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
