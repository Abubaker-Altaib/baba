# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
#----------------------------------------
#holiday status(inherit)
#----------------------------------------
class  hr_holidays_status(osv.osv):
     """Inherits hr.holidays.status adds fields that handl financial issues during the holidays or define a holiday to spacefic degrees.
     """
     _inherit = "hr.holidays.status"
     _columns = {
        'payroll_type':fields.selection([('paied', 'Paied'), ('unpaied', 'Unpaied'), 
                                         ('customized', 'Customized')], 'Payroll', required=True),
        'degree_ids': fields.many2many('hr.salary.degree', 'leave_degree_rel', 'leave_id', 'degree_id','Degrees'),
        'leave_expenses':fields.selection([('with', 'With Expenses'),('without', 'Without Expenses')], 'Leave Expenses', required=True),
        'expense_allowance_id' :fields.many2one('hr.allowance.deduction', 'Allowance', domain="[('name_type','=','allow')]"),
        'pay_expenses':fields.selection([('payroll', 'With Payroll'), ('leave_validation', 'With Leave Validation') ], 'How to Pay Eexpenses'),
        'allow_deduct_ids' :fields.many2many('hr.allowance.deduction'  , 'hol_allow_deduct_rel'  , 'leave_id' , 'allow_deduct_id' , "Allowances/Desductions" , domain="[('in_salary_sheet','=',True),('special','=',False)]" ),
        'bonus_deduct_ids' :fields.many2many('hr.allowance.deduction' , 'hol_bonus_deduct_rel'  , 'leave_id' , 'bonus_deduct_id', "Bonuses and Desductions" , domain="[('in_salary_sheet','=',False),('special','=',False)]"),

    }
     _defaults = {
        'payroll_type': 'paied',
        'leave_expenses': 'without',
        }
class hr_holidays(osv.osv):

    _inherit = "hr.holidays"
    _columns = {
       

	'acc_number' :fields.many2one("account.voucher",'Voucher',readonly=True), 
    }

    def holidays_validate(self, cr, uid, ids, context=None):
        super(hr_holidays, self).holidays_validate(cr, uid, ids, context=context)
        emp_special_obj = self.pool.get('hr.allowance.deduction.exception')
        payroll_obj = self.pool.get('payroll')
        for rec in self.browse( cr, uid,ids):
            if rec.holiday_status_id.leave_expenses == 'with':
                allow_deduct_id = rec.holiday_status_id.expense_allowance_id
                dt = datetime.strptime(rec.date_from, '%Y-%m-%d %H:%M:%S').date()
                allow_dict=payroll_obj.allowances_deductions_calculation(cr,uid,str(dt),rec.employee_id,{'no_sp_rec':True}, [allow_deduct_id.id], False,[])
                if rec.holiday_status_id.pay_expenses == 'leave_validation':
                    reference = 'HR/Allowances/Holiday_Expenses/ '+rec.employee_id.name+" / "+str(rec.date_from)
                    line={
			          'allow_deduct_id':allow_deduct_id.id,
			          'amount':allow_dict['total_allow'] * rec.number_of_days_temp }
                    voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,'lines':[line]},context=context)
                    self.write(cr, uid, [rec.id], {'acc_number':voucher}, context=context)
                else:
                    emp_special_obj.create(cr, uid, {
			            'code' : rec.employee_id.emp_code,
		                'employee_id': rec.employee_id.id,
		                'allow_deduct_id': allow_deduct_id.id,
		                'start_date' : rec.date_from,
		                'end_date' : dt + relativedelta(months=1),
		                'amount':allow_dict['total_allow'] * rec.number_of_days_temp,
                        'types':allow_deduct_id.name_type,
                        'action':'special',
		            },context=context)
        return True

