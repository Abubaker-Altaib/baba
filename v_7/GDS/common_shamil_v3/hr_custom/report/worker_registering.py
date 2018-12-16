##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import re
from report import report_sxw
import calendar

class worker_registering(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(worker_registering, self).__init__(cr, uid, name, context)
        self.localcontext.update({
             'line':self._get_wife,
                          
        })

    def _get_wife(self,emp1):
          emp=emp1.id
          self.cr.execute('''
                     select r.name as wife,f.start_date as date from hr_employee_family f
                     left join hr_family_relation r on (r.id=f.relation_id)
                     left join hr_employee e on (e.id=f.employee_id)
                     left join resource_resource c on (e.resource_id=c.id)
                     where f.state='approved' and r.max_age=0 and c.id=%s'''%(emp)) 
   
          res= self.cr.dictfetchall()
          return res
 
report_sxw.report_sxw('report.worker.registering', 'hr.employee', 'hr_custom/report/worker_registering.rml' ,parser=worker_registering ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
