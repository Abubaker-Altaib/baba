# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################import datetime
from openerp import addons
import logging
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import tools
import mx
from datetime import datetime
from dateutil.relativedelta import relativedelta

class  hr_holidays_status(osv.osv):
     _inherit = "hr.holidays.status"

     """
     Inherit hr.holidays.status and add new fields to the configuration
     of the holiday in order to be used in the buying or end of service process. 
     """
     _columns = {
     
         'buy_leave': fields.boolean('Allow Buy Leave'),
         'pay_buying':fields.selection([('with_payroll', 'With Payroll'), ('with_validation', 'With Leave Validation')], 'How to Pay Buying Amount'),
         'buy_allowance_id' :fields.many2one('hr.allowance.deduction', 'Allowance', domain="[('name_type','=','allow'),('special', '=', True)]"),
         'end_service_allowance_id' :fields.many2one('hr.allowance.deduction', 'End of Service Allowance', domain="[('name_type','=','allow'),('allowance_type', '=', 'serv_terminate'),('special', '=', True)]"),
         'pay_end_service':fields.selection([('with_payroll', 'With Payroll'), ('with_validation', 'With Leave Validation')], 'How to Pay End of Service Holiday Allowance'),
         'buying_comments':fields.text("Comments"),
         'continous_buy_leave' :fields.float("Max Continous Years To Buy", digits=(18, 2)), 

                }
     _defaults = {
            'buy_leave': False,
              }

     _sql_constraints = [
       ('continous_buy_leave_check', 'CHECK (continous_buy_leave >= 0)', "The continous buy leave years should be greater than or equal to Zero!"),
        ]



#----------------------------------------
#holiday(inherit)
#----------------------------------------
class  hr_holidays(osv.osv):
     _inherit = "hr.holidays"
     """inherit hr.holiday and add new fields associated to the buying  pocess
     """

     def _compute(self, cr, uid, ids, arg, fields, context=None):
        """
        Mehtod returns the state as percentage to be used in the progress bar.

        @return: Dictionary of values 
        """
        res = {}
        progress = 0.0
        if not ids:
            return res
        super(hr_holidays, self)._compute(cr, uid, ids,arg, fields, context=context)
        for hol in self.browse(cr, uid, ids):
            if hol.state == 'paid':
                progress = 100.0
            if hol.state == 'confirm_buying':
                progress = 25.0
            if hol.state in ('holiday_buying', 'holiday_end_service'):
                progress = 75.0
            res[hol.id] = progress
        return res

     _columns = {
        'state': fields.selection([('draft', 'To Submit'),  ('cancel', 'Cancelled'), ('confirm', 'To Approve'), ('refuse', 'Refused'),
                                   ('validate1', 'Second Approval'), ('validate', 'Approved'), ('cut', 'Cut Leave'), 
                                   ('approve_cut', 'Approve Cut'), ('done_cut', 'Done Cut'),('postpone', 'Postpone'),
                                   ('confirm_buying', 'To Approve'),('holiday_buying','Leave Buying'),
('holiday_end_service','End of Service Allowance'), ('paid','Paid')],
                                   'State', readonly=True),
        'progress': fields.function(_compute, type='float', method=True, string='Progress'),
        'acc_number': fields.many2one('account.voucher','Voucher Number',readonly=True), 
        'amount': fields.float('Amount',  readonly=True , size=64),
        'buying_day': fields.integer('Buying Days', readonly=True,size=64),   
        
                }

     def buying_holiday(self, cr, uid, ids, context=None):
         self.calculate_holiday_amount(cr,uid,ids,'buying',context=context)
         return True
    
     def end_service_holiday(self, cr, uid, ids, context=None):
         self.calculate_holiday_amount(cr,uid,ids,'end_service',context=context)
         return True


     def calculate_holiday_amount(self, cr, uid, ids,holiday_type, context=None):
        """
        Workflow method that changes the state to 'holiday_buying' and it
        checks if the holiday meets continuous years to buy condition if its exists  
        if it does then it calculates the amount of the days to buy. 
        @return : Boolean True
        """
        for holiday in self.browse(cr,uid,ids,context=context):
           passed=False
           if holiday_type== 'buying':
              continuity = holiday.holiday_status_id.continous_buy_leave
              if continuity:
                 year = mx.DateTime.Parser.DateTimeFromString(holiday.date_from).year
                 cr.execute('''SELECT DISTINCT
  to_char(hr_holidays.date_from,'YYYY')  as year 
FROM 
  public.hr_holidays
WHERE
  employee_id=%s AND holiday_status_id=%s  AND to_char(date_from,'YYYY')!=%s AND state='paid'
ORDER BY  year DESC 
LIMIT %s
 ''',(holiday.employee_id.id,holiday.holiday_status_id.id,str(year),continuity))
                 res=cr.dictfetchall()
                 result= [int(y['year'])  for y in res if res]
                 if not result:
                     passed=True
                 else:
                     if not result[0]-year in [1,-1]:
                         passed=True
                     else:
                           result.append(int(year))
                           result.sort()
                           passed=not(float((result[-1]-result[0] + 1)/len(result))==1 and len(result)>continuity) and True or False
              else:
                 passed = True
              if not passed :
                 raise osv.except_osv(_('Warrning'),_("Sorry You can not buy this holiday you have exceeded the number of continuous years allowed to buy the holiday!"))
           payroll_obj = self.pool.get('payroll')
           date = mx.DateTime.Parser.DateTimeFromString(holiday.date_from)
           date = str(date.year)+'-'+str(date.month)+'-'+str(date.day)
           if holiday_type == 'buying':
              allowance_id = [holiday.holiday_status_id.buy_allowance_id.id]
           else:
              if not holiday.holiday_status_id.end_service_allowance_id:
                 raise osv.except_osv(_('Warrning'),_("Please Enter end of the service allowance first"))
              allowance_id = [holiday.holiday_status_id.end_service_allowance_id.id]
           allow_dict=payroll_obj.allowances_deductions_calculation(cr,uid,date,holiday.employee_id,{'no_sp_rec':True},allowance_id, False,[])
           if holiday_type == 'buying':
              res = {'state':'holiday_buying',}
           else:
	      res = {'state':'holiday_end_service',}
           res.update({'amount':allow_dict['total_allow'] * holiday.number_of_days_temp ,})
           return self.write(cr, uid, ids,res, context=context)

     def paid(self, cr, uid, ids, context=None):
         """
         Workflow function that check the buying amount if not transferred then transferred
         to the voucher and changes the state to 'paid'.
         
         @return : Boolean True
         """
	 emp_special_obj = self.pool.get('hr.allowance.deduction.exception')
         vals = {'state':'paid'}
         for rec in self.browse( cr, uid,ids):
            if rec.state == 'holiday_buying':
               holiday_type = 'buying'
               allowance_id = rec.holiday_status_id.buy_allowance_id
               allowance_type = rec.holiday_status_id.buy_allowance_id
               pay_type = rec.holiday_status_id.pay_buying
            else:
               holiday_type = 'end_service'
               allowance_id = rec.holiday_status_id.end_service_allowance_id
               allowance_type = rec.holiday_status_id.end_service_allowance_id
               pay_type = rec.holiday_status_id.pay_end_service
            if (holiday_type == 'buying' and not allowance_id) or (holiday_type == 'end_service' and not allowance_id):
               raise orm.except_orm(_('Sorry'), _('No allwances assigned to the holiday'))
            if pay_type == 'with_validation':
               reference = 'HR/Allowances/Holiday '+ holiday_type+ ' / ' +rec.employee_id.name+" / "+str(rec.date_from)


               lines = self.pool.get('hr.employee').get_emp_analytic(cr, uid, {rec.employee_id:rec.amount}, \
							 {'allow_deduct_id':rec.holiday_status_id.buy_allowance_id.id})
	       voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,'lines':lines, 
                                                                             'narration':reference,
								'department_id':rec.employee_id.department_id.id,},context=context)


               vals.update({'acc_number':voucher})
            else:
               dt = datetime.strptime(rec.date_from, '%Y-%m-%d %H:%M:%S').date()
               emp_special_obj.create(cr, uid, {
			 'code' : rec.employee_id.emp_code,
		         'employee_id': rec.employee_id.id,
		         'allow_deduct_id': allowance_id.id,
		         'start_date' : rec.date_from,
		         'end_date' : dt + relativedelta(months=1),
		         'amount':rec.amount,
                         'types':allowance_type.name_type,
                         'action':'special',
		},context=context)
               
         return self.write(cr, uid, ids, vals, context=context) 





