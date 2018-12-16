
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
from base_custom.amount_to_text_ar import amount_to_text

class enrich_receive_notification(report_sxw.rml_parse):
    """ To manage enrich receive notification report """

    def __init__(self, cr, uid, name, context):
        super(enrich_receive_notification, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert':self._convert,
        })

    def _convert(self,cost):
    	return amount_to_text(cost)

report_sxw.report_sxw('report.enrich_receive_notification.report','payment.enrich.lines','addons/admin_affairs_payments/report/enrich_receive_notification.rml',parser=enrich_receive_notification,header=True)


