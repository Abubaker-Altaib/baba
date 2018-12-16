# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import fields, osv
import time
import math
from openerp.tools.translate import _
#----------------------------------------
#loan paid
#----------------------------------------
class hr_loan_paid(osv.osv_memory):
    _name ='hr.employee.loan.paid'
    _description = "Employee's Out Of Salary Loan Payment"

    def _get_months(self, cr, uid, context):
        months = [(n, n) for n in range(1, 13)]
        return months

    _columns = {
        'employee_id' :fields.many2one("hr.employee",'Employee Name', required= True ),
	'loan_id': fields.many2one('hr.employee.loan', 'Loan Name',required=True ),
	'loan_amount' :fields.float("Loan Amount", digits=(18,2) , required= True),
        'month': fields.selection(_get_months,'Month'),
	'year' :fields.integer("Year", size=8, required= True),
	'comments':fields.char("Comments",size=20),
    	'installment_no' :fields.integer("installments number", size=8, readonly=True),
	'rais' :fields.integer("Rais", size=8, readonly=True ),
        'state':fields.selection([('draft','Draft') , ('paid','Paid')]),

         }
    _defaults={
	'employee_id': False,
        'state':'draft',
        'year': int(time.strftime('%Y')),
              }
    _sql_constraints = [
       ('amount_check', 'CHECK (loan_amount > 0)', "Loan amount should be greater than Zero!"),
		]

    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
	#employee_type domain
	emp_obj = self.pool.get('hr.employee')
	company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
	contractors = company_obj.loan_contractors
	employee = company_obj.loan_employee
	recruit = company_obj.loan_recruit
	trainee = company_obj.loan_trainee
	employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
	domain = {'employee_id':employee_domain['employee_id']}
	return {'domain': domain}

    def paid_loan(self,cr,uid, ids, context={}):
        """
	Paying loan for employee if the paid type is paid once.

        @return: Dictionary 
        """
        for p in self.browse( cr, uid,ids):
            employee_loan_obj = self.pool.get('hr.employee.loan')
            loan_archive_obj = self.pool.get('hr.loan.archive')
            emp_loan = employee_loan_obj.browse(cr,uid,p.loan_id.id,context=context)
            if p.loan_amount > emp_loan.remain_installment :
               raise osv.except_osv(_('Sorry'),_('your amount is greater then remain amount %s')%(emp_loan.remain_installment))
            else:
               paid_installment= loan_archive_obj.search(cr,uid,[('employee_id','=',p.employee_id.id),('loan_id','=',p.loan_id.id),
					('month','=',p.month),('year','=',p.year),('payment_type','!=','salary')])
               if not paid_installment:
                  paid_dict = {
                    'payroll_id': emp_loan.employee_id.payroll_id.id,
		    'employee_id': p.employee_id.id,
		    'loan_id': emp_loan.id,
		    'loan_amount': p.loan_amount,
		    'month' : p.month,
		    'year' : p.year,
		    'comments': p.comments,
		    'payment_type':'payment',
	      		  }
                  loan_archive_obj.create(cr, uid, paid_dict,context={})
               else:
                  raise osv.except_osv(_('Sorry'),_('your loan installment is already paid for selected month'))
            return {}

    def assign_emp_paid_loan(self, cr, uid, ids, context={}):
        """
	Paid loan for employee if the paid type is divide amount to monthly installments .

	@return: Dictionary 
        """
        for a in self.browse( cr, uid,ids):
            employee_loan_obj = self.pool.get('hr.employee.loan')
            loan_archive_obj = self.pool.get('hr.loan.archive')
    	    emp_loan = employee_loan_obj.browse(cr,uid,a.loan_id.id,context=context)
    	    installment_no=0
    	    if a.loan_amount > emp_loan.remain_installment :
               raise osv.except_osv(_('Sorry'),_('your amount is greater then remain amount %s')%(emp_loan.remain_installment))
            else :
               installment_no=0
               month = int(context['month'])
               year =  a.year
               net_installment_no= math.trunc(a.installment_no)
               if not a.installment_no < net_installment_no:
                  paid_installment= loan_archive_obj.search(cr,uid,[('employee_id','=',a.employee_id.id),('loan_id','=',emp_loan.id),('month','=',a.month),('year','=',a.year)])
                  if not paid_installment:
                     while installment_no <= net_installment_no:
                          paid_amount = a.loan_amount
                          net_installments_amount=emp_loan.installment_amount * net_installment_no
                          if installment_no == net_installment_no:
	                     amount = paid_amount - net_installments_amount
                             if amount:
                                installment_archive_id = loan_archive_obj.search(cr,uid,[('employee_id','=',a.employee_id.id),('loan_id','=',emp_loan.id),('month','=',month),('year','=',a.year)],context=context)
                                if installment_archive_id :
                                    installment_archive= loan_archive_obj.browse(cr,uid,installment_archive_id,context=context)[0]
                                    loan_archive_obj.write(cr,uid,installment_archive_id,{'loan_amount':installment_archive.loan_amount+amount},context=context) 
                          else:
                             amount = emp_loan.installment_amount            
                             loan_archive_dict = {
                                 'payroll_id': emp_loan.employee_id.payroll_id.id,
	                         'employee_id': a.employee_id.id,
                                 'loan_id': emp_loan.id,
                                 'payment_type':'payment',
	                         'loan_amount':amount,
	                         'month' :month,
	                         'year' :year,
	        		 'payment_type':'payment',
	                         'comments': a.comments,
	                              }
                             loan_archive_obj.create(cr, uid, loan_archive_dict,context={})
                             if month == 12:
                                month = 1
                                year = year+1
                             else:
                                month+=1
                          installment_no+=1 
            return {}
 
    def compute(self,cr,uid, ids, context):
        """
	Retrieve number of installment to be paid if the pay type is monthly installments 
        based on paid amount and loan installment amount, and retrive the residual amount.
        @return: True 
        """
        loan_archive_obj = self.pool.get('hr.loan.archive')
        this = self.browse(cr, uid, ids)[0]
        for c in self.browse( cr, uid,ids):
            paid_installment= loan_archive_obj.search(cr,uid,[('employee_id','=',c.employee_id.id),('loan_id','=',c.loan_id.id),('month','=',c.month),('year','=',c.year)])
            if not paid_installment:
               month= int(c.month)
               employee_loan_obj = self.pool.get('hr.employee.loan')
               emp_loan = employee_loan_obj.browse(cr, uid,c.loan_id.id,context=context)
               installment_no= c.loan_amount/emp_loan.installment_amount
               net_installment_no = math.trunc(installment_no)
               rais = c.loan_amount-(emp_loan.installment_amount * net_installment_no)
               self.write(cr,uid,[c.id],{'installment_no':net_installment_no,'rais':rais,'state':'paid'})
            else:
               raise osv.except_osv(_('Sorry'),_('your loan installment is already paid for selected month'))
            return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.loan.paid',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'context':{'month':c.month},
            'target': 'new',
             }
 
class hr_loan_suspend(osv.osv_memory):

    _name ='hr.employee.loan.suspend'
    _description = "Employee's Suspeneded loan"
    _columns = {
		'start_date' :fields.date("Start Date",required=True),
		'end_date' :fields.date("End Date",),
		'comments':fields.text("Comments",size=100),
	
         }
    def suspend_loan(self, cr, uid, ids, context=None):
        """
	Suspend loan for employee within specific period

        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of Ids 
        @param context: A standard dictionary 
        @return: Close the wizard. 
        """ 
        if not context:
            context = {}
        emp_loan_obj = self.pool.get('hr.employee.loan')
        emp_loan_id = context.get('active_id', False)
        loan = emp_loan_obj.browse(cr, uid, emp_loan_id, context=context)
        data = self.browse(cr, uid, ids[0], context=context)
        emp_loan_vals = {
            'suspend_date': data.start_date,
            'end_suspend_date': data.end_date,
            'comments': data.comments,
            'state':'suspend',
        }
        emp_loan_obj.write(cr, uid, [emp_loan_id], emp_loan_vals, context=context)
        return {'type': 'ir.actions.act_window_close'}

