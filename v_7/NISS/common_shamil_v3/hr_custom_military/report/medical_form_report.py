# -*- coding: utf-8 -*-

from report import report_sxw



class medical_form_report(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('hr.employee.illness').browse(self.cr , self.uid , [self.context['active_id']]) :
            res = {
                'name' : i.employee_id.name_related ,
                'job' : i.employee_id.job_id.name ,
                'department' : i.employee_id.department_id.name ,
                'code' : i.employee_id.otherid ,
                'degree' : i.employee_id.degree_id.name ,
                'type' : i.type ,
                'illness' : i.illness or "" , 
                'comment' : i.doctor_comment or "" , 
                'company_name' : self.pool.get('res.users').browse(self.cr , self.uid , [self.uid])[0].company_id.name or "",
                'user' : self.pool.get('res.users').browse(self.cr , self.uid , [self.uid])[0].name or "",
                'station' : i.station or "" , 
                'date' : i.date ,
            }
    	return res

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(medical_form_report, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)



report_sxw.report_sxw('report.medical_form_report','hr.employee.illness','addons/hr_custom_military/report/medical_form.mako',parser=medical_form_report,header=False)
