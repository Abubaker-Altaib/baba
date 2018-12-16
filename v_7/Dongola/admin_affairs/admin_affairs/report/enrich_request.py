#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar


class enrich_request(report_sxw.rml_parse):
    """ To manage enrich request """

    def __init__(self, cr, uid, name, context):
        super(enrich_request, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'convert':self.convert,
        })
        self.context = context
    def convert(self, amount):
        return amount_to_text_ar(amount, 'ar')

report_sxw.report_sxw('report.enrich_request.report', 'payment.enrich', 'addons/admin_affairs/admin_affairs/report/enrich_request.rml' ,parser=enrich_request ,header=True)


