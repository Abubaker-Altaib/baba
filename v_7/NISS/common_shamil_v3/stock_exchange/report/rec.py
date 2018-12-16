# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class rec(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rec, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'toint' : self.toint ,
        })



    def toint(self,qty):
         return int(qty)

report_sxw.report_sxw('report.stock.rec.list','exchange.order','addons/stock_exchange/report/rec.rml',parser=rec)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:





