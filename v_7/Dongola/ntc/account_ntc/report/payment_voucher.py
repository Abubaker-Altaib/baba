
# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler
from base_custom import amount_to_text_ar

class payment_voucher(report_sxw.rml_parse):
    """ To manage customer invoice payment voucher report """
    def __init__(self, cr, uid, name, context):
        super(payment_voucher, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'words':self.words
        })
    def words(self,number):
        return [{'word': amount_to_text_ar.amount_to_text(number)}]

report_sxw.report_sxw('report.account_invoice_payment_voucher.report','account.invoice','addons/account_ntc/report/payment_voucher.rml',parser=payment_voucher,header=True)


