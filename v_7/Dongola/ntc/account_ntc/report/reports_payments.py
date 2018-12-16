# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class reports_payments(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(reports_payments, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
        })
        self.context = context
    
    def lines(self,invoice):
        vals = []
        number = 0
        if invoice.move_creation == 'voucher':
            for voucher in invoice.voucher_ids:
                vals.append({'number':voucher.number,
                            'date':voucher.date,
                            'amount':voucher.amount,
                            'state':voucher.state,
                           })
        if invoice.move_creation == 'invoice':
            if invoice.move_id:
                for line in invoice.move_id.line_id:
                    if invoice.account_id == line.account_id:
                        number+=1
                        if line.reconcile_id:
                            state = "paid"
                        elif line.reconcile_partial_id:
                            state = "partial_payment"
                        elif line.reconcile_id == False and line.reconcile_partial_id == False:
                            state = "not_paid"
                        vals.append({'number':number,
                                    'date':line.date_maturity,
                                    'amount':line.credit,
                                    'state':state,
                                   })
        return vals
        
report_sxw.report_sxw('report.report_payment', 'account.invoice', 'addons/account_ntc/report/reports_payments.rml', parser=reports_payments, header='portrait')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
