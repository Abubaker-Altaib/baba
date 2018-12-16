# -*- coding: utf-8 -*-

from report import report_sxw

title = {
    'officer' : unicode('ر.البطاقة', 'utf-8') ,
    'soldier' : unicode('نمرة', 'utf-8'),
}

move_order_type = {
    'opreation': unicode('عمليات', 'utf-8') ,
    'mission':unicode('مأمورية', 'utf-8'),
    'transmission': unicode('إرسالية', 'utf-8'),
    'movement':unicode('تنقلات', 'utf-8'),
    'commision': unicode('قمسيون', 'utf-8'),
    'append': unicode('إلحاق', 'utf-8'),
    'join': unicode('انضمام لوحدته', 'utf-8') ,
}

class move_order_report(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('hr.move.order.advance').browse(self.cr , self.uid , [self.context['active_id']]) :
            res['employees'] = self.get_employees(i.move_order_line_ids)
            res['destination'] =  i.destination or unicode('غير محدد', 'utf-8')
            res['type'] = i.type and move_order_type[i.type] or unicode('غير محدد', 'utf-8')
            res['weapon'] = i.weapon or unicode('لا يكن', 'utf-8')
            res['ammu'] = i.ammu or unicode('لا يكن', 'utf-8')
            res['equipment'] = i.clothes or unicode('حسب التعليمات', 'utf-8')
            res['leader_id'] = i.method or unicode('المتاحة', 'utf-8')
            res['move_date'] = i.move_date or unicode('غير محدد', 'utf-8')
            res['road'] = i.road or ""
            res['company_name'] = i.company_id.name or ""
            res['power'] = i.power or ""
            res['vehicle'] = i.vehicle or ""
    	return res

    def get_employees(self , objs):
        emp_data = []
        for line in objs :
            emp = line.employee_id
            data = {
                'degree_seq' : emp.degree_id.sequence , #order sequence of employee degree . help in sorting
                'name' : emp.name_related ,
                'type' : title[emp.payroll_id.military_type] ,
                'degree' : emp.degree_id.name ,
                'code' : emp.emp_code,
            }
            emp_data.append(data)
        temp = sorted(emp_data, key=lambda k: k['code']) #sorting using code
        temp2 = sorted(temp, key=lambda k: k['degree_seq'],reverse=True) #sorting using degree 
        return temp2

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        super(move_order_report, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.move_order_advance_report','hr.move.order.advance','addons/hr_custom_military/report/move_order_advance.mako',parser=move_order_report,header=False)
