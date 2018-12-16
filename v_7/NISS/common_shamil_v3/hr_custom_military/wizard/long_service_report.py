# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from datetime import datetime
from tools.translate import _


class long_service_report_wizard(osv.osv_memory):
    _name = "long_service_report.wizard"

    _columns = {
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'employee_id': fields.many2one('hr.employee', string="Employee"),

        'company_id': fields.many2one('res.company', 'company'),
        'department_id': fields.many2one('hr.department', 'Department'),

        'job_id': fields.many2one('hr.job', 'Job'),

        'payroll_id': fields.many2one('hr.salary.scale', 'Scale'),
        'degree_id': fields.many2one('hr.salary.degree', 'degree' ,domain="[('payroll_id', '=', payroll_id)]"),


        'gift_id': fields.many2one('hr.gift', 'gift'),

        'candidate': fields.boolean('Cantidates'),


    }

    def _default_company(self, cr, uid, context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id': _default_company,
    }

    def print_report(self, cr, uid, ids, context={}):
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.long_service.report', 'datas': data}
