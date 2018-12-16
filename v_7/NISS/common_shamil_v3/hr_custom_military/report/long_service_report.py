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


class long_service(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(long_service, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
        })
    
    def _get_years(self, gift):
        if gift.give_condition == 'employment_date':
            return gift.years
        else:
            return gift.years + self._get_years(gift.last_gift_id)
    
    def _get_candidates(self, data):
        employee_id = data['form']['employee_id']
        department_id = data['form']['department_id']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        gift_id = data['form']['gift_id']

        gift_id = gift_id[0]
        
        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']
        payroll_id = data['form']['payroll_id']
        clouses = " emp.state='approved'"

        if employee_id:
            employee_id = employee_id[0]
            if clouses:
                clouses += " and emp.id="+str(employee_id)
            if not clouses:
                clouses = " emp.id="+str(employee_id)
            

        if department_id:
            department_id = department_id[0]
            domain = ['|',('id','=',department_id),('id','child_of',department_id)]
            deps_ids = self.pool.get("hr.department").search(self.cr, self.uid, domain)
            if deps_ids:
                deps_ids += deps_ids
                deps_ids = tuple(deps_ids)
                if clouses:
                    clouses += " and emp.department_id in "+str(deps_ids)
                if not clouses:
                    clouses = " emp.department_id in "+str(deps_ids)


        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and users.company_id="+str(company_id)
            if not clouses:
                clouses = "  users.company_id="+str(company_id)

        if job_id:
            job_id = job_id[0]
            if clouses:
                clouses += " and emp.job_id="+str(job_id)
            if not clouses:
                clouses = " emp.job_id="+str(job_id)

        
        if degree_id:
            degree_id = degree_id[0]
            if clouses:
                clouses += " and emp.degree_id="+str(degree_id)
            if not clouses:
                clouses = " emp.degree_id="+str(degree_id)


        if payroll_id:
            payroll_id = payroll_id[0]
            if clouses:
                clouses += " and emp.payroll_id="+str(payroll_id)
            if not clouses:
                clouses = " emp.payroll_id="+str(payroll_id)

            
        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.id in"+str(readable_emp_ids)

        sub_query = """select long_service.employee_id from hr_long_service long_service 
                    where long_service.state='done' and long_service.gift_id="""+str(gift_id)

        self.cr.execute(sub_query)
        sub_res = self.cr.dictfetchall()

        sub_res = [x['employee_id'] for x in sub_res]

        if sub_res:
            sub_res = sub_res + sub_res
            sub_res = tuple(sub_res)
            if clouses:
                clouses += " and emp.id not in"+str(sub_res)
            if not clouses:
                clouses = "emp.id not in"+str(sub_res)

        query = """select emp.id  
                    from hr_employee emp 
                    left join resource_resource res_res on (emp.resource_id=res_res.id)
                    left join res_users users on (res_res.user_id=users.id) 
                    """
        
        if clouses:
            query += "where "+clouses


        self.cr.execute(query)
        res = self.cr.dictfetchall()

        res = [x['id'] for x in res]
        temp_list = []
        
        gift_id = self.pool.get('hr.gift').browse(self.cr, self.uid, gift_id)
        gift_years = self._get_years(gift_id)
        res = self.pool.get('hr.employee').actual_duration_computation_custom(self.cr, self.uid, res,end_date )

        for i in res:
            if res[i]['total_service_years'] >= gift_years:
                temp_list.append(i)

        self.all_data = []
        print"................tmep_list",temp_list
        if temp_list:

            temp_list = temp_list + temp_list
            temp_list = tuple(temp_list)

            clouses = "emp.id in"+str(temp_list)

            query = """select emp.otherid,emp.name_related,emp.employment_date,
                        deg.name as deg_name,job.name as job_name, dep.name as dep_name 
                        from hr_employee emp 
                        left join hr_salary_scale pay on (emp.payroll_id=pay.id) 
                        left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                        left join hr_job job on(job.id = emp.job_id) 
                        left join hr_department dep on(dep.id = emp.department_id) 
                        """

            if clouses:
                query += "where "+clouses
            query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"
            self.cr.execute(query)
            res = self.cr.dictfetchall()

            self.all_data = res
        
            
        return len(self.all_data)

    def _get_all_len(self, data):
        employee_id = data['form']['employee_id']
        department_id = data['form']['department_id']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        company_id = data['form']['company_id']
        gift_id = data['form']['gift_id']
        candidate = data['form']['candidate']
        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']
        payroll_id = data['form']['payroll_id']

        if candidate:
            return self._get_candidates(data)

        


        clouses = " long_service.state='done'"
        

        if gift_id:
            gift_id = gift_id[0]
            if clouses:
                clouses += " and gift.id="+str(gift_id)
            if not clouses:
                clouses = " gift.id="+str(gift_id)

        if employee_id:
            employee_id = employee_id[0]
            if clouses:
                clouses += " and emp.id="+str(employee_id)
            if not clouses:
                clouses = " emp.id="+str(employee_id)
            

        if department_id:
            department_id = department_id[0]
            domain = ['|',('id','=',department_id),('id','child_of',department_id)]
            deps_ids = self.pool.get("hr.department").search(self.cr, self.uid, domain)
            if deps_ids:
                deps_ids += deps_ids
                deps_ids = tuple(deps_ids)
                if clouses:
                    clouses += " and emp.department_id in "+str(deps_ids)
                if not clouses:
                    clouses = " emp.department_id in "+str(deps_ids)


        
        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and long_service.company_id="+str(company_id)
            if not clouses:
                clouses = "  long_service.company_id="+str(company_id)

        if start_date:
            if clouses:
                clouses += " and long_service.date>='"+str(start_date)+"'"
            if not clouses:
                clouses = " long_service.date>='"+str(start_date)+"'"

        if end_date:
            clouses += " and long_service.date<='"+str(end_date)+"'"

        if job_id:
            job_id = job_id[0]
            if clouses:
                clouses += " and emp.job_id="+str(job_id)
            if not clouses:
                clouses = " emp.job_id="+str(job_id)

        
        if degree_id:
            degree_id = degree_id[0]
            if clouses:
                clouses += " and emp.degree_id="+str(degree_id)
            if not clouses:
                clouses = " emp.degree_id="+str(degree_id)


        if payroll_id:
            payroll_id = payroll_id[0]
            if clouses:
                clouses += " and emp.payroll_id="+str(payroll_id)
            if not clouses:
                clouses = " emp.payroll_id="+str(payroll_id)

            
        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.in in"+str(readable_emp_ids) 

        query = """select long_service.date,gift.name as gift_name,
		            emp.otherid,emp.name_related,emp.employment_date,long_service.next_allow_date,
                    deg.name as deg_name,job.name as job_name, dep.name as dep_name 
                    from hr_long_service long_service 
                    left join hr_gift gift on (long_service.gift_id=gift.id)
                    left join hr_employee emp on (long_service.employee_id=emp.id)
                    left join hr_salary_scale pay on (emp.payroll_id=pay.id)  
                    left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                    left join hr_job job on(job.id = emp.job_id) 
                    left join hr_department dep on(dep.id = emp.department_id) 
                    """

        if clouses:
            query += "where "+clouses
        query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"
        self.cr.execute(query)
        res = self.cr.dictfetchall()

        self.all_data = res
        
            
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.hr.long_service.report', 'hr.long.service',
                      'addons/hr_custom_military/report/long_service_report.mako', parser=long_service, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
