# -*- coding: utf-8 -*-
##############################################################################
#
#	NCTR, Nile Center for Technology Research
#	Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_payrecomput_employees(osv.osv_memory):

    _name ='hr.payrecompute.employees'
    _description = 'Recompute Payroll for all selected employees'
    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'hr_employee_recompute_rel', 'payroll_id', 'employee_id', 'Employees'),
    }
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None: context = {}
        fvg = super(hr_payrecomput_employees, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        record_id = context and context.get('active_id', False) or False
        if view_type == 'form' and (context.get('active_model') == 'hr.employee.salary.addendum') and record_id:
            preq_obj = self.pool.get('hr.employee.salary.addendum').browse(cr, uid, record_id, context=context)
            if  preq_obj.arch_ids:
                fvg['fields']['employee_ids']['domain']=[('id','in',[r.employee_id.id for r in preq_obj.arch_ids])] 
        return fvg
    
    def recompute(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        if context and context.get('active_id', False):
            
            if not data['employee_ids']:
                raise osv.except_osv(_("Warning!"), _("You must select employee(s) to Recompute Payroll."))
            context.update({'employee_ids':data['employee_ids'],'recompute':True})
            active_id =context['active_id']
            self.pool.get('hr.employee.salary.addendum').rollback(cr, uid,  [active_id], context = context)
            self.pool.get('hr.employee.salary.addendum').compute(cr, uid,  [active_id], context = context)
        return {'type': 'ir.actions.act_window_close'}

hr_payrecomput_employees()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
