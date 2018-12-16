# -*- coding: utf-8 -*-

from report import report_sxw

title = {
    'officer' : unicode('ر.البطاقة', 'utf-8') ,
    'soldier' : unicode('نمرة', 'utf-8'),
}

class emp_record_report(report_sxw.rml_parse):
		

	def _get_record(self):
		wiz_obj = self.pool.get('emp_record_wizard.report')
		objs = wiz_obj.browse(self.cr , self.uid , [self.context['active_id']])
		res = []
		for o in objs :
			if o.employee_ids :
				for emp in o.employee_ids :
					data = {
						'emp_code' : emp.emp_code ,
						'name' : emp.name_related ,
						'degree_name' : emp.degree_id.name, 
						'birthday' : emp.birthday, 
						'religion' : emp.religion or "", 
						'qualification' : 'Q', 
						'pl_state' : emp.pl_state and emp.pl_state.name or "" , 
						'local' : emp.local and emp.local.name or "" , 
						'managiral_unit' : emp.managiral_unit and emp.managiral_unit.name or "" , 
						'tribe' : emp.tribe and emp.tribe.name or "", 
						'job' : emp.job_id.name , 
						'marital' : emp.marital or "", 
						'no' : emp.identification_id or ' - ', 
						'blood_type' : emp.blood_type or "" , 
						'ne' : emp.ne_name or ' ' , 
						'mother' : emp.mother_name, 
						'recruitment_date' : emp.recruitment_date , 
						'end_date' : emp.end_date, 
						'additional_service' : 'split', 
					}
					res.append(data)
			else : print "Nooooooone"
			print "###########################33 rrr " , res
		return {'employees' : res}

	def __init__(self, cr, uid, name, context):
		self.cr = cr
		self.uid = uid
		self.context = context
		super(emp_record_report, self).__init__(cr, uid, name, context=context)
		employee_objs = self._get_record()
		self.localcontext.update(employee_objs)

		
report_sxw.report_sxw('report.emp_record_report','hr.employee','addons/hr_custom_military/report/emp_record_report.mako',parser=emp_record_report,header=False)