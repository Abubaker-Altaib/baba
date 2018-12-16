# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw

class bankers_insurance_accept(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bankers_insurance_accept, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })


report_sxw.report_sxw('report.bankers_insurance_accept','bankers.insurance','addons/extra_insurance/report/bankers_insurance_accept.rml',parser=bankers_insurance_accept, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
