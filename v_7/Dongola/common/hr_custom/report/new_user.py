# -*- coding: utf-8 -*-
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

class new_user(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(new_user, self).__init__(cr, uid, name, context)
        self.localcontext.update({
               'line':self._get_qualification,
                          
        })

    def _get_qualification(self,emp1):
          emp=emp1.id
          self.cr.execute('''
                  select qa.name AS qua ,s.name AS spc,q.qual_date AS date,q.organization AS org from hr_employee_qualification q 
                  left join hr_employee e on (e.id=q.employee_id)
                  left join hr_specifications s on (s.id=q.specialization)
                  left join hr_qualification qa on (qa.id=q.emp_qual_id)
                  left join resource_resource c on (c.id=e.resource_id) where q.state='approved' and c.id=%s'''%(emp))
          res= self.cr.dictfetchall()
          return res
 
report_sxw.report_sxw('report.new_user', 'hr.employee', 'addons/hr_custom/report/new_user.rml' ,parser=new_user ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
