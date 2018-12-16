import time
import re
import pooler
from report import report_sxw
import calendar
import datetime



class holi_free(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(holi_free, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'lines1':self._getcom,
            'lines':self.get_emp,
            'line':self._getShop,
            'line5':self._holiday_count,
            
        })
    
    def get_emp(self,data):
         top_res=[]
         if data['department_id']:
          for b in  data['department_id']:
                self.cr.execute(''' SELECT dep.name as nn, dep.id as dep_id from hr_department dep where id=%s'''%b)
                do = self.cr.dictfetchall()
                data_dec={'name': do[0]['nn'],'department_id': do[0]['dep_id'],}
                top_res.append(data_dec)
         return top_res

    def _getcom(self,data):
        self.cr.execute('SELECT name AS company_name From res_company where id=%s'%(data['form']['comp_id'][0]))
        res = self.cr.dictfetchall()
        return res

    def _getShop(self,data,p):
                  periods=[]
                  hol_state = ('validate','validate1','confirm')
                  year = str(data['form']['year'])
                  self.cr.execute("SELECT g.name as degree,jo.name AS job_name,r.name AS emp,e.emp_code as code From hr_employee as e left join resource_resource as r on (e.resource_id=r.id) left join hr_job AS jo on (e.job_id=jo.id) left join hr_department d on (e.department_id=d.id) left join res_company as c on (d.company_id=c.id) left join hr_salary_degree as g on (e.degree_id=g.id) where d.id=%s and e.id not in (select employee_id from hr_holidays where ((department_id=%s) and (state in %s) AND (to_char(date_from,'YYYY')='%s' )))"%(p,p,hol_state,year))
                  res = self.cr.dictfetchall()
                  return res

    def _holiday_count(self,data,dept):

        hol_state = ('validate','approve')
        year = str(data['form']['year'])

        self.cr.execute("SELECT DISTINCT count(id) as count from hr_employee where department_id=%s and id not in (select employee_id from hr_holidays where ((department_id=%s) and (state in %s) AND (to_char(date_from,'YYYY')='%s' )))"%(dept,dept,hol_state,year)) 
        res = self.cr.dictfetchall()
        return res
                
                    
                
    
                
                    
                
        
report_sxw.report_sxw('report.holi.free', 'hr.employee', 'addons/hr_holidays_custom/report/holi_free.rml' ,parser=holi_free ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

