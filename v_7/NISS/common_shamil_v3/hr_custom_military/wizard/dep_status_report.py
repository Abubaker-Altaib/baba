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


class dep_status_report(osv.osv_memory):
    _name = "dep_status_report.wizard"

    _columns = {
        'status_ids': fields.many2many('hr.dep.status', 'dep_status_wiz_dep_status_rel', string="Statuses"),
        'department_ids': fields.many2many('hr.department', 'dep_status_wiz_dep_rel', string="Departments"),
        'include_ch': fields.boolean('include inner departments'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'company_id': fields.many2one('res.company','company'),
        'who_not_go': fields.boolean('who not go'),
        'job_id': fields.many2one('hr.job','Job'),
        'degree_id': fields.many2one('hr.salary.degree','degree'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'company_id' : _default_company,
    }
    
    def print_report(self, cr, uid, ids, context={}):
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.dep_status.report', 'datas': data}
            
