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

class pq_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(pq_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'user': self.pool.get('res.users').browse(cr, uid, uid, context)
        })
report_sxw.report_sxw('report.purchase_quote','pur.quote','../purchase_custom/report/pq_report.rml',pq_report)
