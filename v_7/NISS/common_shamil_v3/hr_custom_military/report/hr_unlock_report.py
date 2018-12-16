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
    		#res['code'] = i.code or ""
    		res['date'] = i.start_date
    		res['emps'] = self.get_employee(i.employee_id)
    		#res['phone'] = i.airport_partner_id and i.airport_partner_id.phone or ""
    		print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>res",res
    	return res

    def get_employee(self , emp):
    	emp_data = []
        data = {
			'name' : emp.name_related ,
			'degree_seq' : emp.degree_id.sequence ,
			'code' : emp.otherid,
		}   
        return data

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(hr_unlock, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.hr_unlock_report','hr.unlock','addons/hr_custom_military/report/hr_unlock.mako',parser=hr_unlock,header=False)
