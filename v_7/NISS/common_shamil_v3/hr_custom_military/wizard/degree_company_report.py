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


class degree_company(osv.osv_memory):
    _name = "degree_company.wizard"

    _columns = {
        'company_id': fields.many2one('res.company', string="Company"),
        'degrees_ids': fields.many2many('hr.salary.degree', string="Degrees"),
        'job_id': fields.many2one('hr.job', string="Job"),
        'department_id': fields.many2one('hr.department', string="Department"),
        'included_department': fields.boolean('Includes sub-departments'),
        'gender': fields.selection([('male','Male'),('female','Female')], string='Gender'),
    }

    def print_report(self, cr, uid, ids, context={}):
    	rec = self.browse(cr, uid, ids)[0]
    	if not rec.department_id and not rec.degrees_ids:
    		raise osv.except_osv(_(''),_("you sould select degree or department")) 
        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.degree_company.report', 'datas': data}
            
