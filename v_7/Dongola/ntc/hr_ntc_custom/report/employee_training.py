# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import datetime
import mx
from openerp.report import report_sxw


class employee_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(employee_form, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'user':self._get_user,
            'line':self._get_data
           })
        self.year = int(time.strftime('%Y'))

    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name


    def _get_data(self, data):
        scale_object = self.pool.get('hr.salary.scale')
        process_object = self.pool.get('hr.process.archive')
        date1 = data['date_from']
        date2 = data['date_to']
        payroll_ids = data['payroll_ids']
        refrence = 'hr.salary.degree%'
        payroll_ids = not payroll_ids and scale_object.search(self.cr,self.uid,[]) or payroll_ids
        self.year = date1 and mx.DateTime.Parser.DateTimeFromString(date1).year or self.year
        res=[]
        if date1 and date2:
            self.cr.execute(" select distinct emp.id as emp_id, emp.employment_date as employement_date, emp.birthday as birthday, "\
            "jop.name as job_name,"\
            "degree.name as degree_name,"\
            "res.name as name " \
            "from hr_employee_training_line t "\
            "left join  hr_employee emp on (emp.id=t.employee_id) "\
            "left join hr_job jop on (jop.id=emp.job_id) "\
            "left join resource_resource res on (res.id=emp.resource_id) "\
            "left join hr_salary_degree degree on(emp.degree_id=degree.id) "\
            "where emp.payroll_id in %s and "\
            "t.start_date >= %s and t.end_date <= %s ",(tuple(payroll_ids),date1,date2))
        elif date1 and not date2:
            self.cr.execute(" select distinct emp.id as emp_id, emp.employment_date as employement_date, emp.birthday as birthday, "\
            "jop.name as job_name,"\
            "degree.name as degree_name,"\
            "res.name as name " \
            "from hr_employee_training_line t "\
            "left join  hr_employee emp on (emp.id=t.employee_id) "\
            "left join hr_job jop on (jop.id=emp.job_id) "\
            "left join resource_resource res on (res.id=emp.resource_id) "\
            "left join hr_salary_degree degree on(emp.degree_id=degree.id) "\
            "where emp.payroll_id in %s and "\
            "t.start_date >= %s",(tuple(payroll_ids),date1))
        elif date2 and not date1:
            self.cr.execute(" select distinct emp.id as emp_id, emp.employment_date as employement_date, emp.birthday as birthday, "\
            "jop.name as job_name,"\
            "degree.name as degree_name,"\
            "res.name as name " \
            "from hr_employee_training_line t "\
            "left join  hr_employee emp on (emp.id=t.employee_id) "\
            "left join hr_job jop on (jop.id=emp.job_id) "\
            "left join resource_resource res on (res.id=emp.resource_id) "\
            "left join hr_salary_degree degree on(emp.degree_id=degree.id) "\
            "where emp.payroll_id in %s and "\
            "t.end_date <= %s ",(tuple(payroll_ids),date2))
        else:
            self.cr.execute(" select distinct t.employee_id as t_emp, emp.id as emp_id, emp.employment_date as employement_date, emp.birthday as birthday, "\
            "jop.name as job_name,"\
            "degree.name as degree_name,"\
            "res.name as name " \
            "from hr_employee_training_line t "\
            "left join  hr_employee emp on (t.employee_id=emp.id) "\
            "left join hr_job jop on (jop.id=emp.job_id) "\
            "left join resource_resource res on (res.id=emp.resource_id) "\
            "left join hr_salary_degree degree on(emp.degree_id=degree.id) "\
            "where emp.payroll_id in %s",(tuple(payroll_ids),))


        
        res=self.cr.dictfetchall()
        for x in res:
            self.cr.execute("select process.approve_date as date "\
                "from hr_process_archive process "\
                "where process.employee_id = %s and "\
                "process.reference like %s "\
                "order by id DESC limit 1",(x['emp_id'],refrence))
            res1 = self.cr.dictfetchall()
            x['degree_date'] = res1 and res1[0]['date'] or x['employement_date']

            # TO Add Traning_no

            self.cr.execute("select t.employee_id as te_emp "\
                "from hr_employee_training_line t "\
                "where t.employee_id = %s and t.type ='hr.approved.course' "\
                ,(x['t_emp'],))
            res3 = self.cr.dictfetchall()
            x['traning_no'] = len(res3)



            self.cr.execute("select qual.emp_qual_id as id "\
                "from hr_employee_qualification qual "\
                "where qual.employee_id = %s",(x['emp_id'],))
            result = self.cr.dictfetchall()
            if result:
                self.cr.execute("select qual.name as qual_name "\
                    "from hr_qualification qual "\
                    "where qual.id = %s",(result[0]['id'],))
                res2 = self.cr.dictfetchall()
            x['qual_name'] = result and res2 and res2[0]['qual_name'] or 'لا يوجد'


            
        return res

        

report_sxw.report_sxw('report.training.employee', 'hr.employee.training', 'addons/hr_ntc_custom/report/employee_training.rml' ,parser=employee_form ,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
