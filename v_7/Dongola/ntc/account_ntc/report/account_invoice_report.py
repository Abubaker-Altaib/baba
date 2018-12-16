# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar
class report_account_invoice(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(report_account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert':self.convert,
            #'lines': self.lines,
        })
        self.context = context
        
    def convert(self, amount):
        return amount_to_text_ar(amount, 'ar')
        
report_sxw.report_sxw('report.account.invoice.report', 'account.invoice', 'addons/account_ntc/report/account_invoice_report.rml' ,parser=report_account_invoice , header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
