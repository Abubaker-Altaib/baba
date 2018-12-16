import time
from report import report_sxw
import calendar
import datetime
import pooler
import time
import mx
import datetime

from time import strptime

import datetime as timedelta
from datetime import datetime
import math

class promo_rec(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(promo_rec, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            #'way':self._get_way,
            'time': time,
            #'over1':self._get_birthday1,
            'line':self._get_line,
            'emp':self._get_emp,
            

        })
          
############################################################################################### All dep1
    def _get_line(self,data):
         date1 =data['from']
         #print ">>>>>>>>>>>>>>>>date1" ,date1
         top_res1=[]
         top_res2=[]
         #max_date = (mx.DateTime.Parser.DateTimeFromString(date1)).year
         #form_date =str(date1)+'-'+'01'+'-'+'01'
         self.cr.execute(''' 
SELECT distinct
  r."name" as name, 
  e.emp_code as code,
  max(tl.start_date) as start,
  d.name as dep
FROM 
  public.hr_employee_training t INNER JOIN
  public.hr_employee_training_line tl ON t.id=tl.training_employee_id INNER JOIN
  public.hr_employee e ON tl.employee_id=e.id INNER JOIN
  public.resource_resource r ON r.id = e.resource_id INNER JOIN 
  public.hr_department d ON d.id=e.department_id
WHERE 
	e.state!='refuse' AND t.type ='hr.approved.course' AND tl.start_date <'%s'
GROUP BY r."name" ,e.emp_code,dep

   '''%data['from'])
         res=self.cr.dictfetchall()
         for b in res:
                       
                   dic={
                        'name':b['name'],
                        'code':b['code'],
                        'start':b['start'],
                        'dep':b['dep'],
              
                        }

                   
                   top_res1.append(dic) 
         #print ">>>>>>>top_res1" ,len(top_res1)  '''
         return top_res1

###############################################################################################################
    def _get_emp(self,data):
         date1 =data['from']
         #print ">>>>>>>>>>>>>>>>date1" ,date1
         top_res1=[]
         top_res2=[]
         #max_date = (mx.DateTime.Parser.DateTimeFromString(date1)).year
         #form_date =str(date1)+'-'+'01'+'-'+'01'
         self.cr.execute(''' 
SELECT distinct
  r."name" as name, 
  e.emp_code as code,
  d.name as dep,
  e.id
FROM 
  public.hr_employee e ,
  public.resource_resource r ,
  public.hr_department d 
  
WHERE 
  e.state!='refuse' and
  r.id =e.resource_id and
  d.id=e.department_id and 
  e.id not in (SELECT distinct
   e.id as emp_id
  
FROM 
  public.hr_employee_training t INNER JOIN
  public.hr_employee_training_line tl ON t.id=tl.training_employee_id INNER JOIN
  public.hr_employee e ON tl.employee_id=e.id INNER JOIN
  public.resource_resource r ON r.id = e.resource_id INNER JOIN 
  public.hr_department d ON d.id=e.department_id
WHERE 
	e.state!='refuse' AND tl.start_date <'%s' AND t.type ='hr.approved.course'
)
GROUP BY r."name" ,e.emp_code,dep  ,e.id

   '''%data['from'])
         res=self.cr.dictfetchall()
         for b in res:
                       
                   dic={
                        'name':b['name'],
                        'code':b['code'],
                        'dep':b['dep'],
              
                        }

                   
                   top_res1.append(dic) 
         #print ">>>>>>>top_res1" ,len(top_res1)  '''
         return top_res1
   
report_sxw.report_sxw('report.no_training', 'hr.employee.training.line', 'addons/hr_training/report/no_training.rml', parser=promo_rec,header="True")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
