# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
import re
#----------------------------------------
#hr_department_payroll(inherit) 
#----------------------------------------
class hr_department_payroll(osv.Model):

    _name = "hr.department.payroll"

    _columns = {
        'name': fields.char('Department Of Payroll',size=256, required=True ),
 	'department_payroll_ids':fields.one2many('hr.employee', 'payroll_employee_id', 'Employees', readonly=True, domain=[('state', '=', 'approved')]),
 	#'department_payroll_ids':fields.many2many('hr.employee', 'payroll_employee_id_rel' ,'payroll_employee_id' , 'employee' ), 
        'state_id':fields.selection([('khartoum', 'khartoum'), ('states', 'States')], "States or Khartoum", required=True),
    }
    

   


#----------------------------------------
# Employee (Inherit) 
# Adding new fields 
#----------------------------------------
class hr_employee(osv.Model):

    _inherit = "hr.employee"

    _order = "sequence"

    def onchange_state(self, cr, uid, ids=[], payroll_state=True, context=None):
        """
        """
        vals = {}
        if payroll_state:
            vals = {'payroll_employee_id': False}
        return {'value': vals}

    _columns = {

        'payroll_employee_id':fields.many2one('hr.department.payroll', 'Department of Payroll',ondelete="restrict" ),
        'payroll_state':fields.selection([('khartoum', 'khartoum'), ('states', 'States')], "States or Khartoum", required=False),
      
    }

    _defaults = {
       
    }

   

    _constraints = [
        
    ]
    _sql_constraints = [
       
    ]

#----------------------------------------
#----------------------------------------
#salary suspend archive
#----------------------------------------

suspend_type = [
           ('suspend', 'Suspend'),
           ('resume', 'Resume'),
	    ]
class salary_suspend_archive(osv.osv):
    _name = "hr2.basic.salary.suspend.archive"
    _columns = {
		 'employee_id':fields.many2one('hr.employee', "Employee", required=True),
		 'suspend_date' :fields.date("Suspend/Resume Date", size=8 , required=True),
		 'comments': fields.text("Comments"),
		 'suspend_type':fields.selection(suspend_type, "Suspend Type" , readonly=True),
		 'company_id': fields.many2one('res.company','company'),
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
    
salary_suspend_archive()



#----------------------------------------
#employee family relation (Inherit)
#----------------------------------------
class employee_family(osv.Model):

    _inherit = "hr.employee.family"
    _columns = {
'employee_id': fields.many2one('hr.employee', "Employee", required=True, domain=[('state', '=', 'approved')]) ,
             }

class hr_payroll_main_archive(osv.Model):

    _inherit = "hr.payroll.main.archive"
    _columns = {
        'payroll_employee_id':fields.many2one('hr.department.payroll', 'Department of Payroll'),
        'payroll_state':fields.selection([('khartoum', 'khartoum'), ('states', 'States')], "States or Khartoum"),
    }


class hr_basic_houes(osv.osv):
    _name = "hr.basic.houes"
    _columns = {
           'employee_id':fields.many2one('hr.employee', "Employee", required=True),
           'houes_date' :fields.date("Date", size=8 , required=True),
           'Comments': fields.text("Comments"),
	   'houses_type' :fields.selection([('1', 'Government'), ('3', 'Rent')], 'House Type'),
           'department_id': fields.related('employee_id', 'department_id', string="Department", type="many2one", relation="hr.department",readonly=True),
           'company_id': fields.related('employee_id', 'company_id', string="company name", type="many2one", relation="res.company",readonly=True),
            'state':fields.selection([('draft','Draft'), ('confirm', 'Confirm')] ,'Status'),  
           'house_type': fields.related('employee_id', 'house_type', string="Last House",  type="char", store=True),
    }

    _defaults = {
        'state' : 'draft',
       
    }
    def set_to_draft(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        emp_obj = self.pool.get('hr.employee')
        for hous in self.browse(cr, uid, ids, context=context):
               emp_id=hous.employee_id.id
               houses=hous.house_type
               print">>>>>>>>>>>>>>>>>>>>>>>>>>>",emp_id,houses
               emp_obj.write(cr, uid,[emp_id], {'house_type' : houses}, context=context)
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def confirm(self,cr,uid,ids,context=None):
        """
        Mehtod that sets the state to confirm.

        @return: Boolean True
        """
        emp_obj = self.pool.get('hr.employee')
        for hous in self.browse(cr, uid, ids, context=context):
               emp_id=hous.employee_id.id
               houses=hous.houses_type
               print">>>>>>>>>>>>>>>>>>>>>>>>>>>",emp_id,houses
               emp_obj.write(cr, uid,[emp_id], {'house_type' : houses}, context=context)
        self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
  
        return True

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context):
            if rec.state != 'draft':
                raise osv.except_osv(_('ValidateError'), _("this record is must be in draft state"))
        super(hr_basic_houes, self).unlink(cr, uid, ids, context=context)


