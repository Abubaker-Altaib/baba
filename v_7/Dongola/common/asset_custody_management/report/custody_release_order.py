# -*- coding: utf-8 -*-
##############################################################################
#
# NCTR, Nile Center for Technology Research
# Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time

from report import report_sxw

class custody_release_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(custody_release_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })


report_sxw.report_sxw('report.custody_release_order','custody.release.order','addons/custody_management/report/custody_release_order.rml',parser=custody_release_order,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
