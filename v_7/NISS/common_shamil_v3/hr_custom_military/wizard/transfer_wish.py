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


class transfer_wish(osv.osv_memory):
    _name = "transfer_wish.wizard"

    _columns = {
        'employee_id': fields.many2one('hr.employee', "Employee", domain="[('state','!=','approved')]"),
        'reason_id': fields.many2one('hr.transfer.reason', string='Reason'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'medical_date': fields.date("Medical Date"),
        'state':fields.selection([('draft','Draft'), ('confirm', 'Confirm')] ,'Status'),  
        'department_id': fields.many2one('hr.department', string="Department"),
        'with_childs': fields.boolean(string="with childs"),
        'company_id': fields.many2one('res.company', 'company'),
        'job_id': fields.many2one('hr.job', 'Job'),
        'degree_id': fields.many2one('hr.salary.degree', 'degree'),
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
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.transfer_wish.report', 'datas': data}
