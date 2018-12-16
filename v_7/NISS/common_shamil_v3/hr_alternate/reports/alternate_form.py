# -*- coding: utf-8 -*-

from report import report_sxw
from tools.translate import _
from openerp.osv import osv, fields, orm
import time
import datetime

class alternate_form(report_sxw.rml_parse):
    '''
    @return move order data in dictionary
    '''
    def get_record(self):
    	res = {}
    	for i in self.pool.get('hr.alternative.process').browse(self.cr , self.uid , [self.context['active_id']]) :
            res['number'] = i.number or ""
            res['sequance'] = i.sequance or ""
            res['report_header'] = i.report_header and i.report_header.replace('\n', '<br/>') or ""
            res['report_alerts'] =i.report_alerts and i.report_alerts.replace('\n', '<br/>') or ""
            res['setting'] = i.alternative_setting_id and i.alternative_setting_id.name or ""
            res['date'] = datetime.date.today().strftime('%Y-%m-%d')
            res['emps'] = self.get_lines(i.lines_ids)
            res['alternative1'] = i.alternative1 
            res['alternative2'] = i.alternative2 
            res['from_company2department']=self.from_company_to_department(self.uid)
    	return res

    def get_weekday(self, str):
        key = str
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('src', '=', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return key

    def get_lines(self, lines):
        result=[]
        for line in lines:
            res={}
            res['department'] = line.employee_id.department_id.name
            res['phone'] = line.employee_id.work_phone or line.employee_id.mobile_phone
            res['employee'] = line.employee_id.name
            res['degree'] = line.degree.name
            res['date'] = line.date
            res['weekday'] = self.get_weekday(line.weekday)
            result.append(res)
        return result

    def from_company_to_department(self,uid):
        emp_obj=self.pool.get('hr.employee')
        dept_obj=self.pool.get('hr.department')
        emp=emp_obj.search(self.cr, self.uid, [('user_id','=',uid)])
    	res = ""
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
        super(alternate_form, self).__init__(cr, uid, name, context=context)
        record = self.get_record()
        self.localcontext.update(record)

report_sxw.report_sxw('report.alternate_form_report','hr.alternative.process','addons/hr_alternate/reports/alternate_form.mako',parser=alternate_form,header=True)
