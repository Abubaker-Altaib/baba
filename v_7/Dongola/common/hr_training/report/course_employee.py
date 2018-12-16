# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import  netsvc
from report import report_sxw
from openerp.tools.translate import _
from openerp.osv import fields,osv,orm

class course_employee(report_sxw.rml_parse ):
      def __init__(self, cr, uid, name, context):
        super(course_employee, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'info':self._get_course,
 
   })

      def _get_course(self,course):
         self.cr.execute('''
SELECT distinct
  emp.emp_code AS code,
  resource.name AS emps,
 training.end_date AS end, 
 training.start_date as start
 
FROM 
  hr_employee_training training
left join hr_employee_training_line line on (line.training_employee_id=training.id)
left join  hr_employee emp on (emp.id=line.employee_id)
left join  resource_resource resource on (resource.id=emp.resource_id)
left join  hr_training_course course on (course.id=training.course_id)
where training.type ='hr.approved.course' and course.id=%s  and training.state = 'done' '''%(course) )
         res = self.cr.dictfetchall()
         if not res :
            raise osv.except_osv(_('warning!'), _('You can not print ..there is no data on this report !'))
         return res


report_sxw.report_sxw('report.course.employee', 'hr.training.course', 'addons/hr_traning/report/course_employee.rml' ,parser=course_employee ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
