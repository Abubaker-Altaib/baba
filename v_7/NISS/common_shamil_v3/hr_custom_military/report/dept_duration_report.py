import time
from report import report_sxw
from datetime import datetime
from dateutil.relativedelta import relativedelta


class dept_duration_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(dept_duration_report, self).__init__(cr, uid, name, context)
        records = dict()
        records = self.get_record()
        self.localcontext.update(records)

#------------------------------- line----------------------------------   

    def get_record(self):
        data = self.pool.get('dept.duration.report.wizard').browse(self.cr , self.uid , [self.context['active_id']])[0]
        print">>>>>>>>>>>>>>>>>>>>>>>>>>>data",data
        res = {
            'department' : data.department_id.name ,
            'degree' : data.degree_id.name ,
            'type':data.type,
            'total':len(self._get_data(data)),
            'date' : time.strftime('%Y-%m-%d') ,
            'more' : data.more_than ,
            'less' : data.more_than,
            'age_from' : data.age_from ,
            'age_to' : data.age_to,
            'employees' : self._get_data(data), 
        }
        return res

    def _get_data(self,data):
        res=[]
        emp_obj=self.pool.get('hr.employee')
        age_days=0
        age_months=0
        age_years=0
        if data.type == 'department_duration':
            emp_ids = emp_obj.search(self.cr, self.uid, [('department_id','=',data.department_id.id),('state','=','approved'),('actual_service_years','>=',data.more_than),('actual_service_years','<=',data.less_than)])
        else:
            emp_ids = emp_obj.search(self.cr, self.uid, [('degree_id','=',data.degree_id.id),('state','=','approved')])
        for emp in emp_obj.browse(self.cr,self.uid,emp_ids):
            if data.type == 'age':
                emp.actual_duration_computation()
                df=datetime.strptime(emp.birthday,'%Y-%m-%d')
                now=str(datetime.now().date())
                dt=datetime.strptime(now,'%Y-%m-%d')
                date=relativedelta(dt,df)
                age_days=date.days
                age_months=date.months
                age_years=date.years
                if age_years >= data.age_from and  age_years <= data.age_to:
                    res.append({'emp':emp,'age_days':age_days,'age_months':age_months,'age_years':age_years})

            else:
                res.append({'emp':emp,'age_days':age_days,'age_months':age_months,'age_years':age_years})
        return res

report_sxw.report_sxw('report.dept_duration_reports', 'hr.employee', 'addons/hr_custom_military/report/dept_duration_report.mako' ,parser=dept_duration_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
