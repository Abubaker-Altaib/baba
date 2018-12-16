# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from tools.translate import _


class job_degree_wizard_report(osv.osv_memory):
    _name = "job_degree_wizard.report"

    _columns = {
        'jobs': fields.many2many('hr.job', 'job_degree_wizard_job_rel', string="Jobs"),
        'scales': fields.many2many('hr.salary.scale', 'job_degree_wizard_salary_scale_rel', string="Salary Scales"),
        'departments': fields.many2many('hr.department', 'job_degree_wizard_department_rel', string="Departments"),
        'type': fields.selection([('job_degree', 'Job and Degree'), ('depart_job', 'Department and Job'), ('depart_degree', 'Department and Degree')], string="Type")
    }

    def print_report(self, cr, uid, ids, context={}):

        data = {'form': self.read(cr, uid, ids, [])[0]}
        if data['form']['type'] == 'job_degree':
            return {'type': 'ir.actions.report.xml', 'report_name': 'hr.job_degree.report', 'datas': data}

        if data['form']['type'] == 'depart_job':
            return {'type': 'ir.actions.report.xml', 'report_name': 'hr.depart_job.report', 'datas': data}

        if data['form']['type'] == 'depart_degree':
            return {'type': 'ir.actions.report.xml', 'report_name': 'hr.depart_degree.report', 'datas': data}