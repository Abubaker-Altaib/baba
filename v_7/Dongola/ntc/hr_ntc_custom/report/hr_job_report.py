# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.report import report_sxw
from itertools import groupby
from operator import itemgetter
import time

class report_hr_job_dep(report_sxw.rml_parse):

    globals()['total'] = 0
    globals()['available'] = 0
    globals()['curr_num'] = 0
    
    def __init__(self, cr, uid, name, context):
        super(report_hr_job_dep, self).__init__(cr, uid, name, context)
        self.info = {'levels':0, 'company':'','title':''}
        self.localcontext.update({
            'main': self.create_xml,
            'total': self._total,
            'user':self._get_user,
        })

        globals()['total'] = 0
        globals()['available'] = 0
        globals()['curr_num'] = 0


    def _get_user(self,data, header=False):
        if header:
            return self.pool.get('res.company').browse(self.cr, self.uid, data['form']['company_id'][0]).logo
        else:
            return self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name


    def create_xml(self, data):
        job_obj = self.pool.get('hr.job')
        employee_substitution_obj = self.pool.get('hr.employee.substitution')
        job_ids = data['job_ids']
        num = 0
        res2 = []
        result = []
        date = time.strftime('%Y-%m-%d')
        if job_ids:
            self.cr.execute("SELECT hr_job.id as id ,hr_job.no_of_employee AS curr_num, "\
                            "hr_job.expected_employees as available_num, hr_job.no_of_recruitment as total_num, "\
                            "hr_job.name as name "\
                            "FROM hr_job "\
                            "LEFT JOIN job_degree_rel d on (d.degree_id= hr_job.id) "\
                            "LEFT JOIN hr_salary_degree deg on (deg.id= d.job_id) "\
                            "WHERE hr_job.id in %s "\
                            "order by deg.sequence, hr_job.name" ,
                            (tuple(job_ids),))
        else:
            self.cr.execute("SELECT hr_job.id as id ,hr_job.no_of_employee AS curr_num, "\
                            "hr_job.expected_employees as available_num, hr_job.no_of_recruitment as total_num, "\
                            "hr_job.name as name "\
                            "FROM hr_job "\
                            "LEFT JOIN job_degree_rel d on (d.degree_id= hr_job.id) "\
                            "LEFT JOIN hr_salary_degree deg on (deg.id= d.job_id) "\
                            "order by deg.sequence, hr_job.name" )
        res = self.cr.dictfetchall()
        grouped_lines = dict((k, [v for v in itr]) for k, itr in groupby(res, itemgetter('id')))
        vals = grouped_lines.keys()

        for idss in vals:
            emp = []
            dep = []
            degree_id = []
            num += 1
            no_emp = 0
            dep_ids = []
            rec = job_obj.browse(self.cr,self.uid,idss)
            job = grouped_lines[idss][0]
            if job['curr_num'] == None:
                 job['curr_num'] = 0 
            if job['available_num'] == None:
                 job['available_num'] = 0 
            if job['total_num'] == None:
                 job['total_num'] = 0 
            
            job['curr_num'] = int(job['curr_num'])
            job['available_num'] = int(job['available_num'])
            job['total_num'] = int(job['total_num'])
            job['no'] = num
            globals()['total'] += job['total_num']
            globals()['available'] += job['available_num']
            globals()['curr_num'] += job['curr_num']
            dep_ids += [x.id for x in rec.dep_ids]
            for x in rec.employee_ids:
                degree = x.degree_id.name
                sub_degree = ''
                dep_name = x.department_id.parent_id and (x.department_id.parent_id.name + '/' ) or ''
                
                if x.department_id.id not in dep_ids:
                    no_emp += 1
                    substitue_ids = employee_substitution_obj.search(self.cr, self.uid, ['|', ('end_date', '>=', date), ('end_date', '=', False), 
                            ('employee_id', '=', x.id), ('start_date', '<=', date)])
                    if substitue_ids:
                        sub_record = employee_substitution_obj.browse(self.cr, self.uid, substitue_ids[0])
                        sub_degree = sub_record.degree_id.name
                    emp.append({'name':x.name.encode('utf-8'),'department_id':(x.department_id.name).encode('utf-8'),'degree':degree.encode('utf-8'),'sub_degree':sub_degree.encode('utf-8')})
                    dep.append({'name':('-').encode('utf-8'),'employee_id':emp,'no_emp':no_emp})
            job['employee_id'] = emp

            for x in rec.dep_ids:
                emp1 = []
                dep_name1 = x.parent_id and (x.parent_id.name + '/' ) or ''
                no_emp = 0
                for y in rec.employee_ids:
                    sub_degree = ''
                    if y.department_id.id == x.id:
                        no_emp += 1
                        dep_name = y.department_id.parent_id and (y.department_id.parent_id.name + '/' ) or ''
                        degree = y.degree_id.name
                        sub_degree = ''
                        substitue_ids = employee_substitution_obj.search(self.cr, self.uid, ['|', ('end_date', '>=', date), ('end_date', '=', False), 
                            ('employee_id', '=', y.id), ('start_date', '<=', date)])
                        if substitue_ids:
                            sub_record = employee_substitution_obj.browse(self.cr, self.uid, substitue_ids[0])
                            sub_degree += sub_record.degree_id.name
                        emp1.append({'name':y.name.encode('utf-8'),'department_id':(y.department_id.name).encode('utf-8'),'degree':degree.encode('utf-8'),'sub_degree':sub_degree.encode('utf-8')})
                dep.append({'name':(dep_name1 + x.name).encode('utf-8'),'employee_id':emp1,'no_emp':no_emp})
            job['department_id'] = dep

            for x in rec.degree_ids:
                degree_id.append({'name':(x.name).encode('utf-8')})
            job['degree_id'] = degree_id


            result.append(job)
        res2.append(result)


        return res2

    def _total(self,data):
        return {'total':globals()['total'], 'available':globals()['available'], 'curr_num' :globals()['curr_num']}


 
report_sxw.report_sxw('report.hr.employee.job', 'hr.employee', 'addons/hr_ntc_custom/report/hr_job_report.rml',parser=report_hr_job_dep, header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
