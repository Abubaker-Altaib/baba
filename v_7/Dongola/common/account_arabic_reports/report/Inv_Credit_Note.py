# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from account_custom import amount_to_text_ar
from openerp.osv import osv, fields

class account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert':self.convert,
        })

    def convert(self, amount, cur):
        amt_ar = amount_to_text_ar.amount_to_text(amount, 'ar', cur)
        return amt_ar

report_sxw.report_sxw(
    'report.inv.credit.note',
    'account.invoice',
    'addons/account_arabic_reports/report/Inv_Credit_Note.rml',
    parser=account_invoice, header=False 
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
