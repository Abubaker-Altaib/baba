# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp import tools
from report.interface import report_rml
from openerp.tools.translate import _
from openerp.report import report_sxw

class report_custom(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_custom, self).__init__(cr, uid, name, context)
        self.info = {'levels':0, 'company':'','title':''}
        self.localcontext.update({
            'main': self.create_xml,
            'info': self.get_info,

        })
    def get_info(self,data):
        if  data['form']['report_type'] == 'employee':
            self.info['title']="Employee record"
        elif  data['form']['report_type'] == 'relation':
            self.info['title']="Employee relation"
        else:
            self.info['title']="Employee qualification"
        self.info['company']='company' in data and data['company'] or " "     
        return self.info


    def get_param(self, data):
        append_where = " "
        if data['form']['company_id']:
            append_where += " and r.company_id=%s  " % str(data['form'].get('company_id')[0])
        if data['form']['job_ids']:
            append_where += " and e.job_id in (%s) "   % ','.join(map(str, data['form']['job_ids']))
        if data['form']['department_ids']:
            append_where += " and e.department_id in (%s) " % ','.join(map(str, data['form']['department_ids']))

        if data['form']['employee_ids']:
            append_where += " and e.id in (%s) " % ','.join(map(str, data['form']['employee_ids']))

        if  data['form']['groupby']=='company':
            query = "select  1 as level,id,name from res_company " 
            if data['form']['company_id']: query += "where id=%s" % str(data['form'].get('company_id')[0]) 
            append_where += " and  co.id=%s " 
        else:
            query = "select  3 as level,id,name from hr_department " 
            append_where += " and  d.id=%s " 
        return {'query':query,'append_where':append_where}

    def get_emp_param(self, data):
        append_select = "  "
        append_join = "  "
        label = {u'a2': u'إسم الموظف',u'a3': u'القسم',u'a4': u'نوع الموظف', 'level':4}
        append_where = " "
        if data['form']['emp_code']:
            label.update({u'a1':u'CODE'})
            append_select += " , e.emp_code as a1 "
        if data['form']['birthday']:
            append_select += " , e.birthday as a5 "
            label.update({u'a5':u'تاريخ الميلاد'})
        if data['form']['location']:
            append_select += " ,p.street||' , ' ||p.city as a6 "
            append_join += " left join res_partner p on (e.address_home_id=p.id) "
            label.update({u'a6':u'الموقع'})
        if data['form']['wizout_sinid']: 
            append_where += " and  e.sinid is Null"
        if data['form']['sinid']: 
            append_select += " , e.sinid  as a7"
            label.update({u'a7':u'SINID'}) 
        return {'label':label,'append_select':append_select, 'append_join':append_join,'append_where':append_where}

    def create_xml(self, data):
        param = self.get_param(data)
        self.cr.execute(param['query'])
        res = self.cr.dictfetchall() 
        result = []
        if data['form']['report_type'] == 'employee':
            emp_param = self.get_emp_param(data)     
            label = emp_param['label']
            print label
        for r in res: 
            #Report type 1: Employee
            if data['form']['report_type'] == 'employee': 
                self.cr.execute("SELECT 3 as level, r.name as a2 "\
					      + emp_param['append_select'] +\
					   ", d.name as a3,\
					    e.employee_type as a4\
					    FROM  hr_employee  e\
			      		left join resource_resource r on (e.resource_id = r.id)\
					    left join hr_department d on(d.id= e.department_id)\
					    left join res_company co on(co.id= r.company_id)\
					    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
					    "where e.state is not null  " +  emp_param['append_where'] +param['append_where'],(r['id'],) )  
                emp = self.cr.dictfetchall() 
                if emp: result  += [r] + emp
            else:
                self.cr.execute("SELECT 2 as level, e.id, r.name as name \
					    FROM  hr_employee  e\
			      		left join resource_resource r on (e.resource_id = r.id)\
					    left join hr_department d on(d.id= e.department_id)\
					    left join res_company co on(co.id= r.company_id)\
					    where e.state is not null  " + param['append_where'],(r['id'],) )  
                employees = self.cr.dictfetchall()     
                if employees: result  += [r]                                          
                if data['form']['report_type'] == 'relation':
                    label = {'a1': u'إسم الموظف','a2': u'نوع العلاقة',
                                'a3': u'تاريخ البداية','a4': u'تاريخ النهاية',
                                'a5': u'الإسم', 'level':4} 
                    for employee in employees: 
                        self.cr.execute(''' SELECT 3 as level ,s.name AS a1,
			                r.name AS a2,f.start_date AS a3,f.end_date AS a4,f.relation_name AS a5
			                FROM hr_employee_family as f  
			                left join  hr_family_relation AS r on (r.id=f.relation_id) 
			                left join hr_employee AS e on (f.employee_id=e.id) 
			                left join resource_resource AS s on (e.resource_id=s.id) 
			                left join res_company co on(co.id= s.company_id)
			                left join hr_department d on(d.id= e.department_id)
			                WHERE e.id=%s ''',(employee['id'],) ) 
                        relation = self.cr.dictfetchall() 
                        if relation: result  +=   [employee] + relation    
                else:
                    label = {u'a1': u'المؤهل',u'a2': u'التاريخ',u'a3': u'الجهة', 'level':4}
                    for employee in employees: 
                        self.cr.execute(''' SELECT 3 as level ,b.name as a1 ,
                            q.qual_date AS a2,q.organization AS a3 
		                       FROM hr_employee_qualification q
			                left join hr_employee e on (q.employee_id=e.id) 
			                left join hr_qualification b on (q.emp_qual_id=b.id)
			                left join resource_resource  o on  (e.resource_id=o.id) 
			                left join res_company  co on (co.id= o.company_id)
			                left join hr_department d on(d.id= e.department_id)
		                        where  e.id=%s''',(employee['id'],) ) 
                        qualification = self.cr.dictfetchall() 
                        if qualification: result  +=   [employee] + qualification                                     
        return  [label] + (result)


 
report_sxw.report_sxw('report.hr.common.report', 'hr.employee', 'hr_custom/report/report/hr_employee_report.mako',parser=report_custom)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
