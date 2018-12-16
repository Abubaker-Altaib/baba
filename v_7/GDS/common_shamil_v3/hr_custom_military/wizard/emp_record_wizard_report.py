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


class emp_record_wizard_report(osv.osv_memory):
    _name = "emp_record_wizard.report"

    _columns = {
        'scale_ids': fields.many2many('hr.salary.scale', 'emp_record_wizard_salary_scale_rel', string="Salary Scales"),
        'department_id': fields.many2one('hr.department', string="Department"),
    	'employee_ids': fields.many2many('hr.employee' , 'emp_record_wizard_employee_rel' , string="Employees")
    }

    def print_report(self, cr, uid, ids, context={}):
    	return {
            'type': 'ir.actions.report.xml',
            'report_name': 'emp_record_report',
        }