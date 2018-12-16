# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.report import report_sxw
from mako.template import Template
from openerp.report.interface import report_rml
from openerp.report.interface import toxml

class degree_based(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(degree_based, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'process':self._process,
            #'total':self.get_total,

        })

    def get_jobs(self,data):
        self.cr.execute("""SELECT distinct jview.id  
                           FROM hr_job jnormal 
                           LEFT JOIN hr_job jview ON (jview.id=jnormal.parent_id)
                           WHERE jview.type='view'
                           AND jnormal.id IN (SELECT distinct emp.job_id
                                              FROM  hr_employee emp
                                              LEFT JOIN hr_job job ON (job.id=emp.job_id)
                                              WHERE emp.state not in ('draft','refuse') AND emp.degree_id IN %s)""",(tuple(data['degree_ids']),))
        res= self.cr.fetchall()
        jobs=[r[0] for r in res if res] 
        return jobs

    def jobs(self,data):
        row=[]
        jobs=[]
        self.cr.execute("""SELECT count(emp.id) as count,
                          emp.job_id as job_id , job.name AS job,
                          emp.degree_id as degree_id, deg.name AS degree
                          FROM  hr_employee emp
                          LEFT JOIN hr_job job ON (job.id=emp.job_id)
                          LEFT JOIN hr_salary_degree deg ON (deg.id=emp.degree_id)
                          WHERE emp.state not in ('draft','refuse') AND emp.degree_id IN %s
                          GROUP BY emp.job_id, job.name,emp.degree_id,deg.name
                          ORDER BY emp.degree_id,emp.job_id""",(tuple(data['degree_ids']),))
        res= self.cr.dictfetchall()
        jobs=dict([((r['job_id'],r['degree_id']), r['count']) for r in res]) 
        return jobs

    def _process(self,data):
        row=[]
        col=[]
        sums=[]
        job_obj=self.pool.get('hr.job')
        jobs=self.get_jobs(data)
        job_ids=job_obj.browse(self.cr,self.uid, jobs)
        degree_ids=self.pool.get('hr.salary.degree').browse(self.cr,self.uid, data['degree_ids'])

        for degree in degree_ids :
            col.append(degree.name)
            sums.append(0)
        col.append(u'الوظيفة/الدرجة ')

        row.append(col)
        datas=self.jobs(data)
        child_job_ids=[]
        for job in job_ids:
            col=[]
            child_job_ids = job_obj.search(self.cr, self.uid, [('parent_id', 'child_of', job.id)])
            for degree in degree_ids :
                count=0
                for j in child_job_ids:
                    count+= datas.get((j,degree.id), 0)
                col.append(count)
            col.append(job.name)
            row.append(col)
         
        return row

report_sxw.report_sxw('report.degree_based', 'hr.employee', 'hr_payroll_custom/report/static_emps_by_degree.mako' ,parser=degree_based ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
