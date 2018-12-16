import time
import re
import pooler
from report import report_sxw
import calendar
import datetime


class holi_info(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(holi_info, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line':self._get_holi,
            'line2':self.get_holdi_name,
                          
        })
        self.context = context
    def get_holdi_name(self,data):
         c=data['dep_id'][0]
         hol_list=[]
         holi_obj=self.pool.get('hr.holidays.status')
         for l in data['holi_type']:
             holi_name=holi_obj.browse(self.cr,self.uid,l,context=self.context).name
             dic={'hol_name':holi_name,'hol_id':l}
             hol_list.append(dic)
         return hol_list


    def _get_holi(self,data,hol_id):
         res = {}
         res_data = {}
         top_result = []
         date1 = data['year']
         #--------- function to retrieve alternative employee name ----------
         def get_alter_emp(self,emp):
                res_emp = {}
                
                self.cr.execute("SELECT DISTINCT resource_resource.name as emp_name from resource_resource,hr_employee where ((hr_employee.resource_id=resource_resource.id) and (hr_employee.id = %s ))"%emp)
                res_emp = self.cr.dictfetchall()
                return res_emp[0]['emp_name']
         #------------------------------------------------------------------- 
         self.cr.execute('''SELECT 
  resource_resource."name" AS emp_name, 
  hr_employee.emp_code AS emp_code, 
  hr_employee.id as employee_id,
  hr_holidays_status.id as holiday,
  hr_holidays.number_of_days, 
  hr_holidays.alternative_employee, 
  to_char(hr_holidays.date_from,'dd-mm-YYYY') AS date_from, 
  to_char(hr_holidays.date_to,'dd-mm-YYYY') AS date_to, 
  hr_holidays_status.number_of_days AS default_days
FROM 
  hr_holidays, 
  hr_employee, 
  resource_resource, 
  hr_holidays_status, 
  hr_department
WHERE 
  hr_holidays.employee_id = hr_employee.id AND
  hr_holidays.holiday_status_id = hr_holidays_status.id AND
  hr_holidays.department_id = hr_department.id AND
  hr_employee.resource_id = resource_resource.id AND
  hr_holidays_status.absence=FALSE AND
  hr_holidays.state not in ('draft','cancel','refuse')AND
  hr_holidays.department_id=%s  
  and hr_holidays_status.id=%s order by emp_name,date_from'''
,(data['dep_id'][0],hol_id))
         res = self.cr.dictfetchall()
         i = 0
         while i < len(res):
             holiday_details = self.pool.get('hr.holidays.status').get_days(self.cr, self.uid, [hol_id], res[i]['employee_id'], False, context=self.context)
             max_leaves = holiday_details.get(res[i]['holiday'], {}).get('max_leaves', 0)
             leaves_taken = holiday_details.get(res[i]['holiday'], {}).get('leaves_taken', 0)
             remaining = holiday_details.get(res[i]['holiday'], {}).get('remaining_leaves', 0)
             if(res[i]['number_of_days'] < 0):
                   day_num = res[i]['number_of_days']*-1
             else:
                   day_num = res[i]['number_of_days']
             if (leaves_taken < max_leaves):
                complete_day=0
                part_day = day_num
                re = remaining
             else:
                complete_day= max_leaves
                part_day = 0
                re = 0
             day_num = part_day
             if(res[i]['alternative_employee'] > 0):
                alter_emp = get_alter_emp(self,res[i]['alternative_employee'])
             else:
                alter_emp = False
             res_data = { 'no': str(i+1),
                         'emp_code': res[i]['emp_code'],
                         'emp_name': res[i]['emp_name'],
                         'date_to': res[i]['date_to'],
                         'date_from': res[i]['date_from'],
                         'complete_day': complete_day and complete_day or '0',
                         'part_day': day_num and day_num or '0',
                         'net_day': re or '0',
                         'alter_emp': alter_emp,
                    }
             top_result.append(res_data)
             i+=1
             
         return top_result
 


    
report_sxw.report_sxw('report.holi.info', 'hr.employee', 'addons/hr_holidays_custom/report/holi_info.rml' ,parser=holi_info ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
