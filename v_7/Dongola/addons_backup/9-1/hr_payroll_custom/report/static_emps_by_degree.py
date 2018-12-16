# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
            'degree':self.get_degree,

        })
    def get_degree(self,data):

        row = []
        emp_obj = self.pool.get('hr.employee')
        start_date = data['start_date'] and data['start_date'] or datetime.now() - relativedelta(years=100)
        end_date = data['end_date'] and data['end_date'] or time.strftime('%Y-%m-%d')
        for dg in data['degree_ids']:
            emp_ids = [] 
            if data['start_date'] or data['end_date'] :
                self.cr.execute("""SELECT employee_id 
                              FROM   hr_process_archive
                              WHERE reference like 'hr.salary.degree%%' """ + """ and
                              state = 'approved' and 
                              approve_date >= %s and
                              approve_date <= %s  and
                              substring(reference,18,1) =%s """,(start_date, end_date, str(dg)))
                res= self.cr.fetchall()
                emp_ids += [emp[0] for emp in res if res]
            emp_ids += emp_obj.search(self.cr,self.uid, [('state', '=', 'approved'),
                                                         ('degree_id', '=', dg),
                                                         ('promotion_date', '>=', start_date),
                                                         ('promotion_date', '<=', end_date)])
            emp_ids += emp_obj.search(self.cr,self.uid, [('state', '=', 'approved'),
                                                         ('degree_id', '=', dg),
                                                         ('promotion_date', '=', False)])
            emp_ids = list(set(emp_ids))
            count = 0
            col = []
            d_emp = []
            print"================",d_emp
            for emp in emp_obj.browse(self.cr,self.uid,emp_ids):
                
                dtl = []
                count+=1
                dtl.append(count)
                dtl.append(emp.name)
                dtl.append(emp.job_id.name)
                dept = emp.department_id.name 
                if emp.department_id.parent_id : dept+= "/ " + emp.department_id.parent_id.name
                if  emp.department_id.parent_id.parent_id: dept+= "/ " + + emp.department_id.parent_id.parent_id.name
                dtl.append(dept)
                d_emp.append(dtl)
            if not emp_ids: continue
            col.append(emp.degree_id.name)
            col.append( d_emp)
            row.append(col)
        for r in row:
            print"...............",r
        return  row

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

report_sxw.report_sxw('report.emp_based', 'hr.employee', 'hr_payroll_custom/report/static_deg_by_emp_landscape.rml' ,parser=degree_based ,header="internal landscape")
report_sxw.report_sxw('report.degree_based', 'hr.employee', 'hr_payroll_custom/report/static_emps_by_degree.mako' ,parser=degree_based ,header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
