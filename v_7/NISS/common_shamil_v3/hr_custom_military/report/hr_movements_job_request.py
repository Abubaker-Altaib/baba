# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from report import report_sxw
from account_custom.common_report_header import common_report_header

class hr_movements_job_request(report_sxw.rml_parse, common_report_header):
    def __init__(self, cr, uid, name, context):
        super(hr_movements_job_request, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'to_arabic': self.to_arabic,
        })
    
    def to_arabic(self, data):
        name = (data == 'single' and 'أعزب') or \
        (data == 'married' and 'متزوج') or \
        (data == 'widower' and 'أرمل') or \
        (data == 'divorced' and 'مطلق') or ""
        return name

                  
report_sxw.report_sxw('report.hr_movements_job_request', 'hr.movements.job', 'hr_custom_military/report/hr_movements_job_request.rml' ,parser=hr_movements_job_request ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

