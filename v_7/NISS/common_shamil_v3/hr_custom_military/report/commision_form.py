# -*- coding: utf-8 -*-

from report import report_sxw
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta



class commision_form(report_sxw.rml_parse):
    '''
    @return commision data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('hr.commision').browse(self.cr , self.uid , [self.context['active_id']]) :
            res = {
                'name' : i.name ,
                'employee' : i.employee_id.name ,
                'department' : i.employee_id.department_id.name ,
                'otherid' : i.employee_id.otherid ,
                'degree' : i.employee_id.degree_id.name ,
                'hospital' : i.hospital or "",
                'birthday' : i.employee_id.birthday, 
                'employment_date' : i.employee_id.employment_date, 
                'report_date' : i.report_date, 
                'company_name' : self.pool.get('res.users').browse(self.cr , self.uid , [self.uid])[0].company_id.name or "",
                'user' : self.pool.get('res.users').browse(self.cr , self.uid , [self.uid])[0].name or "",
                'date' : i.date ,
                'birthday_duration':self.get_birthday_duration(i.employee_id),
                'work_duration':self.get_work_duration(i.employee_id),
            }
    	return res

    def get_birthday_duration(self,emp):
        res={}
        birthday=emp.birthday

        df=datetime.strptime(birthday,'%Y-%m-%d')
        now=str(datetime.now().date())
        dt=datetime.strptime(now,'%Y-%m-%d')
        date=relativedelta(dt,df)

        res['days']=date.days
        res['months']=date.months
        res['years']=date.years
        return res

    def get_work_duration(self,emp):
        res={}
        emp.actual_duration_computation()

        res['total_days']=emp.total_service_days
        res['total_months']=emp.total_service_months
        res['total_years']=emp.total_service_years
        return res

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(commision_form, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)



report_sxw.report_sxw('report.commision_form','hr.commision','addons/hr_custom_military/report/commision_form.mako',parser=commision_form,header=True)
