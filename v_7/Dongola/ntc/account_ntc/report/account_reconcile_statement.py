# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import re
import datetime
from openerp.osv import osv, orm
from openerp.tools.translate import _
from report import report_sxw
from account_custom.common_report_header import common_report_header

class account_cash_reconcile(report_sxw.rml_parse, common_report_header):

    _description = "Cash Reconcilation"

    globals()['total_amount']=0.0

    def __init__(self, cr, uid, name, context=None):
        super(account_cash_reconcile, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'line_type_sum':self.line_type_sum,
            'report_data':self.report_data,
            'total':self._gettotal,
        })
        self.context = context

    def report_data(self, statement):
        voucher_pool = self.pool.get('account.voucher')
        statement_date = datetime.datetime.strptime(statement.date, '%Y-%m-%d')
        domain = [('state','in',['pay']), ('date','=',statement_date), ('pay_journal_id','=',statement.journal_id.id),('pay_type','=','cash')]
        voucher_ids = voucher_pool.search(self.cr, self.uid, domain)
        val = []
        globals()['total_amount']=0.0
        for voucher in voucher_pool.browse(self.cr, self.uid, voucher_ids):
            globals()['total_amount'] += voucher.amount
            val.append({'number':voucher.number,
                            'partner':voucher.partner_id.name,
                            'date':voucher.date,
                            'amount': voucher.amount,
                            })
        return val

    def _gettotal(self,data):
    
        return globals()['total_amount']

    def line_type_sum(self, line_type):
        expens_sum = 0
        revenu_sum = 0
        res = []
        for line in line_type.line_ids:
            if line.line_type == 'out_line':
                expens_sum += line.amount
            if line.line_type == 'in_line':
                revenu_sum += line.amount
        res.append({ 'expenses' : expens_sum,
                'revenues' : revenu_sum,
              })
        return res
    
report_sxw.report_sxw('report.account.reconcile.statement.ntc', 'account.bank.statement', 'addons/account_ntc/report/account_reconcile_statement.rml', parser=account_cash_reconcile, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
