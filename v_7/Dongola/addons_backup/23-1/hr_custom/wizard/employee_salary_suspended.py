# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields,osv
import pooler
import time
from tools.translate import _

suspend_type = [
    ('suspend', 'Suspend'),
    ('resume', 'Resume'),
]


#----------------------------------------
#employee suspend
#----------------------------------------
class emp_suspend(osv.osv_memory):
    _name ='emp.suspend'

    _columns = {
	
        'employee_id': fields.many2one('hr.employee','Employees',required=True),
        'suspend_date' :fields.date("Suspend Date", required= True),
	'comments':fields.char("Comments"),
        'suspend_type':fields.selection(suspend_type,"Suspend/Resume"),
        'company_id': fields.many2one('res.company','Company',readonly=True),
       }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'emp.suspend', context=c),
		}


    def emp_suspend(self, cr, uid,ids, context=None):
        """suspend and resume empployee salary.
        @return: dectionary 
        """
        for t in self.browse( cr, uid,ids):
           emp_obj = self.pool.get('hr.employee')
           susp_arch_obj = self.pool.get('hr.basic.salary.suspend.archive')
           employee = emp_obj.read(cr, uid, t.employee_id.id, ['salary_suspend'], context=context)
           if t.suspend_type == 'suspend':
              if employee['salary_suspend']:
                 raise osv.except_osv(_('Sorry'), _('This Employee is Already Suspend'))
              sal_susp = True
           else:
              if not employee['salary_suspend']:
                 raise osv.except_osv(_('Sorry'), _('This Employee is Already Resumed'))
              sal_susp = False
           susp_arch_vals = {
                 'employee_id': t.employee_id.id,
                 'suspend_date': t.suspend_date,
                 'comments': t.comments ,
                 'suspend_type': t.suspend_type ,
                        }
           susp_arch_obj.create(cr, uid, susp_arch_vals, context=context)
           emp_obj.write(cr, uid, [t.employee_id.id], {'salary_suspend':sal_susp}, context=context)
           return {}  


emp_suspend()

