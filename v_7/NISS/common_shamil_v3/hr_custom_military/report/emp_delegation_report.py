import time
from report import report_sxw
from datetime import datetime
from dateutil.relativedelta import relativedelta

class emp_delegation_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.context = context
        super(emp_delegation_report, self).__init__(cr, uid, name, context)
        records = dict()
        records = self.get_record()
        self.localcontext.update(records)

#------------------------------- line----------------------------------   

    def get_record(self):
        data = self.pool.get('emp.delegation.report.wizard').browse(self.cr , self.uid , [self.context['active_id']])[0]
        res = {
            'department' : data.department_id and data.department_id.name or False ,
            'delegation' : data.state_id.name,
            'level2' : data.state_id_level2.name,
            'level3' : data.state_id_level3.name,
            'total':len(self._get_data(data)),
            'date' : time.strftime('%Y-%m-%d') ,
            'date_from' : data.date_from ,
            'date_to' : data.date_to,
            'employees' : self._get_data(data), 
        }
        return res

    def _get_data(self,data):
        res=[]
        departments=[]
        delegations=[]
        dept_obj=self.pool.get('hr.department')
        delegation_obj=self.pool.get('hr.employee.delegation')
        delegation_days=0
        delegation_months=0
        delegation_years=0

        if data.department_id:
            departments.append(data.department_id.id)
        else:
            departments = dept_obj.search(self.cr, self.uid, [])
        if data.date_from and data.date_to:
            if data.state_id_level2 and data.state_id_level2:
                delegations=delegation_obj.search(self.cr, self.uid, [('state','=','approve'),('start_date','>=',data.date_from),('start_date','<=',data.date_to),('new_state_id','=',data.state_id.id),('new_state_id_level2','=',data.state_id_level2.id),('new_state_id_level3','=',data.state_id_level3.id)])
            else:
                delegations=delegation_obj.search(self.cr, self.uid, [('state','=','approve'),('start_date','>=',data.date_from),('start_date','<=',data.date_to),('new_state_id','=',data.state_id.id)])
        else:
            if data.state_id_level2 and data.state_id_level2:
                delegations=delegation_obj.search(self.cr, self.uid, [('state','=','approve'),('new_state_id','=',data.state_id.id),('new_state_id_level2','=',data.state_id_level2.id),('new_state_id_level3','=',data.state_id_level3.id)])
            else:
                delegations=delegation_obj.search(self.cr, self.uid, [('state','=','approve'),('new_state_id','=',data.state_id.id)])
        for rec in delegation_obj.browse(self.cr,self.uid,delegations):
            if rec.employee_id.department_id.id in departments:
                df=datetime.strptime(rec.start_date,'%Y-%m-%d')
                now=str(datetime.now().date())
                dt=datetime.strptime(now,'%Y-%m-%d')
                date=relativedelta(dt,df)
                delegation_days=date.days
                delegation_months=date.months
                delegation_years=date.years
                res.append({'emp':rec,'delegation_days':delegation_days,'delegation_months':delegation_months,'delegation_years':delegation_years})
        return res

report_sxw.report_sxw('report.emp_delegation_reports', 'hr.employee', 'addons/hr_custom_military/report/emp_delegation_report.mako' ,parser=emp_delegation_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
