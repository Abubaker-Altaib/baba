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


class training(osv.osv_memory):
    _name = "training.wizard"

    _columns = {
        'type': fields.many2one('hr.military.training.category', string="Type"),
        'place': fields.many2one('hr.military.training.place', string="Place"),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'employee_id': fields.many2one('hr.employee', string="Employee"),
        'state':fields.selection([('draft','Draft'), ('confirm', 'Confirm')] ,'Status'), 
        'course_type':fields.selection([('sureness','Sureness'), ('security', 'Security'),
                                        ('specialized','Specialized'), ('qualifying', 'Qualifying'),
                                        ('technician','Technician'), ('administrative', 'Administrative')] ,'Course Type'),
        'participation_type':fields.selection([('student','Student'), ('lecturer', 'Lecturer'),
                                        ('translator','Translator'), ('supervisor', 'Supervisor')],'Participation Type'),
        'reference':fields.selection([('file','File Certificate'), ('statement', 'Training Statement')],'Reference'),
        'training_eval': fields.selection([('excellent','Excellent'),('v_good','Very Good'),
                                            ('good','Good'),('middle','Middle'),
                                            ('u_middle','Under Middle'),('weak','Weak')], 'Training Eval'),
        'company_id': fields.many2one('res.company','company'),
        'location':fields.selection([('inside','Inside'), ('outside', 'Outside')] ,'Location'), 
        'who_not_take': fields.boolean('who not take'),
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
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.training.report', 'datas': data}
            
