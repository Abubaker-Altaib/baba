import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class vac_req(report_sxw.rml_parse):
       def __init__(self, cr, uid, name, context):
                super(vac_req, self).__init__(cr, uid, name, context)
                self.localcontext.update({
                        'time': time,
                        '_get_emp':self._get_emp,
                        '_get_man':self._get_man,
                        '_get_man1':self._get_man1,
                        '_get_man2':self._get_man2,

               })
      
    
       
       def _get_emp(self,ids):
           #print "ids",ids
           p = pooler.get_pool(self.cr.dbname).get('hr.holidays')
           holi =p.browse(self.cr, self.uid,[ids])[0]
           emp=holi.employee_id.id 
           vac=holi.holiday_status_id.id 
           date=holi.date_from
           print "emp",emp ,vac ,date
           self.cr.execute('SELECT r.name as emp,e.emp_code as code,d.name as dep,s.name as holiday,s.code as vac_code,h.date_from as from,h.date_to as to,h.create_date as cre,h.number_of_days_temp as no_day,h.state as state,h.notes as notes FROM hr_holidays AS h left join hr_employee AS e on (h.employee_id=e.id) left join  resource_resource AS r on (e.resource_id=r.id) left join hr_department d on (e.department_id=d.id) left join hr_holidays_status as s  on (h.holiday_status_id=s.id)  where e.id=%s and s.id=%s and h.date_from=%s',(emp,vac,date)) 
           res = self.cr.dictfetchall()
           print "transfer",res
           return res

       def _get_man(self,ids):
           #print "ids",ids
           p = pooler.get_pool(self.cr.dbname).get('hr.holidays')
           #s=p.search(self.cr, self.uid,[('employee_id','=',ids)])
           emp_id=p.browse(self.cr, self.uid,[ids])[0]
           #print "jjjj",emp_id.employee_id.id
           emp=emp_id.employee_id.id
           vac=emp_id.holiday_status_id.id
           date=emp_id.date_from
           #print "emp",emp
           
           self.cr.execute('SELECT  r.name as name FROM hr_holidays AS h left join hr_employee AS e on (h.manager_id=e.id) left join  resource_resource AS r on (e.resource_id=r.id) left join hr_department d on (e.department_id=d.id) left join hr_holidays_status as s  on (h.holiday_status_id=s.id)  where s.id=%s and h.date_from=%s',(vac,date)) 
           res = self.cr.dictfetchall()
           #print "transfer",res
           return res
       def _get_man2(self,ids):
           #print "ids",ids
           p = pooler.get_pool(self.cr.dbname).get('hr.holidays')
           #s=p.search(self.cr, self.uid,[('employee_id','=',ids)])
           emp_id=p.browse(self.cr, self.uid,[ids])[0]
           #print "jjjj",emp_id.employee_id.id
           emp=emp_id.employee_id.id
           vac=emp_id.holiday_status_id.id
           date=emp_id.date_from
           #print "emp",emp
           
           self.cr.execute('SELECT  r.name as name FROM hr_holidays AS h left join hr_employee AS e on (h.alternative_employee=e.id) left join  resource_resource AS r on (e.resource_id=r.id) left join hr_department d on (e.department_id=d.id) left join hr_holidays_status as s  on (h.holiday_status_id=s.id)  where s.id=%s and h.date_from=%s',(vac,date)) 
           res = self.cr.dictfetchall()
           #print "transfer",res
           return res

       def _get_man1(self,ids):
           #print "ids",ids
           p = pooler.get_pool(self.cr.dbname).get('hr.holidays')
           #s=p.search(self.cr, self.uid,[('employee_id','=',ids)])
           emp_id=p.browse(self.cr, self.uid,[ids])[0]
           #print "jjjj",emp_id.employee_id.id

           emp=emp_id.manager_id.id
           vac=emp_id.holiday_status_id.id
           date=emp_id.date_from
           #print "emp",emp
           
           self.cr.execute('SELECT  r.name as name FROM hr_holidays AS h left join hr_employee AS e on (h.manager_id2=e.id) left join  resource_resource AS r on (e.resource_id=r.id) left join hr_department d on (e.department_id=d.id) left join hr_holidays_status as s  on (h.holiday_status_id=s.id)  where  s.id=%s and h.date_from=%s',(vac,date)) 
           res = self.cr.dictfetchall()
           #print "transfer",res
           return res
                
                    
                
        
report_sxw.report_sxw('report.vac_req', 'hr.holidays', 'addons/hr_holidays_custom/report/vac_req.rml' ,parser=vac_req)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

