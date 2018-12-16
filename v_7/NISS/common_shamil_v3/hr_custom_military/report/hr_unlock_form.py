# -*- coding: utf-8 -*-

from report import report_sxw
import time
import datetime

class hr_unlock_form(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
        line="................................................................................................................................................................."
        line2="............................................................................................................................................................."

        res = {}
    	for i in self.pool.get('hr.unlock').browse(self.cr , self.uid , [self.context['active_id']]) :
            res['name'] = i.employee_id.name_related 
            res['degree'] = i.emp_degree.name 
            res['code'] = i.otherid
            res['department'] = i.emp_dept.name
            res['reason'] = i.reason.name
            res['dest'] = i.destination or line
            res['dept_comment'] = i.dept_comment or line2
            res['date'] = datetime.date.today().strftime('%Y-%m-%d')
            res['from_company2department']=self.from_company_to_department(self.uid)
    	return res

    def from_company_to_department(self,uid):
        emp_obj=self.pool.get('hr.employee')
        dept_obj=self.pool.get('hr.department')
        emp=emp_obj.search(self.cr, self.uid, [('user_id','=',uid)])
        res = ""
        if emp:
            employee = emp_obj.browse(self.cr, self.uid, emp[0])
            reads=dept_obj.name_get(self.cr, self.uid, [employee.department_id.id])
            res+= employee.company_id.name + '<br/>' 
            departments=reads[0][1].split(' / ')
            for dept in departments:            
                dept_res=dept_obj.search(self.cr, self.uid, [('name','ilike',dept.encode('utf-8')),('cat_type','in',['department','corp','aria'])])
                if dept_res:
                    res+=dept.encode('utf-8')+'<br/>'
                else:
                    break
        return res

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(hr_unlock_form, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.hr_unlock_form','hr.unlock','addons/hr_custom_military/report/hr_unlock_form.mako',parser=hr_unlock_form,header=False)
