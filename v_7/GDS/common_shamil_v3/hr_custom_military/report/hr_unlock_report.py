# -*- coding: utf-8 -*-

from report import report_sxw

class hr_unlock(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('hr.unlock').browse(self.cr , self.uid , [self.context['active_id']]) :
    		res['state'] = i.state
    		res['dest'] = i.destination or ""
    		res['code'] = i.code or ""
    		res['date'] = i.start_date
    		res['emps'] = self.get_employees(i.employee_ids)
    		res['phone'] = i.airport_partner_id and i.airport_partner_id.phone or ""
    	return res

    def get_employees(self , objs):
    	emp_data = []
    	for emp in objs :
    		data = {
    			'name' : emp.name_related ,
    			'degree_seq' : emp.degree_id.sequence ,
				'code' : emp.emp_code,
    		}   
    		emp_data.append(data)
        temp = sorted(emp_data, key=lambda k: k['code']) #sorting using code
        temp = sorted(emp_data, key=lambda k: k['degree_seq'],reverse=True) #sorting using degree 
        return temp

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(hr_unlock, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.hr_unlock_report','hr.unlock','addons/hr_custom_military/report/hr_unlock.mako',parser=hr_unlock,header=False)
