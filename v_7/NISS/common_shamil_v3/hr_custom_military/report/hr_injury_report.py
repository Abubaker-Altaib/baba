# -*- coding: utf-8 -*-

from report import report_sxw

title = {
    'officer' : unicode('ر.البطاقة', 'utf-8') ,
    'soldier' : unicode('نمرة', 'utf-8'),
}

class hr_injury(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('hr.injury').browse(self.cr , self.uid , [self.context['active_id']]) :
            res['code'] = i.name.otherid
            res['name'] = i.name.name_related
            res['type'] = title[i.name.payroll_id.military_type]
            res['degree'] = i.name.degree_id.name
            res['company_name'] = self.pool.get('res.users').browse(self.cr , self.uid , [self.uid])[0].company_id.name or ""
            res['date'] = i.injury_date or ""
            res['place'] = i.injury_place or ""
            res['inability_date'] = i.inability_date or ""
            res['inability_per'] = i.inability_percentage or ""
            res['ref_date'] = i.ref_date or ""
            res['ref'] = i.ref or ""
            res['decision'] = i.decision or ""
            res['approve'] = i.department_id and self.pool.get('hr.move.order').get_department_manger(self.cr ,self.uid, i.department_id.id) or ""
        return res

    def __init__(self, cr, uid, name, context):
        print "####################3 injury"
        self.cr = cr
        self.uid = uid
        self.context = context
        super(hr_injury, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.hr_injury_report','hr.injury','addons/hr_custom_military/report/hr_injury_report.mako',parser=hr_injury,header=False)
