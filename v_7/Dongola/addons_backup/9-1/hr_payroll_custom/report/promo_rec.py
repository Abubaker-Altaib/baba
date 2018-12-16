import time
from report import report_sxw
import re
import pooler
import calendar
from osv import fields, osv
import mx
from datetime import datetime

class promo_rec(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(promo_rec, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'lines':self.get_emp,
            'line':self._getShop,
        })
   
    def get_emp(self,form):
        result = []
        periods = []        
        emp = pooler.get_pool(self.cr.dbname).get('hr.job')
        result = emp.browse(self.cr,self.uid, form['job_id'])
        return result

    def _getShop(self,data,i):
                      date1 = data['form']['from']
                      degree =data['form']['degree'][0]
                      re_res1=[]
                      check1=0
                      check=0
                      periods=[]
                      ids_list=[]
                      ids_list1=[]
                      name_list=[]
                      name_list1=[]
                      name_list2=[]
                      name_list3=[]
                      name_list4=[]
                      name_list5=[]
                      name_list6=[]
                      dif=0
                      #for b in data['form']['job_id'][0][2]:
                              #periods.append(b)                     
                      self.cr.execute('''
                    SELECT distinct
  resource_resource.name emp_name, 
  hr_department.name as dep_name, 
  hr_employee.employment_date as emp_date, 
  hr_employee.emp_code as code, 
  hr_process_archive.promotion_date as last_promo, 
  hr_employee.birthday as birthday, 
  hr_employee.id as e_id
 
FROM
  public.hr_department, 
  public.hr_employee, 
  public.resource_resource,
  hr_job,
  hr_process_archive
WHERE 
  hr_employee.resource_id = resource_resource.id AND
  hr_employee.department_id = hr_department.id and
  hr_employee.job_id = hr_job.id 
 and hr_employee.job_id=%s and hr_employee.degree_id=%s
order by 
hr_process_archive.promotion_date asc ,hr_employee.employment_date asc ,hr_employee.birthday asc
 ''',(i,degree))
                      res1 = self.cr.dictfetchall()
                      if len(res1) > 0:
                         for d in res1:
                          if d['last_promo']:
                            dif=0
                            P_date = mx.DateTime.Parser.DateTimeFromString(d['last_promo'])
                            X_date = mx.DateTime.Parser.DateTimeFromString(date1 )

                            P_month=int(X_date.month)-int(P_date.month)
                            diff =( int(X_date.year)-int(P_date.year) ) + (float(P_month)/float(365))
                            if (diff >= data['form']['year']):
                                ids_list.append(d['e_id'])
                                name_list.append(d['emp_name'])
                                name_list1.append(d['code'])
                                name_list2.append(d['emp_date'])
                                name_list3.append(d['last_promo'])
                                name_list4.append(d['birthday'])
                                name_list5.append(d['dep_name'])
                            
                            
                      p=0
                      while len(ids_list) > p :
                            self.cr.execute('''
         
SELECT distinct
   Max(qual_date),
   hr_qualification."name" as qual_name,
   hr_specifications."name" as specialization
   FROM 
   public.hr.employee.qualification, 
  public.hr_qualification, 
  public.hr_specifications, 
  public.hr_employee
   WHERE
    hr.employee.qualification.specialization = hr2_specifications.id AND
  hr.employee.qualification.employee_id = hr_employee.id AND
  hr.employee.qualification.emp_qual_id = hr_qualification.id AND
   hr.employee.qualification.emp_qual_id = hr_qualification.id 
   and qual_date =(select max(qual_date) 
   from  hr.employee.qualification where  hr.employee.qualification.employee_id=%s
)
  GROUP BY  hr_qualification."name",hr2_specifications."name"
   '''%ids_list[p])
                            res1 = self.cr.dictfetchall()                            
                            i=0
                            if len(res1) > i :                  
                                 check=res1[i]['qual_name']
                                 check1=res1[i]['specialization']
                            dic={  
                                    'no':p+1,
                                   'specialization':check1,
                                    'emp_name':name_list[p],
                                   'qual_name':check,
                                   'code':name_list1[p],
                                   'emp_date':name_list2[p],
                                   'last_promo':name_list3[p],
                                   'birthday':name_list4[p],
                                   'dep_name':name_list5[p],
                            }
                            re_res1.append(dic)
                            p=p+1
                      return re_res1
    
    
report_sxw.report_sxw('report.promo.rec', 'hr.employee', 'addons/hr_process/report/promo_rec.rml' ,parser=promo_rec,header="custom landscape")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
