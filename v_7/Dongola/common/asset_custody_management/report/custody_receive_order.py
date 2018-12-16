# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time

from report import report_sxw

class custody_receive_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(custody_receive_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })


report_sxw.report_sxw('report.custody_receive_order','asset.pact.order','addons/asset_custody_management/report/custody_receive_order.rml',parser=custody_receive_order,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
