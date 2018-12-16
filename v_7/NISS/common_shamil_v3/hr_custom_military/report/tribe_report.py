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


class tribe(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(tribe, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
            'get_name': self._get_name,
        })

    def _get_name(self, data):
        key = _(data)
        department_obj = self.pool.get('hr.department')
        name = department_obj.name_get_custom(self.cr, self.uid, [data])[0][1]
        return name

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
        parent_tribe = data['form']['parent_tribe']
        tribe = data['form']['tribe']
        department_id = data['form']['department_id']
        with_childs = data['form']['with_childs']
        company_id = data['form']['company_id']
        job_id = data['form']['job_id']
        degree_id = data['form']['degree_id']


        clouses = False

        #for who_not_take emp search

        who_not_take_clouses = False

        if parent_tribe:
            parent_tribe = parent_tribe[0]
            if clouses:
                clouses += " and emp.parent_tribe="+str(parent_tribe)
            if not clouses:
                clouses = "emp.parent_tribe="+str(parent_tribe)
        
        if tribe:
            tribe = tribe[0]
            if clouses:
                clouses += " and emp.tribe="+str(tribe)
            if not clouses:
                clouses = "emp.tribe="+str(tribe)
        
        if department_id:
            department_ids = [department_id[0]]
            department_ids += department_ids
            department_ids = tuple(department_ids)
            if with_childs:
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
                clouses += " and emp.department_id in "+str(department_ids)
            if not clouses:
                clouses = "emp.department_id in "+str(department_ids)


        if company_id:
            company_id = company_id[0]
            if clouses:
                clouses += " and users.company_id="+str(company_id)
            if not clouses:
                clouses = "users.company_id="+str(company_id)

        if job_id:
            job_id = job_id[0]
            if clouses:
                clouses += " and emp.job_id="+str(job_id)
            if not clouses:
                clouses = "emp.job_id="+str(job_id)
        
        if degree_id:
            degree_id = degree_id[0]
            if clouses:
                clouses += " and emp.degree_id="+str(degree_id)
            if not clouses:
                clouses = "emp.degree_id="+str(degree_id)

        readable_emp_ids = self.pool.get('hr.employee').search(self.cr, self.uid, [])
        if readable_emp_ids:
            readable_emp_ids = readable_emp_ids + readable_emp_ids
            readable_emp_ids = tuple(readable_emp_ids)
            if clouses:
                clouses += " and emp.id in"+str(readable_emp_ids)
            if not clouses:
                clouses = "emp.id in"+str(readable_emp_ids) 
                
        query = """select parent_tribe.name as parent_tribe_name,tribe.name tribe_name,emp.otherid,emp.name_related,
                    deg.name as deg_name,job.name as job_name ,emp.department_id
                    from hr_employee emp 
                    left join hr_salary_degree deg on (emp.degree_id=deg.id) 
                    left join hr_job job on(job.id = emp.job_id) 
                    left join hr_basic parent_tribe on(parent_tribe.id = emp.parent_tribe) 
                    left join hr_basic tribe on(tribe.id = emp.tribe)
                    left join resource_resource res_res on (emp.resource_id=res_res.id)
                    left join res_users users on (res_res.user_id=users.id)
                    """

        if clouses:
            query += "where "+clouses

        query += " ORDER BY deg.sequence DESC,emp.promotion_date,LPAD(emp.otherid,20,'0')"
        self.cr.execute(query)
        res = self.cr.dictfetchall()
        
       
        #print "......................domain",query,res

        

        self.all_data = res
        
            
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.hr.tribe.report', 'hr.employee',
                      'addons/hr_custom_military/report/tribe_report.mako', parser=tribe, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
