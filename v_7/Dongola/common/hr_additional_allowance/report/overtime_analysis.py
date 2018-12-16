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
    globals()['totalz']={'hol_sum':0.0,'work_sum':0.0,'de_name':'/','value_sum':0.0}
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
         month_to = (month == 12) and 1 or month + 1
         month = (month < 10) and '0'+str(month) or str(month)
         month_to = (month_to < 10) and '0'+str(month_to) or str(month_to)
         if data['selection']=='1':
            qurey=("hr_employee.id =%s and  account_period.code like %s")
            ids=data['emp_id'][0]
            month_all=(str(month)+'/'+str(data['year']))
         else :
            ids=data['dep_id'][0] 
            if data['month']: 
               date1 = int(data['month'])<10 and '0'+str(data['month'])+'/'+str(data['year']) or str(data['month'])+'/'+str(data['year'])   
               #date3='0'+str(date1)
               month_all=(date1)
               qurey=("hr_department.id=%s and  account_period.code like  %s ")
            else:
               qurey=("hr_department.id=%s and  account_period.code like any (%s)")
               month_list=(['01'+'/'+str(data['year']),'02'+'/'+str(data['year']),'03'+'/'+str(data['year']),'04'+'/'+str(data['year']),
                    '05'+'/'+str(data['year']),'06'+'/'+str(data['year']),'07'+'/'+str(data['year']),'08'+'/'+str(data['year']),
                    '09'+'/'+str(data['year']),'10'+'/'+str(data['year']),'11'+'/'+str(data['year']),'12'+'/'+str(data['year'])] ) 
               month_all= month_list
         self.cr.execute('''SELECT distinct
  hr_employee.name_related as emp, 
  hr_additional_allowance_line.holiday_hours as holiday_hours , 
  hr_additional_allowance_line.week_hours as week_hours , 
  hr_additional_allowance_line.amounts_value as value,
  hr_department.name as dep,
  account_period.code as month,
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
 +qurey+ '''and
  hr_allowance_deduction.allowance_type='in_cycle' and hr_allowance_deduction.type='complex' ''',(ids,month_all))
         res = self.cr.dictfetchall()
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
            data_list.append(dic) 
         

          globals()['totalz']['hol_sum'] = round(hol_sum,2 )
          globals()['totalz']['work_sum'] = round(work_sum,2 )
          globals()['totalz']['value_sum'] = round(value_sum,2 )

         if not len(res)>0 and data['selection']=='1':
          emp_recrd = self.pool.get('hr.employee').browse(self.cr,self.uid,ids)
          dic={'emp':emp_recrd.name_related,
                 'holiday_hours':0.0,
                  'week_hours':0.0,
                  'value':0.0,
                  'month':month, 
                  'dep':emp_recrd.department_id.name,}
          data_list.append(dic)
          if month_all == "01"+'/'+str(data['year']):
            globals()['totalz']['hol_sum'] = round(hol_sum,2 )
            globals()['totalz']['work_sum'] = round(work_sum,2 )
            globals()['totalz']['value_sum'] = round(value_sum,2 )
          else:
            globals()['totalz']['hol_sum'] += round(hol_sum,2 )
            globals()['totalz']['work_sum'] += round(work_sum,2 )
            globals()['totalz']['value_sum'] += round(value_sum,2 )

         if not len(res)>0 and data['selection']=='2' and data['month']:
          dic={'emp':'/',
                 'holiday_hours':0.0,
                  'week_hours':0.0,
                  'value':0.0,
                  'month':month_all, 
                  'dep':data['dep_id'][1]}
          data_list.append(dic)
          globals()['totalz']['hol_sum'] = round(hol_sum,2 )
          globals()['totalz']['work_sum'] = round(work_sum,2 )
          globals()['totalz']['value_sum'] = round(value_sum,2 )

         if not len(res)>0 and data['selection']=='2' and not data['month']:
          for i in month_all: 
            dic={'emp':'/',
                 'holiday_hours':0.0,
                  'week_hours':0.0,
                  'value':0.0,
                  'month':i, 
                  'dep':data['dep_id'][1]}
            data_list.append(dic)
          globals()['totalz']['hol_sum'] = round(hol_sum,2 )
          globals()['totalz']['work_sum'] = round(work_sum,2 )
          globals()['totalz']['value_sum'] = round(value_sum,2 )
         return data_list
  
    def _get_total(self,data):

        if data['selection']=='1':
            ids=data['emp_id'][0]
            emp_recrd = self.pool.get('hr.employee').browse(self.cr,self.uid,ids)
            globals()['totalz']['de_name'] = emp_recrd.department_id.name
      
        return globals()['totalz']


 
report_sxw.report_sxw('report.overtime.analysis', 'hr.employee', 'addons/hr_additional_allowance/report/overtime_analysis.rml' ,parser=overtime_analysis ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
