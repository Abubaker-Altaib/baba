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


class escape_status_report(osv.osv_memory):
    _name = "escape_status_report.wizard"

    _columns = {
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'service_end': fields.boolean('Service Ended'),
        'courted': fields.boolean('Courted'),
        'company_id': fields.many2one('res.company','company'),
        'job_id': fields.many2one('hr.job','Job'),
        'degree_id': fields.many2one('hr.salary.degree','degree'),
        'department_id': fields.many2one('hr.department',string='Department'),
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
    	rec = self.browse(cr, uid, ids)[0]
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.escape_status.report', 'datas': data}
            
