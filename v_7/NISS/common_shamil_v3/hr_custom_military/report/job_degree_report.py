
# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class job_degree_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        self.counter = 0
        super(job_degree_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines':self.lines,
            'jobs':self.get_jobs,
            'degrees':self.get_degrees,
            'counter':self.get_counter,
            'get_count_job':self.get_count_job,
            'get_count_job_degree':self.get_count_job_degree,
            'get_count_all':self.get_count_all,
            'get_count_degree':self.get_count_degree,
            'sum_name':unicode('المجموع', 'utf-8')
        })
    def get_count_degree(self, degree):
        degrees = filter(lambda x :x['degree_id'][0] ==  degree, self.emps_names)
        return len(degrees)
    def get_count_all(self):
        return len(self.emps_names)
    def get_count_job(self, job):
        jobs = filter(lambda x :x['job_id'][0] ==  job, self.emps_names)
        return len(jobs)
    def get_count_job_degree(self, job, degree):
        jobs = filter(lambda x :x['job_id'][0] ==  job and x['degree_id'][0] ==  degree, self.emps_names)
        return len(jobs)
    def get_counter(self):
        self.counter += 1
        return self.counter
    def get_jobs(self):
        return self.jobs_names
    def get_degrees(self):
        return self.degrees_names
    def lines(self,data):
        jobs_ids = data['form']['jobs']
        scales_ids = data['form']['scales']
        jobs_obj = self.pool.get('hr.job')
        scale_obj = self.pool.get('hr.salary.scale')
        if not jobs_ids:
            jobs_ids = jobs_obj.search(self.cr, self.uid, [])
        
        if not scales_ids:
            scales_ids = scale_obj.search(self.cr, self.uid, [])

        self.jobs_names = jobs_obj.read(self.cr, self.uid, jobs_ids, ['name'])
        degrees_obj = self.pool.get('hr.salary.degree')
        degrees_ids = degrees_obj.search(self.cr, self.uid, [('payroll_id','in',scales_ids)])
        self.degrees_names = degrees_obj.read(self.cr, self.uid, degrees_ids, ['name'])

        emps_obj = self.pool.get('hr.employee')
        emps_ids = emps_obj.search(self.cr, self.uid, [('job_id','in',jobs_ids), ('degree_id','in',degrees_ids), ])
        self.emps_names = emps_obj.read(self.cr, self.uid, emps_ids, ['degree_id','job_id'])

        return True
        


report_sxw.report_sxw('report.hr.job_degree.report','hr.employee','addons/hr_custom_military/report/job_degree_report.mako',parser=job_degree_report,header=False)
