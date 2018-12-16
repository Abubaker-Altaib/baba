from report import report_sxw
import time
import math
from osv import osv, fields
from tools.translate import _


class department_course(report_sxw.rml_parse): 
      def __init__(self, cr, uid, name, context):
        super(department_course, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'timee' : self._get_depts,
            'comp' : self._get_comp,

      
           })       
      def get_remove(self,data):
         x=data['selection']
         
         return x


 ############################################################################Deptt

      def _get_depts(self,data):
         d_id=[]
         d_list=[]
         top_res=[]
         d_list=[]
         k_id=data['company_id'][0]
         #pl_id=data['plan_id'][0]
         for b in  data['department_id']:
             self.cr.execute('''
SELECT distinct 
m.name as dep , m.id as m_id 
FROM 
  hr_employee_training,
  public.hr_employee, 
  hr_training_plan,
  public.hr_employee_training_line, 
  public.hr_training_course,
  res_company,
  hr_department as m left join hr_department as pd
on (m.parent_id= pd.id)
WHERE 
  hr_employee.id = hr_employee_training_line.employee_id AND
  hr_employee_training.plan_id= hr_training_plan.id and
  hr_employee.department_id = m.id AND
  res_company.id = m.company_id and
  hr_employee_training.type ='hr.approved.course' and
res_company.id=%s and m.id = %s
 ''',(k_id,b ))

        
             res1 = self.cr.dictfetchall()
 
        
             for b in res1: 
               
                 dic={
                   'dep':b['dep'],
                 
                   'm_id':b['m_id'],
                     }
                 top_res.append(dic)
         return top_res
#################################################################################################Company
      def _get_comp(self,i):
         ids_list=[]
         name_list=[]
         self.cr.execute('''
  
         
SELECT distinct
  cou."name" as course, 
   jop."name" as job , 
  emp.emp_code as code, 
  t.end_date as end, 
  t.start_date as start, 
  res."name" as emps 
  

FROM 
 hr_employee_training t
left join hr_employee_training_line line on (line.training_employee_id=t.id)
left join  hr_employee emp on (emp.id=line.employee_id)
left join hr_job jop on (jop.id=emp.job_id)
left join resource_resource res on (res.id=emp.resource_id)
left join hr_training_course cou on(cou.id=t.course_id)
left join hr_department dep on (dep.id=emp.department_id)
WHERE 
  t.type ='hr.approved.course' and
  dep.id=%s'''%i[0][0] )
         res = self.cr.dictfetchall()
 
                 
           
         return res



report_sxw.report_sxw('report.department.course', 'hr.employee.training','addons/hr_training/report/department_course.rml' ,parser=department_course ,header="True")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
