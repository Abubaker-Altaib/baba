import time
from report import report_sxw
import calendar
import datetime
import pooler

class transfer_noti(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(transfer_noti, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'emp': self.get_emp,
            'emp1': self.get_emp1,
            'dep': self.get_dep,
            'dep1': self.get_dep1,
            'line1':self._getcom,
            
        })


        

    def _getcom(self,form):
        result = []
        periods = []
        emp = pooler.get_pool(self.cr.dbname).get('res.company')
        for b in form['comp_id'][0][2]:
            periods.append(b)
        res = emp.browse(self.cr,self.uid, periods)  
        return res
    def get_emp(self,ids):
        p = pooler.get_pool(self.cr.dbname).get('hr.process.archive')
        emp_id=p.browse(self.cr, self.uid,[ids])[0]
        emp=emp_id.id

        
        self.cr.execute('''    
 SELECT 
  hr_salary_degree."name" as degree, 
  hr_job."name" as job,
  hr_employee."emp_code" as code, 
  resource_resource."name" as emp, 
  res_company."name" as comp, 
  hr2_basic_transfer_archive.transfer_date, 
  hr_department."name" as dep
FROM 
  public.hr_employee, 
  public.hr_salary_degree, 
  public.hr_job, 
  public.resource_resource, 
  public.hr2_basic_transfer_archive, 
  public.res_company, 
  public.hr_department
WHERE 
  hr_employee.job_id = hr_job.id AND
  hr_employee.resource_id = resource_resource.id AND
  hr_employee.department_id = hr_department.id AND
  hr_salary_degree.id = hr_employee.degree_id AND
  resource_resource.company_id = res_company.id AND
  hr2_basic_transfer_archive.employee_id = hr_employee.id AND
  res_company.id = hr2_basic_transfer_archive.company_id AND
  hr_department.id = hr2_basic_transfer_archive.department_id and 
  hr2_basic_transfer_archive.id=%s

'''%(emp,)) 
        res = self.cr.dictfetchall()
        return res


    def get_emp1(self,ids):
        p = pooler.get_pool(self.cr.dbname).get('hr.process.archive')
        emp_id=p.browse(self.cr, self.uid,[ids])[0]
        emp=emp_id.id

        
        self.cr.execute('''    
 SELECT 
  hr_salary_degree."name" as degree, 
  hr_job."name" as job,
  hr_employee."emp_code" as code, 
  resource_resource."name" as emp, 
  res_company."name" as comp, 
  hr2_basic_transfer_archive.transfer_date, 
  hr_department."name" as dep
FROM 
  public.hr_employee, 
  public.hr_salary_degree, 
  public.hr_job, 
  public.resource_resource, 
  public.hr2_basic_transfer_archive, 
  public.res_company, 
  public.hr_department
WHERE 
  hr_employee.job_id = hr_job.id AND
  hr_employee.resource_id = resource_resource.id AND
  hr_employee.department_id = hr_department.id AND
  hr_salary_degree.id = hr_employee.degree_id AND
  resource_resource.company_id = res_company.id AND
  hr2_basic_transfer_archive.employee_id = hr_employee.id AND
  res_company.id = hr2_basic_transfer_archive.company_id AND
  hr_department.id = hr2_basic_transfer_archive.department_id and 
  hr2_basic_transfer_archive.id=%s

'''%(emp,)) 
        res = self.cr.dictfetchall()
        return res
    def get_dep(self,ids):
        p = pooler.get_pool(self.cr.dbname).get('hr.process.archive')
        emp_id=p.browse(self.cr, self.uid,[ids])[0]
        emp=emp_id.id

        
        self.cr.execute('''    
 SELECT 
  hr_department."name" as dep, 
  resource_resource."name" as emp
FROM 
  public.hr2_basic_transfer_archive, 
  public.hr_department, 
  public.hr_employee, 
  public.resource_resource
WHERE 
  hr2_basic_transfer_archive.department_id = hr_department.id AND
  hr_employee.resource_id = resource_resource.id AND
  hr_employee.id = hr2_basic_transfer_archive.employee_id and 
  hr2_basic_transfer_archive.id=%s

'''%(emp,)) 
        res = self.cr.dictfetchall()
        return res

    def get_dep1(self,ids):
        p = pooler.get_pool(self.cr.dbname).get('hr.process.archive')
        emp_id=p.browse(self.cr, self.uid,[ids])[0]
        emp=emp_id.id

        
        self.cr.execute('''    
 SELECT 
  hr_department."name" as dep, 
  resource_resource."name" as emp
FROM 
  public.hr2_basic_transfer_archive, 
  public.hr_department, 
  public.hr_employee, 
  public.resource_resource
WHERE 
  hr2_basic_transfer_archive.old_department = hr_department.id AND
  hr_employee.resource_id = resource_resource.id AND
  hr_employee.id = hr2_basic_transfer_archive.employee_id and 
  hr2_basic_transfer_archive.id=%s

'''%(emp,)) 
        res = self.cr.dictfetchall()
        return res


    

report_sxw.report_sxw('report.transfer.noti', 'hr.process.archive', 'addons/hr_process/report/transfer_noti.rml' ,parser=transfer_noti, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
