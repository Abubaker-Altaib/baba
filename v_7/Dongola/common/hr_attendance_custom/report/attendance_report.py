from report import report_sxw
import time
import pooler
import mx
import datetime
from osv import fields, osv
from tools.translate import _
import datetime as timedelta
class attendance_report(report_sxw.rml_parse):   
    def __init__(self, cr, uid, name, context):
        super(attendance_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time':time,
	    'line':  self._get_depts,
	    'line1':  self._getatten,
            'line2':self._get_total,

        })
    def _get_depts(self,data,dept_ids):
         department_obj=self.pool.get('hr.department')
         if not dept_ids :
            self.cr.execute('''select distinct e.department_id  from hr_employee e left join hr_attendance a on e.id=a.employee_id where to_char(a.name,'YYYY-mm-dd')>=%s and to_char(a.name,'YYYY-mm-dd')<=%s ''' ,(data['form']['dfrom'],data['form']['dto']))
            dept_ids=[rec['department_id'] for rec in self.cr.dictfetchall()]
         return department_obj.browse(self.cr,self.uid,dept_ids) 

    def _getatten(self,data,dept_id):
          employee_obj=self.pool.get('hr.employee')
          if dept_id:
             dept_list=[dept_id]
             if data['form']['lower_deps']:
                department_obj=self.pool.get('hr.department')
                dept_list+=department_obj.search(self.cr,self.uid,[('id','child_of',[dept_id])])
          else:
             dept_list=department_obj.search(self.cr,self.uid,[]) 
          emp_ids=employee_obj.search(self.cr,self.uid,[('department_id','in',dept_list)])
          att_list=[]
          if emp_ids:
             sign_out = '''(select to_char(max(name),'hh:MI:ss') from hr_attendance where day=a.day and action='sign_out' )'''
             sign_out_date = '''(select max(name) from hr_attendance where  day=a.day and action='sign_out' )'''  
             self.cr.execute('''select r.name as emp_name , e.emp_code as emp_code ,COALESCE(to_char(min(a.name),'hh:MI:ss'), '00:00:00' ) as sign_in,COALESCE('''+ sign_out + ''', '00:00:00' ) as sign_out, COALESCE((''' + sign_out_date + ''' - min(a.name) ), '00:00:00' ) as hours, a.day as date  from hr_attendance a left join hr_employee e on a.employee_id=e.id left join resource_resource r on e.resource_id=r.id where to_char(a.name,'YYYY-mm-dd')>=%s and to_char(a.name,'YYYY-mm-dd')<=%s and a.action='sign_in' and employee_id in %s group by r.name,e.emp_code,a.day order by a.day ''',(data['form']['dfrom'],data['form']['dto'],tuple(emp_ids)))          
             res= self.cr.dictfetchall() 
             count=0
             total=sum((r['hours'] for r in res) , datetime.timedelta())
             days, seconds = total.days, total.seconds
             hours = days * 24 + seconds // 3600
             minutes = (seconds % 3600) // 60
             seconds = seconds % 60
             total = str(hours)+':'+str(minutes)+':'+str(seconds)
             globals() ['hours_total'] = {'total':total} 
	     d_start= datetime.datetime.strptime('08:00:00','%H:%M:%S')
	     d_end = datetime.datetime.strptime('16:00:00' ,'%H:%M:%S')
	     overtime=datetime.datetime.strptime('00:00:00' ,'%H:%M:%S')		     
	     late= datetime.datetime.strptime('00:00:00' ,'%H:%M:%S')
             for r in res :
		in_time= datetime.datetime.strptime(r['sign_in'],'%H:%M:%S')
  	        out_time= datetime.datetime.strptime(r['sign_out'] ,'%H:%M:%S')
       		if in_time < d_start:

		    overtime +=  d_start - in_time
		else: 

			late  += (in_time - d_start)	
	        if d_end< out_time:
		   overtime +=out_time - d_end 
		else: 
			late += d_end - out_time
 
                count+=1
                dic={
		        'date':r['date'],
		        'sign_in':r['sign_in'],
		        'sign_out':r['sign_out'],
		        'hours':r['hours'],
		        'emp_name':r['emp_name'],
		        'emp_code':r['emp_code'],
		        'count':count,
	                'overtime':overtime.strftime('%H:%M:%S'),
			'late': late.strftime('%H:%M:%S'),

		        }
                att_list.append(dic)
          return att_list

    def _get_total(self):
          
          return globals() ['hours_total']
    
 
report_sxw.report_sxw('report.print.attendance',
                       'hr.employee',
                       'addons/hr_attendance_custom/report/attendance_report.rml',header=True,
                       parser=attendance_report)
