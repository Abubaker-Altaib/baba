import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class certificate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(certificate, self).__init__(cr, uid, name, context)
        self.localcontext.update({
           
                          
        })

   
 
report_sxw.report_sxw('report.certificate', 'hr.employee', 'hr_custom/report/certificate.rml' ,parser=certificate ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
