# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv


class employee_promotion_wizard_report(osv.osv_memory):
    _name = "employee.promotion.wizard.report"

    _columns = {
        'type' : fields.selection([('promotion' , 'promotion') , ('isolate' , 'isolate'), ('bonus' , 'bonus'), ('department' , 'department'), ('job' , 'job')],string="type"),
        'payroll_id' : fields.many2one('hr.salary.scale' , string="Scale") ,
        'degree_id' : fields.many2one('hr.salary.degree' , string="Degree") ,
        'department_id' : fields.many2one('hr.department' , string="Department") ,
        'job_id' : fields.many2one('hr.job' , string="Job") ,
        'bonus_id' : fields.many2one('hr.salary.bonuses' , string="Bonus") ,
        'start_date' : fields.date('Start Date') ,
        'end_date' : fields.date('End Date') ,
        'employee_ids' : fields.many2many('hr.employee' , 'emp_prom_wiz_rel' , 'prom_wiz_id' , 'emp_id') ,
    }

    def print_report(self, cr, uid, ids, context={}):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr_employee_promotion_report',
        }