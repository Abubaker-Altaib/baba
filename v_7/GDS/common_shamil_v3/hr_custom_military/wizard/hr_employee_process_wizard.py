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


class hr_employee_process_wizard(osv.osv_memory):
    _name = "hr.employee.process.wizard"

    _columns = {
        'type': fields.selection([('promotion' , 'Promotion') ,('isolate' , 'Isolate') ,('department' , 'Department Movements') ,('bonus' , 'Yearly Bonus') ,('job' , 'Job Movements') ]),
        'approve_date' : fields.date('Approve Date') , 
        'department_movement_ids': fields.many2many('hr.movements.department', 'move_departments_wizard', string="Department Movements"),
        'job_movement_ids': fields.many2many('hr.movements.job', 'move_job_wizard', string="Job Movements"),
        'promotion_ids': fields.many2many('hr.movements.degree', 'move_degree_wizard', string="Promotion"),
        'isolate_ids': fields.many2many('hr.movements.degree', 'move_isolate_wizard', string="Isolation"),
        'yearly_bonus_ids': fields.many2many('hr.movements.bonus', 'move_bonus_wizard', string="Yearly Bonus"),

    }

    def do_approve(self, cr, uid, ids, context={}):
        for rec in self.browse(cr , uid , ids):
            approve_date = rec.approve_date
            if rec.type == 'department' :
                for process in rec.department_movement_ids :
                    process.do_approve_with_date(rec.approve_date)
            elif rec.type == 'job' :
                for process in rec.job_movement_ids :
                    process.do_approve_with_date(rec.approve_date)
            elif rec.type == 'promotion' :
                for process in rec.promotion_ids :
                    process.do_approve_with_date(rec.approve_date)
            elif rec.type == 'isolate' :
                for process in rec.isolate_ids :
                    process.do_approve_with_date(rec.approve_date)
            elif rec.type == 'bonus' :
                for process in rec.yearly_bonus_ids :
                    process.do_approve_with_date(rec.approve_date)
            return True
