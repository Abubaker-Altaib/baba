import time
import re
import pooler
from report import report_sxw
import calendar
import datetime



class test_free2(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(test_free2, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'employee' :self._get_employee,


      
           }) 
    def _get_employee(self,data):
        res=[]
        date1 =data['From']
        date2 =data['to']
        job_id =data['job_id'][0]
        #emp_ids = self.pool.get('hr.employee.training.line').search(self.cr, self.uid, [('start_date','>=',date1),('start_date','<=',date2),('employee_id.job_id','=',job_id)])
        #emp = self.pool.get('hr.employee.training.line').browse(self.cr, self.uid, emp_ids) 
        self.cr.execute(''' 
            SELECT distinct
              r."name" as name, 
              tc.name as course,
              tl.start_date as start,
              tl.end_date as end,
              d.name as dep,
              job.name as job_name 
            
            FROM 
              public.hr_training_course tc ,
              public.hr_employee_training t ,
              public.hr_employee_training_line tl ,
              public.hr_employee e ,
              public.resource_resource r ,
              public.hr_department d ,
              public.hr_job job 
            
            WHERE 
              t.type ='hr.approved.course' and
              t.course_id=tc.id and
              t.id = tl.training_employee_id and
              tl.employee_id=e.id and
              r.id = e.resource_id and
              d.id=e.department_id and
              e.job_id = job.id and
              e.state!='refuse' and
              tl.start_date >=%s    and tl.start_date <=%s  and job.id=%s
            order by name
            
            ''',(date1,date2,job_id))
        res=self.cr.dictfetchall()

        return res 
       


report_sxw.report_sxw('report.test_free2', 'hr.employee.training.line', 'addons/hr_training/report/test_free2.rml' ,parser=test_free2 ,header="True")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
