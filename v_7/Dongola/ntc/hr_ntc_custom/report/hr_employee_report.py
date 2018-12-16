# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.report import report_sxw
import time

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
            self.info.update({'title':u'سجلات الموظفين','col_no':3})
        elif  data['form']['report_type'] == 'relation':
            self.info.update({'title':u"كفالات الموظفين",'col_no':5})
        else:
            self.info.update({'title':u"مؤهلات الموظفين",'col_no':3})
        self.info['company']='company' in data and data['company'] or " "     
        return self.info


    def get_param(self, data):
        department_obj = self.pool.get('hr.department')
        append_where = " "
        if data['form']['company_id']:
            append_where += " and r.company_id=%s  " % str(data['form'].get('company_id')[0])
        if data['form']['job_ids']:
            append_where += " and e.job_id in (%s) "   % ','.join(map(str, data['form']['job_ids']))
        if data['form']['department_ids']:
            if  data['form']['groupby'] != 'company':
                dep_ids = department_obj.search(self.cr, self.uid, [('id','child_of', data['form']['department_ids'])])
                append_where += " and e.department_id in (%s) " % ','.join(map(str, dep_ids))
            else:
                append_where += " and e.department_id in (%s) " % ','.join(map(str, data['form']['department_ids']))

        if data['form']['employee_ids']:
            append_where += " and e.id in (%s) " % ','.join(map(str, data['form']['employee_ids']))

        if  data['form']['groupby']=='company':
            query = "select  1 as level,res_company.id,res_company.name from res_company " 
            if data['form']['company_id']: query += "where id=%s" % str(data['form'].get('company_id')[0]) 
            append_where += " and  co.id=%s " 
        else:
            query = "select 3 as level, hr_department.id, hr_department.name from hr_department " 
            #append_where += " and  d.id=%s " 
        return {'query':query,'append_where':append_where}

    def get_emp_param(self, data):
        append_select = "  "
        append_join = "  "
        label = {u'a0': u'#',u'a2': u'إسم الموظف',u'a3': u'القسم',u'a4': u'الدرجة', 'level':4}
        append_where = " "
        if data['form']['emp_code']:
            label.update({u'a1':u'CODE'})
            append_select += " , e.emp_code as a1 "
        if data['form']['birthday']:
            append_select += " , e.birthday as a6 "
            label.update({u'a6':u'تاريخ الميلاد'})
        if data['form']['location']:
            append_select += " ,p.street||' , ' ||p.city as a7 "
            append_join += " left join res_partner p on (e.address_home_id=p.id) "
            label.update({u'a7':u'الموقع'})
        if data['form']['wizout_sinid']: 
            append_where += " and  e.sinid is Null"
        if data['form']['sinid']: 
            append_select += " , e.sinid  as a8"
            label.update({u'a8':u'SINID'})
        if data['form']['substitution']: 
            label.update({u'a5':u'درجة الانابة'})
        return {'label':label,'append_select':append_select, 'append_join':append_join,'append_where':append_where}

    def create_xml(self, data):
        param = self.get_param(data)
        param1 = param.copy()
        emp_obj = self.pool.get('hr.employee')
        degree_cat = self.pool.get('hr.degree.category')
        degree_obj = self.pool.get('hr.salary.degree')
        department_obj = self.pool.get('hr.department')
        employee_substitution_obj = self.pool.get('hr.employee.substitution')
        self.cr.execute(param['query'])
        res = self.cr.dictfetchall() 
        result = []
        date = time.strftime('%Y-%m-%d')
        if data['form']['report_type'] == 'employee':
            emp_param = self.get_emp_param(data)     
            label = emp_param['label']
        for r in res:
            #Report type 1: Employee
            if data['form']['report_type'] == 'employee': 
                work_idss = []
                emp_sub_ids = []
                state = 'approve'
            


                if data['form']['substitution']:
                    substitue_ids = employee_substitution_obj.search(self.cr, self.uid, ['|', ('end_date', '>=', date), ('end_date', '=', False), 
                             ('start_date', '<=', date), ('state','=','approve')])
                    if substitue_ids:
                        for sub in employee_substitution_obj.browse(self.cr, self.uid, substitue_ids):
                            emp_sub_ids.append(sub.employee_id.id)

                param['append_where'] = param1['append_where']
                if  data['form']['groupby']=='department':
                    dep_ids = department_obj.search(self.cr, self.uid, [('id','child_of', r['id'])])
                    emp_ids = emp_obj.search(self.cr, self.uid, [('department_id','in', dep_ids)])
                    if emp_ids:
                        param['append_where'] += " and  d.id in %s "
                        if data['form']['substitution']:
                            self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                    + emp_param['append_select'] +\
                                ", d.name as a3,\
                                    de.name as a4, de1.name as a5\
                                    FROM  hr_employee  e\
                                    left join resource_resource r on (e.resource_id = r.id)\
                                    left join hr_department d on(d.id= e.department_id)\
                                    left join res_company co on(co.id= r.company_id)\
                                    left join hr_salary_degree de on(e.degree_id= de.id)\
                                    left join hr_employee_substitution sub on(e.id= sub.employee_id)\
                                    left join hr_salary_degree de1 on(sub.degree_id= de1.id)\
                                    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                    "where e.state not in %s  and e.id in %s and (sub.end_date >= %s or sub.end_date is Null) \
                                    and sub.state = %s and sub.start_date <= %s " +  emp_param['append_where'] +param['append_where'] +\
                                    " order by de.sequence,r.name ",(tuple(['refuse','draft']),tuple(emp_ids), 
                                        date, 'approve', date,tuple(dep_ids),) )

                        if data['form']['worker']:
                            self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                    + emp_param['append_select'] +\
                                ", d.name as a3,\
                                    de.name as a4, de1.name as a5\
                                    FROM  hr_employee  e\
                                    left join resource_resource r on (e.resource_id = r.id)\
                                    left join hr_department d on(d.id= e.department_id)\
                                    left join res_company co on(co.id= r.company_id)\
                                    left join hr_salary_degree de on(e.degree_id= de.id)\
                                    left join hr_degree_category cat on(de.category_id= cat.id)\
                                    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                    "where e.state not in %s  and e.id in %s and cat.worker = True " +  emp_param['append_where'] +param['append_where'] +\
                                    " order by de.sequence,r.name ",(tuple(['refuse','draft']),tuple(emp_ids),tuple(dep_ids),) )

                        else:
                            self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                    + emp_param['append_select'] +\
                                ", d.name as a3,\
                                    de.name as a4\
                                    FROM  hr_employee  e\
                                    left join resource_resource r on (e.resource_id = r.id)\
                                    left join hr_department d on(d.id= e.department_id)\
                                    left join res_company co on(co.id= r.company_id)\
                                    left join hr_salary_degree de on(e.degree_id= de.id)\
                                    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                    "where e.state not in %s  and e.id in %s  " +  emp_param['append_where'] +param['append_where'] +\
                                    " order by de.sequence,r.name ",(tuple(['refuse','draft']),tuple(emp_ids),tuple(dep_ids),) ) 
                    else:
                        param['append_where'] += " and  d.id = %s "
                        if data['form']['substitution']:
                            self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                    + emp_param['append_select'] +\
                                ", d.name as a3,\
                                    de.name as a4, de1.name as a5\
                                    FROM  hr_employee  e\
                                    left join resource_resource r on (e.resource_id = r.id)\
                                    left join hr_department d on(d.id= e.department_id)\
                                    left join res_company co on(co.id= r.company_id)\
                                    left join hr_salary_degree de on(e.degree_id= de.id)\
                                    left join hr_employee_substitution sub on(e.id= sub.employee_id)\
                                    left join hr_salary_degree de1 on(sub.degree_id= de1.id)\
                                    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                    "where e.state not in %s and (sub.end_date >= %s or sub.end_date is Null) \
                                    and sub.state = %s and sub.start_date <= %s " +  emp_param['append_where'] +param['append_where'] +\
                                    " order by de.sequence,r.name ",(tuple(['refuse','draft']), 
                                        date, 'approve', date,r['id'],) )

                        if data['form']['worker']:
                            self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                    + emp_param['append_select'] +\
                                ", d.name as a3,\
                                    de.name as a4, de1.name as a5\
                                    FROM  hr_employee  e\
                                    left join resource_resource r on (e.resource_id = r.id)\
                                    left join hr_department d on(d.id= e.department_id)\
                                    left join res_company co on(co.id= r.company_id)\
                                    left join hr_salary_degree de on(e.degree_id= de.id)\
                                    left join hr_degree_category cat on(de.category_id= cat.id)\
                                    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                    "where e.state not in %s  and e.id in %s and cat.worker = True " +  emp_param['append_where'] +param['append_where'] +\
                                    " order by de.sequence,r.name ",(tuple(['refuse','draft']),tuple(emp_ids),r['id'],) )


                        else:
                            self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                    + emp_param['append_select'] +\
                                ", d.name as a3,\
                                    de.name as a4\
                                    FROM  hr_employee  e\
                                    left join resource_resource r on (e.resource_id = r.id)\
                                    left join hr_department d on(d.id= e.department_id)\
                                    left join res_company co on(co.id= r.company_id)\
                                    left join hr_salary_degree de on(e.degree_id= de.id)\
                                    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                    "where  e.state not in %s  " +  emp_param['append_where'] +param['append_where'] +\
                                    " order by de.sequence,r.name ",(tuple(['refuse','draft']),r['id'],) )
                
                else:
                    if data['form']['substitution']:
                            self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                    + emp_param['append_select'] +\
                                ", d.name as a3,\
                                    de.name as a4, de1.name as a5\
                                    FROM  hr_employee  e\
                                    left join resource_resource r on (e.resource_id = r.id)\
                                    left join hr_department d on(d.id= e.department_id)\
                                    left join res_company co on(co.id= r.company_id)\
                                    left join hr_salary_degree de on(e.degree_id= de.id)\
                                    left join hr_employee_substitution sub on(e.id= sub.employee_id)\
                                    left join hr_salary_degree de1 on(sub.degree_id= de1.id)\
                                    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                    "where e.state not in %s and (sub.end_date >= %s or sub.end_date is Null) \
                                    and sub.state = %s and sub.start_date <= %s " +  emp_param['append_where'] +param['append_where'] +\
                                    " order by de.sequence,r.name ",(tuple(['refuse','draft']), date, state, date,r['id'],) )
                    
                    elif data['form']['worker']:
                            self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                    + emp_param['append_select'] +\
                                ", d.name as a3,\
                                    de.name as a4 \
                                    FROM  hr_employee  e\
                                    left join resource_resource r on (e.resource_id = r.id)\
                                    left join hr_department d on(d.id= e.department_id)\
                                    left join res_company co on(co.id= r.company_id)\
                                    left join hr_salary_degree de on(e.degree_id= de.id)\
                                    left join hr_degree_category cat on(de.category_id= cat.id)\
                                    left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                    "where e.state not in %s and cat.worker = True " +  emp_param['append_where'] +param['append_where'] +\
                                    " order by de.sequence,r.name ",(tuple(['refuse','draft']),r['id'],) )

                    else:
                        self.cr.execute("SELECT 3 as level, r.name as a2 "\
                                + emp_param['append_select'] +\
                            ", d.name as a3,\
                                de.name as a4\
                                FROM  hr_employee  e\
                                left join resource_resource r on (e.resource_id = r.id)\
                                left join hr_department d on(d.id= e.department_id)\
                                left join res_company co on(co.id= r.company_id)\
                                left join hr_salary_degree de on(e.degree_id= de.id)\
                                left join hr_job j on (j.id= e.job_id) " + emp_param['append_join'] +\
                                "where e.state not in %s  " +  emp_param['append_where'] +param['append_where'] +\
                                " order by de.sequence,r.name ",(tuple(['refuse','draft']),r['id'],) )  
                emp = self.cr.dictfetchall()
                count = 0
                for x in emp:
                    count += 1
                    x['a0'] = count
                r.pop('id')
                if emp: result  += [r] + [label] + emp
            else:
                if  data['form']['groupby']=='department':
                    param['append_where'] = param1['append_where']
                    param['append_where'] += " and  d.id = %s "
                self.cr.execute("SELECT 2 as level, e.id, r.name as name \
					    FROM  hr_employee  e\
			      		left join resource_resource r on (e.resource_id = r.id)\
					    left join hr_department d on(d.id= e.department_id)\
					    left join res_company co on(co.id= r.company_id) \
                        left join hr_salary_degree de on(e.degree_id= de.id) \
					    where e.state not in %s  " + param['append_where'] +\
                        " order by de.sequence,r.name",(tuple(['refuse','draft']),r['id'],) )  
                employees = self.cr.dictfetchall()
                r.pop('id')   
                if employees: result  += [r]                                          
                if data['form']['report_type'] == 'relation':
                    label = {'a0':u'#','a1': u'إسم المولود','a2': u'نوع العلاقة',
                                'a3': u'تاريخ الميلاد','a4': u'تاريخ البداية','a5': u'تاريخ النهاية',
                                 'level':4} 
                    for employee in employees: 
                        self.cr.execute(''' SELECT 3 as level ,f.birth_date AS a3,
                         r.name AS a2,f.start_date AS a4,f.end_date AS a5,f.relation_name AS a1
			                FROM hr_employee_family as f  
			                left join  hr_family_relation AS r on (r.id=f.relation_id) 
			                left join hr_employee AS e on (f.employee_id=e.id) 
			                left join resource_resource AS s on (e.resource_id=s.id) 
			                left join res_company co on(co.id= s.company_id)
			                left join hr_department d on(d.id= e.department_id)
			                WHERE e.id=%s ''',(employee['id'],) ) 
                        relation = self.cr.dictfetchall() 
                        employee.pop('id')
                        count = 0
                        for x in relation:
                            count += 1
                            x['a0'] = count
                        if relation: result  +=  [employee] + [label] + relation    
                else:
                    label = {'a0':u'#',u'a1': u'المؤهل',u'a2': u'التاريخ',u'a3': u'الجهة', 'level':4}
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
                        employee.pop('id')
                        count = 0
                        for x in qualification:
                            count += 1
                            x['a0'] = count
                        if qualification: result  +=   [employee] + [label] + qualification
        return (result) 


 
report_sxw.report_sxw('report.hr.common.ntc.report', 'hr.employee', 'hr_ntc_custom/report/hr_employee_report.mako',parser=report_custom)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
