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


class service_state(osv.osv_memory):
    _name = "service_state_wizard"

    _columns = {
        'type': fields.selection([('specific', 'Specified'), ('takeout', 'Takeout')], string="Type"),
        'department_id': fields.many2one('hr.department', string="Department"),
        'with_childs': fields.boolean(string="with childs"),
        'job_id': fields.many2one('hr.job', 'Job'),
        'degree_id': fields.many2one('hr.salary.degree', 'degree'),
        'company_id': fields.many2one('res.company', 'company'),
        'service_state_id': fields.many2one('hr.service.state', 'Service State'),
    }

    def print_report(self, cr, uid, ids, context={}):
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.service_state.report', 'datas': data}
            
