# -*- coding: utf-8 -*-

from report import report_sxw



class commision_inability_form(report_sxw.rml_parse):
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
                'inability_percentage': str(i.inability_percentage * 100) +'%',
                'inability_acc_number':i.inability_acc_number,
                'inability_date':i.inability_date,
            }
    	return res

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(commision_inability_form, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)



report_sxw.report_sxw('report.commision_inability_form','hr.commision','addons/hr_custom_military/report/commision_inability_form.mako',parser=commision_inability_form,header='internal landscape')
