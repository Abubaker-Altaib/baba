#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class vehicles_insurance_report(report_sxw.rml_parse):
    """ To manage vehicles insurance report """

    def __init__(self, cr, uid, name, context):
        super(vehicles_insurance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

report_sxw.report_sxw('report.veh_insurance', 'fleet.vehicle.log.contract', 'addons/service/report/vehicles_insurance_report.rml' ,parser=vehicles_insurance_report , header=False)
