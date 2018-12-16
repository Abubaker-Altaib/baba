import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class service_duration(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(service_duration, self).__init__(cr, uid, name, context)
        self.localcontext.update({
           
                          
        })

   
 
report_sxw.report_sxw('report.service_duration', 'hr.employee', 'hr_custom/report/service_duration.rml' ,parser=service_duration ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
