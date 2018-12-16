#coding: utf-8 
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from osv import osv
import pooler
from report import report_sxw
from base_custom.amount_to_text_ar import amount_to_text



class hall_report(report_sxw.rml_parse):
    """ To manage halls report """

    def __init__(self, cr, uid, name, context):
        super(hall_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'convert':self._convert,
            'get_time':self.get_time
        })
        self.context = context

    def _convert(self,cost):
    	return amount_to_text(cost)

    def get_time(self,record):
        if record.rent:
            record.write({'time_exceeded':datetime.now()})
    	return ''

report_sxw.report_sxw('report.flee_vehicle_log_contract_report.report', 'fleet.vehicle.log.contract', 'addons/service/report/hall_report.rml' ,parser=hall_report , header=True)
report_sxw.report_sxw('report.env_safety_report.report', 'fleet.vehicle.log.contract', 'addons/service/report/env_safety_report.rml' ,parser=hall_report , header=True)

