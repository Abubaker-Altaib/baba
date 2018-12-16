# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time

from report import report_sxw

class delivery_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(delivery_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })


report_sxw.report_sxw('report.delivery_order.reports','stock.picking','addons/exchange/report/delivery_order.rml',parser=delivery_order)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
