# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class products_request(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(products_request, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            #'lines': self.lines,
        })
        self.context = context
        
report_sxw.report_sxw('report.products_request_report', 'stock.picking.out', 'addons/stock_custom/report/products_request_report.rml', parser=products_request, header=False)
