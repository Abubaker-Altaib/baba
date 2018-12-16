from report import report_sxw
import time
import datetime
import pooler
import mx
from osv import fields, osv
import datetime as timedelta
from tools.translate import _
class employee_attendance(report_sxw.rml_parse):   
    def __init__(self, cr, uid, name, context):
        super(employee_attendance, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time':time,
            'line':self._get_atten,
            'line1':self._get_total,

        })
    def _get_atten(self,data,emp_id):
          att_list=[]
          sign_out = '''(select to_char(max(name),'hh:MI:ss') from hr_attendance where employee_id=%s and day=a.day and action='sign_out' )'''
          sign_out_date = '''(select max(name) from hr_attendance where employee_id=%s and day=a.day and action='sign_out' )'''  
          self.cr.execute('''select  to_char(min(name),'Dy') as day , COALESCE(to_char(min(a.name),'hh:MI:ss'), '00:00:00' ) as sign_in, COALESCE('''+ sign_out + ''', '00:00:00' ) as sign_out, COALESCE((''' + sign_out_date + ''' - min(a.name)), '00:00:00' ) as hours, a.day as date  from hr_attendance a where a.employee_id=%s and to_char(a.name,'YYYY-mm-dd')>=%s and to_char(a.name,'YYYY-mm-dd')<=%s and a.action='sign_in' group by a.day order by a.day ''',(emp_id,emp_id,emp_id,data['form']['dfrom'],data['form']['dto']))          
          res= self.cr.dictfetchall() 
          count=0
          total=sum((r['hours'] for r in res) , datetime.timedelta())
          days, seconds = total.days, total.seconds
          hours = days * 24 + seconds // 3600
          minutes = (seconds % 3600) // 60
          seconds = seconds % 60
          total= str(hours)+':'+str(minutes)+':'+str(seconds)
          globals() ['hours_total'] = {'total':total}
          for r in res :
            count+=1
            dic={
                'date':r['date'],
                'sign_in':r['sign_in'],
                'sign_out':r['sign_out'],
                'hours':r['hours'],
                'day':r['day'],
                'no':count,
                }
            att_list.append(dic)
          return att_list

    def _get_total(self):
          return globals() ['hours_total'] 
    
 
report_sxw.report_sxw('report.employee.attendance',
                       'hr.employee',
                       'addons/hr_attendance_custom/report/attendance_of_employee.rml',header=True,
                       parser=employee_attendance)
