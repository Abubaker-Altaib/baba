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


class absence_report_wizard(osv.osv_memory):
    _name = "absence_report.wizard"

    _columns = {
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'employee_id': fields.many2one('hr.employee', string="Employee"),
        
        'company_id': fields.many2one('res.company','company'),
        'department_id': fields.many2one('hr.department','Department'),

        'job_id': fields.many2one('hr.job','Job'),
        'degree_id': fields.many2one('hr.salary.degree','degree'),

        'in_absence': fields.boolean('IN Absence'),
        'first_week': fields.boolean('Frist Week'),
        'second_week': fields.boolean('Second Week'),
        'third_week': fields.boolean('Third Week'),
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
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.absence.report', 'datas': data}
            
