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

def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d')
class promotion_group_by_job(osv.osv_memory):
    _name = "promotion_group_by_job_wizard"

    _columns = {
        'year': fields.char("Year"),
        'start_date': fields.date("Start Date"),
        'end_date': fields.date("End Date"),
        'jobs_ids': fields.many2many('hr.job', 'promotion_group_by_job_job_rel', 'promotion_group_by_job_id', 'job_id', string="Jobs"),
        'degree_id': fields.many2one('hr.salary.degree', string="Degree"),
    }

    def print_report(self, cr, uid, ids, context={}):
        data = {'form': self.read(cr, uid, ids, [])[0]}
        data['form']['start_date'] = data['form']['year'] +"-01-01"
        data['form']['end_date'] = data['form']['year'] +"-12-31"
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'promotion_group_by_job.report', 'datas': data}
