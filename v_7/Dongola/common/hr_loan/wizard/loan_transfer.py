# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
import time
import netsvc

#----------------------------------------
#loan transfer to account
#----------------------------------------
class loan_transfer(osv.osv_memory):
    _name= "loan.transfer"


    _columns = {   
            'loan_id':fields.many2one( 'hr.loan', 'Loan Name', required=True),
            'start_date':fields.date('Start Date', required=True),
            'employee_id': fields.many2many('hr.employee', 'hr_loan_employee_rel','loan_transfer','employee_id','Loan Transfer',domain="[('state','!=','refuse')]"),
           }


    def loan_transfer_amount(self, cr, uid, ids, context={}):
       """Transfer specific loan amounts to voucher.
       @return: Dictionary 
       """
       f=self.browse(cr,uid,ids)

       for loans in self.browse(cr,uid,ids):
         employee_loan_obj = self.pool.get('hr.employee.loan')
         loan_obj = self.pool.get('hr.loan')
         account_period_obj = self.pool.get('account.period')
         voucher_obj = self.pool.get('account.voucher')
         voucher_line_obj = self.pool.get('account.voucher.line')
         
         emp_loan_ids = employee_loan_obj.search(cr,uid,[('loan_id','=',loans.loan_id.id),('state','=','approved')],context=context)
         print emp_loan_ids,"emp_loan_ids"
         if emp_loan_ids :
            total_loan_amount=0.0
            for emp_loan in employee_loan_obj.browse(cr,uid,emp_loan_ids,context=context):
               total_loan_amount+= emp_loan.loan_amount
         else:
            raise osv.except_osv('ERROR', 'Sorry This loan Not Approved')
         loan = loan_obj.browse(cr,uid,loans.loan_id.id,context=context)
         lines=[]
         reference='HR/Loans/'
         if loan.loan_journal_id and loan.loan_journal_id:
           date = time.strftime('%Y-%m-%d')
           period=account_period_obj.find(cr, uid, dt=date ,context={'company_ids':loan.loan_journal_id.company_id.id})
           loan_dict={
		'account_id': loan.loan_journal_id.id,
		'amount': total_loan_amount,
              		}
     
           lines.append(loan_dict)
           voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,'lines':lines,'partner_id':partner_id},context=context)
	   employee_loan_obj.write(cr,uid,[loan.id],{'acc_number': voucher,'state':'transfered'})

           #vouch = voucher_obj.browse(cr,uid,voucher)			
           #employee_loan_obj.write(cr,uid,emp_loan_ids,{'acc_number': vouch.number,'state':'transfered'})

         else:
            raise osv.except_osv('ERROR', 'Please enter account_loan for loan')

       return {}




