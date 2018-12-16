import time
import re
import pooler
from report import report_sxw
import calendar
import datetime



class holi_analysis(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(holi_analysis, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line':self._get_holi,
            'line6':self._get_holi_total,
            'line3':self._get_all_emp,
            'line1':self.get_employee,
            'line2':self.get_dep,
                          
        })

    def get_dep(self,data):
         c=data['dep_id'][0]
         self.cr.execute('SELECT d.name AS dep from hr_department AS d where d.id=%s'%(c))
         res = self.cr.fetchall()
         return res


    def _get_holi(self,data,month,st):
         res = {}
         periods = []
         
         if(st==1):
            hol_state = 'draft'
         elif(st==2):
            hol_state = 'validate'
         elif(st==3):
            hol_state = 'validate1'
         elif(st==4):
            hol_state = 'confirm'
      
         month_to = month + 1
         
         if(month < 10):
            month = '0'+str(month)

         if(month_to < 10):
            month_to = '0'+str(month_to)

         date1 = str(month)    
         date2 = str(month_to) 
                  
         self.cr.execute("SELECT DISTINCT count(employee_id) as count from hr_holidays where ((holiday_status_id in %s) and (department_id=%s) and (state=%s) AND (to_char(date_from,'mm')=%s ))",(tuple(data['holi_type']),data['dep_id'][0],hol_state,date1))
         res = self.cr.dictfetchall()
         return res

    def _get_holi_total(self,data,st):
         res = {}
         if(st==1):
            hol_state = 'draft'
         elif(st==2):
            hol_state = 'validate'
         elif(st==3):
            hol_state = 'validate1'
         elif(st==4):
            hol_state = 'confirm'
         elif(st==5):
            hol_state = 'cancel'
         self.cr.execute("SELECT DISTINCT count(employee_id) as count from hr_holidays where ((department_id=%s) and (state=%s))",(data['dep_id'][0],hol_state))
         res = self.cr.dictfetchall()
         return res

    def _get_all_emp(self,data):
         res = {}
         date1 = str(data['year'])+'-01-01'
                           
         self.cr.execute("SELECT count(id) as count from hr_employee where ((department_id=%s) and (state='refuse') and (state != 'in_service') AND (to_char(employment_date,'YYYY-mm-dd')<=%s ))",(data['dep_id'][0],date1))
         res = self.cr.dictfetchall()
         return res    

    def get_employee(self,form):
        result = []
        periods = []
        emp = pooler.get_pool(self.cr.dbname).get('hr.employee')
        result = emp.browse(self.cr,self.uid, data['holi_type'])
        return result
 
report_sxw.report_sxw('report.holi.analysis', 'hr.employee', 'addons/hr_holidays_custom/report/holi_analysis.rml' ,parser=holi_analysis ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
