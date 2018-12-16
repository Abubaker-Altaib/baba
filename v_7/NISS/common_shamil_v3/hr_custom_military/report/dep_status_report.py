# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from openerp.tools.translate import _



def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class dep_status_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(dep_status_report, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
        })
    
    def _to_arabic(self, data):
        key = _(data)
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module','=', 'hr_custom_military'),('type','=', 'selection'),('src','ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key
        
        return key

    def _get_all_len(self, data):
        status_ids = data['form']['status_ids']
        department_ids = data['form']['department_ids']
        include_ch = data['form']['include_ch']

        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        who_not_go = data['form']['who_not_go']
        company_id = data['form']['company_id']

        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']


        clouses = False

        #for who_not_go emp search

        who_not_go_clouses = False

        if status_ids:
            status_ids += status_ids
            status_ids = tuple(status_ids)
            if clouses:
                clouses += " and dep_status.id in "+str(status_ids)
            if not clouses:
                clouses = "dep_status.id in "+str(status_ids)
        
        if department_ids:
            department_ids += department_ids
            department_ids = tuple(department_ids)
            if include_ch:
                self.cr.execute(""" (with recursive children as (
                select id
                from hr_department 
                where parent_id in %s 
                union all
                select a.id
                from hr_department a
                join children b on (a.parent_id=b.id)
                )
                select id from children)""" %(department_ids,))
                new_deps = [x['id'] for x in self.cr.dictfetchall()]
                new_deps += new_deps
                new_deps = tuple(new_deps)
                department_ids += new_deps
            
            if clouses:
                clouses += " and dep.id in "+str(department_ids)
            if not clouses:
                clouses = "dep.id in "+str(department_ids)

        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and move.company_id="+str(company_id)
            if not clouses:
                clouses = "move.company_id="+str(company_id)
            
            if who_not_go_clouses:
                who_not_go_clouses += " and users.company_id="+str(company_id)
            if not who_not_go_clouses:
                who_not_go_clouses = " users.company_id="+str(company_id)

        if start_date:
            if clouses:
                clouses += " and move.approve_date>='"+str(start_date)+"'"
            if not clouses:
                clouses = "move.approve_date>='"+str(start_date)+"'"

        if end_date:
            if clouses:
                clouses += " and move.approve_date<='"+str(end_date)+"'"
            if not clouses:
                clouses = "move.approve_date<='"+str(end_date)+"'"
        if job_id:
            job_id = job_id[0]
            if clouses:
                clouses += " and emp.job_id="+str(job_id)
            if not clouses:
                clouses = "emp.job_id="+str(job_id)

            if who_not_go_clouses:
                who_not_go_clouses += " and emp.job_id="+str(job_id)
            if not who_not_go_clouses:
                who_not_go_clouses = " emp.job_id="+str(job_id)
        
        if degree_id:
            degree_id = degree_id[0]
            if clouses:
                clouses += " and emp.degree_id="+str(degree_id)
            if not clouses:
                clouses = "emp.degree_id="+str(degree_id)
            
            if who_not_go_clouses:
                who_not_go_clouses += " and emp.degree_id="+str(degree_id)
            if not who_not_go_clouses:
                who_not_go_clouses = " emp.degree_id="+str(degree_id)


        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.in in"+str(readable_emp_ids) 
            
            if who_not_go_clouses:
                who_not_go_clouses += " and emp.id in "+str(readable_emp_ids)
            if not who_not_go_clouses:
                who_not_go_clouses = " emp.id in "+str(readable_emp_ids)


        query = """select emp.id as emp_id, dep.name as dep_name, move.approve_date,dep_status.name as dep_status_name,
                    emp.otherid,emp.name_related,
                    deg.name as deg_name,job.name as job_name 
                    from hr_movements_department move 
                    left join hr_employee emp on (move.employee_id=emp.id) 
                    left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                    left join hr_job job on(job.id = emp.job_id) 
                    left join hr_department dep on (move.reference=dep.id) 
                    left join hr_dep_status dep_status on (dep.dep_status_id=dep_status.id) 
                    """
        # if who_not_take:
        #     query = """select employee_id from hr_military_training training 
        #     left join hr_employee emp on (training.employee_id=emp.id) 
        #     left join hr_salary_degree deg on (emp.degree_id=deg.id)  
        #     left join hr_job job on(job.id = emp.job_id) """

        if clouses:
            query += "where "+clouses
        
        query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"

        self.cr.execute(query)
        res = self.cr.dictfetchall()

        emp_ids = [x['emp_id'] for x in res]

        emp_ids += emp_ids
        emp_ids = tuple( emp_ids ) 
        

        #to get current emps in these deps
        who_not_go_clouses_custom = who_not_go_clouses
        if department_ids:
            if who_not_go_clouses_custom:
                who_not_go_clouses_custom += " and dep.id in "+str(department_ids)
            if not who_not_go_clouses_custom:
                who_not_go_clouses_custom = " dep.id in "+str(department_ids)
        if emp_ids:
            if who_not_go_clouses_custom:
                who_not_go_clouses_custom += " and emp.id not in "+str(emp_ids)
            if not who_not_go_clouses_custom:
                who_not_go_clouses_custom = "emp.id not in "+str(emp_ids)

        query = """select emp.id as emp_id, dep.name as dep_name, 
            emp.otherid,emp.name_related, emp.join_date as approve_date,
            deg.name as deg_name,job.name as job_name,dep_status.name as dep_status_name 
            from hr_employee emp 
            left join hr_salary_degree deg on (emp.degree_id=deg.id)  
            left join hr_job job on(job.id = emp.job_id) 
            left join hr_department dep on (emp.department_id=dep.id)
            left join resource_resource res_res on (emp.resource_id=res_res.id)
            left join res_users users on (res_res.user_id=users.id) 
            left join hr_dep_status dep_status on (dep.dep_status_id=dep_status.id) """
        if who_not_go_clouses_custom:
            query += "where "+who_not_go_clouses_custom
        query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"
        self.cr.execute(query)
        res_current = self.cr.dictfetchall()
        res += res_current
        print "......................res",query
        emp_ids = [x['emp_id'] for x in res]

        if emp_ids:  
            emp_ids += emp_ids
            emp_ids = tuple( emp_ids ) 
            if who_not_go_clouses:
                who_not_go_clouses += " and emp.id not in "+str(emp_ids)
            if not who_not_go_clouses:
                who_not_go_clouses = "emp.id not in "+str(emp_ids)

            
            
            

        
            

        if who_not_go:
            query = """select emp.id as emp_id, dep.name as dep_name, 
            emp.otherid,emp.name_related,
            deg.name as deg_name,job.name as job_name 
            from hr_employee emp 
            left join hr_salary_degree deg on (emp.degree_id=deg.id)  
            left join hr_job job on(job.id = emp.job_id) 
            left join hr_department dep on (emp.department_id=dep.id)
            left join resource_resource res_res on (emp.resource_id=res_res.id)
            left join res_users users on (res_res.user_id=users.id) """
            if who_not_go_clouses:
                query += "where "+who_not_go_clouses
            query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"
            self.cr.execute(query)
            res = self.cr.dictfetchall()



        # if who_not_take:
        #     in_emps = [x['employee_id'] for x in res]
        #     in_emps += in_emps
        #     if in_emps:
        #         in_emps = tuple(in_emps)
        #         query = """select emp.otherid,emp.name_related,
        #                     deg.name as deg_name,job.name as job_name  
        #                     from hr_employee emp 
        #                     left join hr_salary_degree deg on (emp.degree_id=deg.id) 
        #                     left join hr_job job on(job.id = emp.job_id) 
        #                     where emp.state='approved' and emp.id not in """+str(in_emps)
        #         if who_not_take_clouses:
        #             query += "and "+ who_not_take_clouses
        #     if not in_emps:
        #         query = """select emp.otherid,emp.name_related,
        #                     deg.name as deg_name,job.name as job_name  
        #                     from hr_employee emp 
        #                     left join hr_salary_degree deg on (emp.degree_id=deg.id) 
        #                     left join hr_job job on(job.id = emp.job_id) 
        #                     where emp.state='approved' """
        #         if who_not_take_clouses:
        #             query += "and "+ who_not_take_clouses

        #    self.cr.execute(query)
        #    res = self.cr.dictfetchall()





        

        
       

        #print "......................domain",query,res

        


        self.all_data = res
        
            
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.hr.dep_status.report', 'hr.employee',
                      'addons/hr_custom_military/report/dep_status_report.mako', parser=dep_status_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
