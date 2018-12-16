# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from openerp.osv import osv, fields, orm


class depend_on_department(osv.osv_memory):
    _name = "trainee.depend.on.department"

    _columns = {
        'company_id' : fields.many2one('res.company', 'Company', required=True),
		'department_id': fields.many2many('hr.department', 'training_department_rel', 'department_id', 'training_id', 'Department Name', required=True),
        #'plan_id' : fields.many2one('hr.training.plan', 'Plan', required=True),
        
   		 }
    _defaults = {

        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'trainee.depend.on.department', context=c), 
		}    
    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.employee.training',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'department.course',
            'datas': datas,
            }
depend_on_department()
