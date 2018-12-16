# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw

class car_operation_accept(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(car_operation_accept, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw('report.car_operation_accept','car.operation','addons/car_operation/report/car_operation_accept.rml',parser=car_operation_accept, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
