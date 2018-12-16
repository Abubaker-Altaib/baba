# -*- coding: utf-8 -*-

from report import report_sxw
from openerp.tools.translate import _
from openerp.osv import fields,osv,orm
import time

title = {
    'officer' : unicode('رقم.البطاقة', 'utf-8'),
    'soldier' :unicode('نمرة', 'utf-8')  ,
}

family = {
    'wife' : unicode('لزوجته', 'utf-8') , 
    'son' : unicode('لابنه', 'utf-8') ,
    'daughter' : unicode('لابنته', 'utf-8') ,
    'father' : unicode('لوالده', 'utf-8') ,
    'mother' : unicode('لوالدته', 'utf-8') ,
  }

class medical_form_report(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
    	res = {}
    	#raise osv.except_osv(_('warning!'), _('You can not print %s')%self.context['active_model'])
        if self.context['active_model'] == 'hr.employee.illness': 
	    	for i in self.pool.get('hr.employee.illness').browse(self.cr , self.uid , [self.context['active_id']]) :
		    res = {
		        'name' : i.employee_id.name_related ,
		        'department' : i.employee_id.department_id.name ,
		        'code' : i.employee_id.emp_code ,
		        'degree' : i.employee_id.degree_id.name ,
		        'type' : title[i.employee_id.payroll_id.military_type] ,
                        'struct':i.employee_id.payroll_id.military_type,
		        'illness' : i.illness or "" , 
		        'comment' : i.doctor_comment or "" , 
		        'company_name' : self.pool.get('res.users').browse(self.cr , self.uid , [self.uid])[0].company_id.name or "",
		        'station' : i.station or "" , 
		        'date' : i.date ,
		        'family' : i.family and family[i.family] or "" ,
		    }
        elif self.context['active_model']=='hr.employee':
             for i in self.pool.get('hr.employee').browse(self.cr , self.uid , [self.context['active_id']]) :
                    res_id = self.pool.get('resource.resource').search(self.cr,self.uid, [('user_id','=',self.uid)])
                    emp_id = self.pool.get('hr.employee').search(self.cr,self.uid, [('resource_id','=',res_id)])
                    emp_data = self.pool.get('hr.employee').browse(self.cr , self.uid , emp_id)
                    #raise osv.except_osv(_('warning!'), _('You can not print %s')%emp_data)
		    res = {
		        'name' : i.name_related ,
		        'department' : i.department_id.name ,
		        'code' : i.emp_code ,
		        'degree' : i.degree_id.name ,
		        'type' : title[i.payroll_id.military_type] ,
                        'struct':i.payroll_id.military_type,
		        'illness' : "  " , 
		        'comment' : "  " , 
		        'company_name' : emp_data and emp_data[0].department_id.name or ' ',
		        'station' :"  " , 
		        'date' : time.strftime('%Y-%m-%d') ,
		        'family' :False ,
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
