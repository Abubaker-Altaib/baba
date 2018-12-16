import time
import re
import pooler
from report import report_sxw
import calendar
import datetime



class overtime_analysis(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(overtime_analysis, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line':self._get_over,
            'total':self._get_total,
            
               
        })
    globals()['holiday']=0.0
    globals()['work']=0.0
    globals()['value']=0.0
    globals()['totalz']={'hol_sum':0.0,'work_sum':0.0}
    def _get_over(self,data,month):
         
         res = {}
         mergedlist=[]
         data_list=[]
         emp_list=[]
         dic={}
         hol_sum=0.0
         work_sum=0.0
         value_sum=0.0
         allo_list=[]
         #month = 8
         month_to = (month == 12) and 1 or month + 1
         month = (month < 10) and '0'+str(month) or str(month)
         month_to = (month_to < 10) and '0'+str(month_to) or str(month_to)
         '''if(month < 10):
            month = '0'+str(month)
         if(month_to < 10):
            month_to = '0'+str(month_to) '''
         month_all = data['month'] and ('%'+'0'+str(data['month'])+'%') or 
                      ('{"%01%","%02%","%03%","%4%","%05%","%06%","%07%","%08%","%09%","%10%","%11%","%12%"}')
         if data['selection']=='1':
            print "-------------------------------data month", month,month_to
            qurey=("hr_employee.id =%s and  account_period.name like %s")
            ids=data['emp_id'][0]
            date1 = str(month)    
            date2 = str(month_to)
            month_all=('%'+date1+'%')
            search_ids = 
         else :
            ids=data['dep_id'][0] 
            if data['month']: 
               date1 = data['month']   
               date3='0'+str(date1)
               month_all=('%'+date3+'%')
               qurey=("hr_department.id=%s and  account_period.name like  %s ")
            else:
               qurey=("hr_department.id=%s and  account_period.name like any (%s)")
               month_list=('{"%01%","%02%","%03%","%4%","%05%","%06%","%07%","%08%","%09%","%10%","%11%","%12%"}')
               month_all=month_list
         print "-----------------------------------------qurey month_all ids", qurey, month_all,ids
         self.cr.execute('''SELECT account_period.name
          FROM account_period
          WHERE account_period.name like %s''',tuple([month_all])) 
         print "----------------------self.cr.dictfetchall()",self.cr.dictfetchall()
         self.cr.execute('''SELECT distinct
  hr_employee.name_related as emp, 
  hr_additional_allowance_line.holiday_hours as holiday_hours , 
  hr_additional_allowance_line.week_hours as week_hours , 
  hr_additional_allowance_line.amounts_value as value,
  hr_department.name as dep,
  account_period.name as month,
  hr_employee.id as ids
 
FROM 
  public.hr_additional_allowance_line, 
  public.hr_additional_allowance, 
  public.hr_employee,
  account_period,
  hr_allowance_deduction,
  hr_department
WHERE 
  hr_additional_allowance_line.employee_id = hr_employee.id AND
  hr_additional_allowance.id = hr_additional_allowance_line.additional_allowance_id  and
  account_period.id=hr_additional_allowance.period_id and 
  hr_additional_allowance.department_id=hr_department.id  and 
  hr_allowance_deduction.id=hr_additional_allowance.allowance_id and  '''
 +qurey+ '''and account_period.name like %s and
  hr_allowance_deduction.allowance_type='in_cycle' and hr_allowance_deduction.type='complex' ''',(ids,month_all,('%'+str(data['year'])) ))
         res = self.cr.dictfetchall()
         print "---------------------------alfadil", res
         if len(res)>0:
          for i in res:
            dic={'emp':i['emp'],
                 'holiday_hours':i['holiday_hours'],
                  'week_hours':i['week_hours'],
                  'value':i['value'],
                  'month':i['month'], 
                  'dep':i['dep'],}
            hol_sum+=i['holiday_hours']
            work_sum+=i['week_hours']
            value_sum+=i['value'] 
          self.cr.execute('''SELECT distinct dep.name as de_name,
sum(line.holiday_hours) as holiday , 
  sum(line.week_hours) as week , 
  sum(line.amounts_value) as value 
 from hr_department as dep,
 hr_employee as emp ,
 hr_additional_allowance_line as line,
 hr_additional_allowance as a,
 hr_allowance_deduction as allo
 where line.employee_id = emp.id AND a.id = line.additional_allowance_id  
 and dep.id=emp.department_id and emp.id=%s and  allo.allowance_type='in_cycle' and
 allo.id=a.allowance_id  and allo.type='complex' GROUP BY de_name'''%data['emp_id'][0])
          dep_data=self.cr.dictfetchall()
          data_list.append(dic)
          globals()['holiday']=dep_data[0]['holiday']
          globals()['work']=dep_data[0]['week']
          globals()['value']=dep_data[0]['value']                
          globals()['totalz']={'hol_sum':round(hol_sum or globals()['holiday'],2 ),'work_sum':round(work_sum or globals()['work'],2),'value_sum':round(value_sum or globals()['value'],2),'de_name':dep_data[0]['de_name'] }
         return data_list
  
    def _get_total(self):
      
        return globals()['totalz']


 
report_sxw.report_sxw('report.overtime.analysis', 'hr.employee', 'addons/hr_additional_allowance/report/overtime_analysis.rml' ,parser=overtime_analysis ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
