
# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class depart_job_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        self.counter = 0
        super(depart_job_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines':self.lines,
            'jobs':self.get_jobs,
            'departments':self.get_departments,
            'counter':self.get_counter,
            'get_count_job':self.get_count_job,
            'get_count_department_job':self.get_count_department_job,
            'get_count_all':self.get_count_all,
            'get_count_department':self.get_count_department,
            'sum_name':unicode('المجموع', 'utf-8')
        })
    def get_count_department(self, department):
        departments = filter(lambda x :x['department_id'][0] in self.child_deps[department], self.emps_names)
        return len(departments)
    def get_count_all(self):
        return len(self.emps_names)
    def get_count_job(self, job):
        jobs = filter(lambda x :x['job_id'][0] ==  job, self.emps_names)
        return len(jobs)
    def get_count_department_job(self, department, job):
        jobs = filter(lambda x :x['job_id'][0] ==  job and (x['department_id'][0] in self.child_deps[department]), self.emps_names)
        return len(jobs)
    def get_counter(self):
        self.counter += 1
        return self.counter
    def get_jobs(self):
        return self.jobs_names
    def get_departments(self):
        return self.departments_names
    def lines(self,data):
        jobs_ids = data['form']['jobs']
        departments_ids = data['form']['departments']
        jobs_obj = self.pool.get('hr.job')
        department_obj = self.pool.get('hr.department')
        if not jobs_ids:
            jobs_ids = jobs_obj.search(self.cr, self.uid, [])
        
        if not departments_ids:
            departments_ids = department_obj.search(self.cr, self.uid, [('cat_id.category_type','=','organization')])

        self.jobs_names = jobs_obj.read(self.cr, self.uid, jobs_ids, ['name'])
        self.departments_names = department_obj.read(self.cr, self.uid, departments_ids, ['name'])

        self.child_deps = {}
        all_deps = []
        for dep in departments_ids:
            self.child_deps[dep] = [dep]
            #add childs of a department
            self.child_deps[dep]+= department_obj.search(self.cr, self.uid, [('id','child_of',[dep])])
            all_deps+=self.child_deps[dep]
        emps_obj = self.pool.get('hr.employee')
        emps_ids = emps_obj.search(self.cr, self.uid, [('job_id','in',jobs_ids),('department_id','in',all_deps) ])
        self.emps_names = emps_obj.read(self.cr, self.uid, emps_ids, ['department_id','job_id'])

        return True
        


report_sxw.report_sxw('report.hr.depart_job.report','suggested.attendance','addons/hr_custom_military/report/depart_job_report.mako',parser=depart_job_report,header=False)
