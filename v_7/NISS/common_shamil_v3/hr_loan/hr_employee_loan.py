# -*- coding: utf-8 -*-
##############################################################################
#
#	NCTR, Nile Center for Technology Research
#	Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
import itertools
from collections import defaultdict
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
#from copy_attachments import copy_attachments as copy_attachments
import netsvc
import openerp.addons.decimal_precision as dp

#----------------------------------------
# Employee loan
#----------------------------------------
class hr_employee_loan(osv.Model):
	_name = "hr.employee.loan"
        _description = "Employee Loan"
        _inherit = 'ir.needaction_mixin'

	def create_remission(self, cr, uid, loan,ids, context=None):
		"""
		Workflow function that transfers remission loan amount to voucher.

		@return: ID of the created voucher
		"""
		voucher_obj = self.pool.get('account.voucher')
		loan_archive_obj= self.pool.get('hr.loan.archive')

		msg = False 
		if not  loan.loan_id.loan_account_id:
		   msg ='loan account' 
		if not  loan.loan_id.loan_remission_account_id:
		   msg = msg  and  'loan account and remission account' or ' remission account'
		if msg:
     		    raise osv.except_osv('ERROR', 'Please configure %s for loan'% (msg,))

                paid_dict = {
		    'payroll_id': loan.employee_id.payroll_id.id,
		    'employee_id': loan.employee_id.id,
		    'loan_id': loan.id,
		    'loan_amount': loan.remission_amount,
		    'month' :  int(time.strftime('%m')),
		    'year' :  int(time.strftime('%Y')),
		    'comments': 'Pay remission',
		    'payment_type':'remission',
      		  }
                archive_id = loan_archive_obj.create(cr, uid, paid_dict,context={})
		date = time.strftime('%Y-%m-%d')
                lines=[]
		reference = "HR/Loan Remission/"+str(date)
		partner_id=loan.employee_id.user_id.partner_id.id or False
                lines = [{
                         'account_id':loan.loan_id.loan_remission_account_id.id,#loan.loan_id.loan_account_id.id,
			 'amount':loan.remission_amount,
                         'narration':loan.loan_id.name,
                         'name':loan.loan_id.name,
			}]
		voucher_id = self.pool.get('payroll').create_payment(cr, uid, ids,\
							{'reference':reference,
							'lines':lines,
							'partner_id':partner_id,
							'account_id':loan.loan_id.loan_account_id.id},context=context)
	        self.write(cr,uid,[loan.id],{'state':'transfered','acc_remission_no':voucher_id})
		return voucher_id 


	def _get_remission(self, cr, uid, ids, field_name, arg, context=None):
	    res = {}
	    for loan in self.browse(cr, uid, ids, context=context):

	        if loan.loan_id.remission_type == 'amount':
		    res[loan.id] = loan.loan_id.remission  
		elif loan.loan_id.remission_type == 'percentage':
                    res[loan.id] = loan.loan_id.remission*loan.loan_amount/100
		else: 
		    res[loan.id] = 0
	    return res

	def computee(self, cr, uid, ids, name, args,context=None):
                """
		Method for functional fields that computes the paid and the remain 
		amount of employee's loan.

		@param name: name of field to be updated
		@param args: other arguments
                @return: Dictionary of values 
                """
		result ={}

		if not context:
			context = {}
		loan_archive_obj= self.pool.get('hr.loan.archive')
		wf_service = netsvc.LocalService("workflow")
		for loan in self.browse(cr, uid, ids, context=context):
		        #print '**** start loan *** '
    			time1 = time.time()   
			advance_amount = 0
			'''cr.execute("""select COALESCE(SUM(loan_amount),0.0) from hr_loan_archive l 
				          where employee_id=%s and loan_id=%s """,(loan.employee_id.id, loan.id))
			res = cr.fetchone()
			advance_amount = res and res[0] or 0'''
			if  'amount' in context:
			     advance_amount = loan.advance_amount + context['amount']
			else:
			    loan_ids=loan_archive_obj.search(cr, uid,\
				[('employee_id','=',loan.employee_id.id),('loan_id','=',loan.id)])
			    loan_obj=loan_archive_obj.browse(cr,uid,loan_ids)
			    for l in loan_obj:
			        advance_amount+=l.loan_amount

    			#print "Time 1 HERE :    ", time.time()-time1 
    			time2 = time.time()   
			remain=round(loan.loan_amount-advance_amount,2)
			if remain ==0.0 and loan.state not in ('draft','rejected'):
			    wf_service.trg_validate(uid,'hr.employee.loan',loan.id, 'done', cr)
			    cr.execute("""update hr_employee_loan set state='done', end_date=%s 
				          where id=%s  """,(time.strftime('%Y-%m-%d'),loan.id,))
			    #self.write(cr, uid, [loan.id], {'state':'done','end_date':time.strftime('%Y-%m-%d')},context=context)
    			#print "Time 2 HERE :    ", time.time()-time2
    			time3 = time.time()      
                        if loan.state=='done' and remain > 0.0:
			    wf_service.trg_validate(uid,'hr.employee.loan',loan.id, 'paid', cr)
			    self.write(cr, uid, [loan.id], {'state':'paid'},context=context)
    			#print "Time 3 HERE :    ", time.time()-time3 
			result[loan.id] = {
				'advance_amount': advance_amount,
				'remain_installment': remain}
    		#print "Time to compute amout (functionalfields) per loan :    ", time.time()-time1    
		return result

	def _get_employee_loan(self, cr, uid, ids, context={}, args={}):
	    """ 
	    Function to return the ids of loan to recalculate remisssion amount
	    
	    @param args: dictionary contain object name and field,
	    @return: list of IDS    
	    """
	    return self.pool.get('hr.employee.loan').search(cr, uid, [('loan_id', 'in', ids),
					('state','not in',('transfered','paid','done'))], context=context)	

	def _get_loan_archive(self, cr, uid, ids, context={}, args={}):
	    """ 
	    Function to return the ids of loan to recalculate remisssion amount
	    
	    @param args: dictionary contain object name and field,
	    @return: list of IDS    
	    """
	    result = {}
	    for line in self.pool.get('hr.loan.archive').browse(cr, uid, ids, context=context):
	        result[line.loan_id.id] = True
	    return result.keys()

        def get_refund(self, cr, uid, ids, loan_id, args,context=None) :
		res = {}
		payroll_obj= self.pool.get('payroll')
		addendum_refund = 0.0
		salary_refund = 0.0
		installment_amount = 0.0
		addendum_installment = 0.0
		for rec in self.browse(cr, uid, ids):
			loan_setting = rec.loan_id
			if rec.refund_from == 'salary' :
				salary_refund = rec.loan_amount
				addendum_refund = 0.0
			if rec.refund_from == 'addendum':
				addendum_refund = rec.loan_amount
				salary_refund = 0.0
			if rec.refund_from == 'both':
				paid_out = sum([arc.loan_amount for arc in rec.loan_arc_ids if arc.payment_type=='payment'])
				if loan_setting.adden_percentage_from == 'loan':
					addendum_refund = (rec.loan_amount  * rec.addendum_percentage /100) + rec.addendum_plus - rec.salary_plus -paid_out
					salary_refund = rec.loan_amount - addendum_refund + rec.salary_plus - rec.addendum_plus - paid_out
				else: # Will calculate from addendum
					addendum_ids = [addendum.id for addendum in loan_setting.addendum_ids]
 					addendum_dict = payroll_obj.allowances_deductions_calculation(cr,uid,rec.start_date,rec.employee_id,{}, addendum_ids,False,[])
					total_allow = addendum_dict['total_allow'] 
					addendum_refund = (total_allow * rec.addendum_percentage /100) + rec.addendum_plus - rec.salary_plus -paid_out
					# if addendum_refund mored than loan amount make it equal loan amount
					if addendum_refund > rec.loan_amount :
						addendum_refund = rec.loan_amount
					salary_refund = rec.loan_amount - addendum_refund + rec.salary_plus - rec.addendum_plus - paid_out
			#FIXME: addendum_install_no/addendum_installment
			addendum_install_no = rec.addendum_install_no >0 and rec.addendum_install_no  or 1
			total_installment = rec.total_installment  >0 and rec.total_installment  or 1
			###############
			addendum_installment = addendum_refund / addendum_install_no 
			installment_amount = salary_refund / total_installment 
			self.write(cr, uid, ids, {'installment_amount':installment_amount,'addendum_install':addendum_installment})
			res.update({rec.id: {'addendum_refund': addendum_refund ,
                                                     'salary_refund': salary_refund,
                                                     'installment_amount':installment_amount,
                                                      'addendum_install':addendum_installment}})
		return res

	_columns = {
		'code': fields.related('employee_id', 'emp_code', type='char', string='Code', store=True, readonly=True),
		'employee_id' :fields.many2one("hr.employee",'Employee', required= True ,readonly= True,states={'draft':[('readonly',False)]}, select=1),
		'department_id':fields.related('employee_id', 'department_id', string='Department', type='many2one', relation='hr.department',
						 readonly=True, store=True),
		'loan_id' :fields.many2one("hr.loan",'Loan', required= True,readonly= True,states={'draft':[('readonly',False)]}, select=1),
		'loan_amount' :fields.float("Loan Amount",digits=(18,2),readonly= True,states={'draft':[('readonly',False)],'requested':[('readonly',False)]}),
		'total_installment' :fields.integer("Salary Installment No",readonly= True ,states={'draft':[('readonly',False)],'requested':[('readonly',False)]}),
		'paid_installment' :fields.integer("Paid Installment"),
		'installment_amount' :fields.float("Installment Amount",digits=(18,2),readonly= True,),
		'remain_installment': fields.function(computee, method=True, string="Remain Amount", type='float',
             		store={
	                   'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['loan_amount','comments'], 20),
                           'hr.loan.archive': (_get_loan_archive,['loan_amount','loan_id','id'], 10),
                	  }, multi='sums'),
        	'remission_amount': fields.function(_get_remission, string='Remission Amount', method=True, type='float',
             		store={
	                   'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['loan_id','loan_amount'], 20),
                       'hr.loan': (_get_employee_loan, ['remission_type','remission'], 10),
                	  }),

		'start_date' :fields.date("Start Date", required= True ,readonly= True,states={'draft':[('readonly',False)]}, select=1),
		'end_date': fields.date('End Date',readonly= True,states={'draft':[('readonly',False)]}),
		'comments':fields.text("Comments",size=100),
		'advance_amount': fields.function(computee, method=True, string='Advance Amount',type='float',
			store={
	                   'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['loan_amount','comments'], 20),
                           'hr.loan.archive': (_get_loan_archive,['loan_amount','loan_id','id'], 10),
                	  }, multi='sums'),
		'state':fields.selection([('draft','Draft'),('requested','Requested'),
                                          ('approved','Approved'),('rejected','Rejected'),
                                          ('transfered','Transfered'),('paid','Paid'),
                                          ('suspend','Suspend'),('done','Done')],"State",readonly=True, select=1),
		'acc_remission_no' : fields.many2one("account.voucher",'Remission Voucher No',readonly=True),
		'name':fields.related('loan_id','name', type='char', readonly=True , string="Loan Name",size=50, store=True),
		'reject_reasons':fields.selection([('1','Employment years for Employee Not Fit employment Years for The Loan  '),
								('2','Total Loans Installments for The Department Exceed Max Percentage '),
								('3','Total Loans Installments for The Employee Exceed Max Percentage '),
								('4','Loan Limit is Once and Already Taken'),
								('5','Interference Between same Loan Not Allowed'),
								('6','Pension Reached Before Fininshig Loan Installments'),
								('7','Loan Not Allowed for The Degree of Employee'),
								('8','Because This Employee Salary is Suspended'),
								('9','Employee Loans Over Allowed Number')],"Rejection Reasons",readonly=True),
		'reject_date' :fields.date("Reject Date",readonly=True),
		'loan_suspend_ids':fields.one2many('hr.loan.suspend','loan_id',"Loans"),
		'acc_number' :fields.many2one("account.voucher",'Voucher',readonly=True),
		'loan_arc_ids':fields.one2many('hr.loan.archive','loan_id',"Loans"),
        'salary_plus': fields.float("Salary Plus"),
        'addendum_plus': fields.float("Addendum Plus"),
        'addendum_percentage': fields.float('Addendum Percentage',readonly= True,states={'draft':[('readonly',False)]}),
        'salary_refund': fields.function(get_refund, method=True , string='Salary Refund', 
				store = {'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['loan_id','addendum_plus','advance_amount','salary_plus','addendum_install_no','total_installment','addendum_percentage','loan_amount','refund_from'], 20)},multi='loan_id'),
        'addendum_refund': fields.function(get_refund, method=True, string="Addendum Refund", type='float', 
				store = {'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['loan_id','addendum_plus','salary_plus','advance_amount','addendum_install_no','total_installment','loan_amount','addendum_percentage','refund_from'], 20)},multi='loan_id'),
        'addendum_install_no' : fields.integer('Addendum Installment No'),
        'addendum_install' : fields.float('Addendum Installment Amount'),
        'refund_from' :fields.selection([('salary','Salary'),
                                         ('addendum','Addendum'),
                                         ('both' ,'Salary and Addendum')],'Refund From',readonly= True,
                                          states={'draft':[('readonly',False)],'requested':[('readonly',False)]}),

	}

	_defaults = {
		'employee_id': False,
		'state' : 'draft',
		'start_date':time.strftime('%Y-%m-%d'),
                'refund_from':'Salary',
		#'remain_installment':0
			}
        _sql_constraints = [
       	 	('date_check', "CHECK ( start_date < end_date)", "The start date must be anterior to the end date."),
                           ]

        def unlink(self, cr, uid, ids, context=None):
            for rec in self.browse(cr, uid, ids, context=context):
                if rec.state != 'draft':
                    raise osv.except_osv(_('Warning!'),_('You cannot delete an employee loan which in %s state.')%(rec.state))
            return super(hr_employee_loan, self).unlink(cr, uid, ids, context)


	def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        	"""
		Method that returns the  employee_type that allowed to take the loan.

           	@param emp_id: Id of employee
           	@return: Dictionary of values
        	"""
		emp_obj = self.pool.get('hr.employee')
		company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
		contractors = company_obj.loan_contractors
		employee = company_obj.loan_employee
		recruit = company_obj.loan_recruit
		trainee = company_obj.loan_trainee
		employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
                employee_domain['employee_id'].append(('state', '=', 'approved'))
		domain = {'employee_id':employee_domain['employee_id']}
		return {'domain': domain}

        def onchange_total_installment(self, cr, uid, ids, loan_id,total_installment,salary_instal=False,context={}):
		"""
		Method that changes the installment of the loan if the configuration allow so.
	      	@param loan_id: ID of Loan
	       	@param total_installment: The New Total Installment of Loan
	       	@return: Dictionary of values
			"""
		loan_setting = self.pool.get('hr.loan').browse(cr, uid, loan_id)
		if loan_id and total_installment:
		    if loan_setting.change_installment_no :
		        if salary_instal : 
		            return {'value': {'total_installment' : total_installment}}
		        else : 
		            return {'value': {'addendum_install_no' : total_installment}}
		    else :           
		        if salary_instal : 
		            return {'value': {'total_installment':loan_setting.installment_no}}
		        else : 
		            return {'value': {'addendum_install_no':loan_setting.addendum_install_no}}

	def onchange_loan_id(self, cr, uid, ids, loan_id,context={}):
        	"""
		Method that returns the amunt of the loan.
           	
		@param loan_id: Id of Loan
           	@return: Dictionary of loan value
        	"""
		loan_obj = self.pool.get('hr.loan')
		amount=0.0
		if loan_id:
			amount = loan_obj.browse(cr, uid, loan_id).amount
		return {'value': {'loan_amount':amount}}

	def onchange_loan_amount(self, cr, uid, ids,loan_id, loan_amount,installment_amount,context={}):
        	"""
		Method that changes the amunt of the loan if the configuration allow so.

	      	@param loan_id: ID of Loan
           	@param loan_amount: Amount of Loan
           	@return: Dictionary of values
        	"""
		loan_obj = self.pool.get('hr.loan')
		amount=0.0
		if loan_id:
                        loan_config=loan_obj.browse(cr, uid, loan_id)
			if loan_config.change_defult:
				amount=loan_amount
                                installment_amount=amount/loan_config.installment_no
			else:
				return self.onchange_loan_id(cr, uid, ids, loan_id,context=context)
		return {'value': {'loan_amount':amount,'installment_amount':installment_amount}}

	def request_loan(self, cr, uid,ids,context={}):
		"""
		Request loan for specific employee where it checks that the employee
		meets the conditions of the requested loan and the company general 
		trends in regard to loans if it violates one of them the request will
		be canceled.

		Could be rejected for following reasons:
		* Exceeding employment years or max percentage of department loan 
	          or max no of Installments
		* Has been already taken, loan interference, payments exceeding 
		  pension date, loan not allowed for the degree, salary is suspensed, 
		  loans over allowed

		@return: True
		"""
		loan_obj= self.pool.get('hr.loan')
		employee_obj = self.pool.get('hr.employee')
		payroll_obj= self.pool.get('payroll')
		reject_archive_obj= self.pool.get('hr.employee.loan')
		wf_service = netsvc.LocalService("workflow")
		for loan in self.browse(cr,uid,ids):
		   all_emp_ids=loan.employee_id.id
		   all_emp_obj=employee_obj.browse(cr,uid,[all_emp_ids])
		   emp_total_payroll=0.0
		   rejected = False
		   request_dict= {}
		   for emp in all_emp_obj:
			  total_payroll = 0
			  if emp.payroll_id and not emp.bonus_id.basic_salary:
				 raise osv.except_osv(_('ERROR'), _('You Must Enter bonus for the employee'))
			  allow_ids=loan.loan_id.allowances_id.id
			  total_payroll=0.0
			  total_payroll=payroll_obj.allowances_deductions_calculation(cr,uid,loan.start_date,loan.employee_id,{}, [],False,[])
			  total_payroll['total_allow']+= emp.bonus_id.basic_salary
			  emp_total_payroll+=total_payroll['total_allow']
			  if emp.id == loan.employee_id.id:
				 employee_payroll= total_payroll['total_allow']
		   if not loan.loan_id.degree_ids or (loan.loan_id.degree_ids and loan.employee_id.degree_id.id in [d.id for d in loan.loan_id.degree_ids]) : 
			  if loan.loan_id.loan_type=='amount':
				 total_loan=loan.loan_id.amount
				 install_amount= total_loan
				 total_per_month=install_amount
			  else:
					if loan.loan_id.installment_type=='fixed':
					   total_loan=loan.loan_id.amount
					   install_amount = loan.loan_id.amount/loan.loan_id.installment_no
					   total_per_month= install_amount
					else:
					   loan_based_salary=0.0
					   if allow_ids:
						  loan_based_salary=payroll_obj.read_allowance_deduct(cr, uid,loan.employee_id.id,[allow_ids],'allow')
					   '''if loan.loan_id.salary_included:
						  loan_based_salary+=loan.employee_id.bonus_id.basic_salary'''
					   total_loan=loan_based_salary * loan.loan_id.factor
					   install_amount = total_loan/loan.loan_id.installment_no 
					   total_per_month= install_amount
			  check_loan_ids=self.search(cr, uid, [('employee_id','=',loan.employee_id.id),('loan_id','=',loan.loan_id.id),('id','!=',loan.id),('state','!=','rejected')])
			  check_loan_idss=self.search(cr, uid, [('employee_id','=',loan.employee_id.id)])
			  counter = 0
                          # need review
			  if check_loan_ids or check_loan_idss:
				 check_loan_obj=self.browse(cr,uid,check_loan_ids)
				 for c in check_loan_obj:
					if c.loan_amount != c.advance_amount and c.id != loan.id:
					   counter=1
			  if (loan.loan_id.loan_limit=='one' and not check_loan_ids) or (loan.loan_id.loan_limit=='unlimit' and not check_loan_ids) or (loan.loan_id.loan_limit=='unlimit' and check_loan_ids and counter==0) or (loan.loan_id.loan_limit=='unlimit' and check_loan_ids and loan.loan_id.allow_interference) :
				 check_installment_ids=self.search(cr, uid, [('employee_id','=',loan.employee_id.id),('state','not in',('done','rejected'))])
				 if check_installment_ids:
                                        for c in self.browse(cr, uid,check_installment_ids):
					   total_per_month+= c.installment_amount
				
				 if not loan.employee_id.company_id.max_employee or not loan.employee_id.company_id.max_department :
					raise osv.except_osv(_('ERROR'), _('You Must Enter policy for Company'))
				 if total_per_month <= (employee_payroll*loan.employee_id.company_id.max_employee)/100 :
					all_total_per_month=total_per_month
					check_all_installments_ids=self.search(cr, uid, [('employee_id','=',all_emp_ids),('state','not in',('done','rejected'))])
					if check_all_installments_ids:
                                                for c in self.browse(cr, uid,check_all_installments_ids):
						   all_total_per_month+= c.installment_amount
					if all_total_per_month <= (emp_total_payroll*loan.employee_id.company_id.max_department)/100:
					   employment_years=False
					   if loan.loan_id.year_employment:
						  days= loan.loan_id.year_employment * 365
						  employment_dt = time.mktime(time.strptime(loan.employee_id.employment_date,'%Y-%m-%d'))
						  loan_dt = time.mktime(time.strptime(loan.start_date,'%Y-%m-%d'))
						  diff_day = (loan_dt-employment_dt)/(3600*24)
						  if diff_day >= days:
							  employment_years=True
					   if not loan.loan_id.year_employment or (loan.loan_id.year_employment and employment_years==True):
						  if not loan.employee_id.company_id.age_pension:
							 raise osv.except_osv(_('ERROR'), _('You must enter age pension in HR configuration'))
						  if not loan.employee_id.birthday:
							 raise osv.except_osv(_('ERROR'), _('You must enter employee birth date'))

						  else:
				
							 birth_dt = time.mktime(time.strptime(loan.employee_id.birthday,'%Y-%m-%d'))
							 loan_dt = time.mktime(time.strptime(loan.start_date,'%Y-%m-%d'))
							 years=((loan_dt-birth_dt)/(3600*24)) / 365
							 pension=loan.employee_id.company_id.age_pension - years 
							 '''if pension >= (loan.loan_id.installment_no / 12 ):
								if not loan.employee_id.salary_suspend:
								  request_dict = {
									   'loan_amount': total_loan ,
									   'installment_amount': install_amount}
								else:
								   request_dict={'reject_reasons' :'8'}
								   rejected = True

							 else:
								request_dict={'reject_reasons' :'6'}
								rejected = True'''
					   else:
						  request_dict={'reject_reasons' :'1'}
						  rejected = True
					else:
					   request_dict={'reject_reasons' :'2'}
					   rejected = True
				 else:
					   request_dict={'reject_reasons' :'3'}
					   rejected = True
			  
			  else:
				  if loan.loan_id.loan_limit=='one' and check_loan_ids: 
					 request_dict={'reject_reasons' :'4',}
					 
				  if loan.loan_id.loan_limit=='unlimit' and check_loan_ids and counter!= 0 and not loan.loan_id.allow_interference:
					 request_dict={'reject_reasons' :'5',}
				  rejected = True
			  #Allowed Number Loan(GRP) --------------------------------------------------
			  if (loan.employee_id.company_id.allowed_number and check_loan_idss):
					check_allowed_number_obj=self.browse(cr, uid,check_loan_idss)
					l=[ v.id for v in check_allowed_number_obj if v.state !='rejected']
					if len(l) >v.employee_id.company_id.allowed_number:
					   request_dict={'reject_reasons' :'9',}
					   rejected = True
		   else:
			  request_dict={'reject_reasons' :'7',}
			  rejected = True
		return self.write(cr, uid,[loan.id],request_dict,context=context)

	def check_loan(self, cr, uid,ids,context=None):
		"""
		Mehtod that checks if the loan is rejected or not.

		@return: Boolean True or False
		"""
		for loan in self.browse(cr,uid,ids):
			if loan.reject_reasons:
				return False
		return  True

	def suspend_end(self, cr, uid,ids,context=None):
		"""
		Workflow function that changes the state to 'paid'.

		@return: Boolean True 
		"""
		#today=time.strftime("%d/%m/%Y")
		#if state=='suspend' and end_suspend_date==today:
		#self.write(cr, uid,ids, {'state':'paid'},context=context)
		return  True

	def transfer(self, cr, uid,ids,context=None):
		"""
		Workflow function that transfers loan amount to voucher.

		@return: ID of the created voucher
		"""
		voucher_obj = self.pool.get('account.voucher')
		lines=[]
		for loan in self.browse(cr,uid,ids):
			if not  loan.loan_id.loan_account_id:
				raise osv.except_osv('ERROR', 'Please enter account_loan for loan')
			date = time.strftime('%Y-%m-%d')
			reference = 'HR/Loans/ '+" / "+str(date)
			partner_id=loan.employee_id.address_id and loan.employee_id.address_id.id or False
			loan_dict={
				'account_id': loan.loan_id.loan_account_id.id,
				'amount': loan.loan_amount,
			          }
			lines.append(loan_dict)
			voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,'lines':lines,
                                                                                      'department_id':loan.employee_id.department_id.id,
                                                                                      'partner_id':partner_id},context=context)
			self.write(cr,uid,[loan.id],{'acc_number': voucher,'state':'transfered'})                    
		return voucher


	def set_to_draft(self, cr, uid, ids,context=None):
		"""
		Method that resets the workflow and change loan's state to 'draft'.

		@return: Boolean True
		"""
		self.write(cr, uid, ids, {'state': 'draft'},context=context)
		wf_service = netsvc.LocalService("workflow")
		for id in ids:
			wf_service.trg_delete(uid, 'hr.employee.loan', id, cr)
			wf_service.trg_create(uid, 'hr.employee.loan', id, cr)
		return True

	def write(self,cr,uid,ids,vals,context=None):
	   """
	   Method that assures the suspension's information has been entered in the case of suspending the loan.

	   @return: Super write method
	   """
	   if 'state' in vals and vals['state']=='suspend':
		  for loan in self.browse(cr,uid,ids,context):
			 if not loan.loan_suspend_ids:
				raise osv.except_osv(_('ERROR'), _('Enter suspend information'))
	   return super(hr_employee_loan,self).write(cr, uid, ids, vals)

	def copy(self, cr, uid, ids, default={}, context=None):
	        """
		Inherit copy method that copies the current record to reset 
		the defualt values.

	        @return: Super copy method
	        """
		default.update({
			'state': 'draft',
			'name': '/',
			'voucher_id': False,
			'acc_number':'',
                        'reject_reasons':'',
                        'loan_amount':False , 
		        'installment_amount':False ,
		        'start_date':time.strftime('%Y-%m-%d') ,
		        'end_date':False ,

		})
		return super(hr_employee_loan, self).copy(cr, uid, ids, default, context) 
        def set_to_draft(self, cr, uid, ids,context=None):
		"""
		Method that resets the workflow and change loan's state to 'draft'.

		@return: Boolean True
		"""
		self.write(cr, uid, ids, {'state': 'draft'},context=context)
		wf_service = netsvc.LocalService("workflow")
               # print"<><><><><><><><><><",wf_service
		for id in ids:
			wf_service.trg_delete(uid, 'hr.employee.loan', id, cr)
			wf_service.trg_create(uid, 'hr.employee.loan', id, cr)
		return True

###################################################paid loan############
        def paid_loan(self, cr, uid, ids,context=None):
		"""
		Method that resets the workflow and change loan's state to 'paid'.

		@return: Boolean True
		"""
                for loan in self.browse(cr,uid,ids):
		        wf_service = netsvc.LocalService("workflow")
		        wf_service.trg_validate(uid,'hr.employee.loan', loan.id, 'loan_paids', cr)
		        self.write(cr ,uid , ids , {'state' : 'paid'},context = context)
                return True
  
        #def _needaction_domain_get(self, cr, uid, context=None):
         #  emp_obj = self.pool.get('hr.employee')
           #empids = emp_obj.search(cr, uid, [('parent_id.user_id', '=', uid)], context=context)
           #dom = ['&', ('state', '=', 'confirm'), ('employee_id', 'in', empids)]
           # if this user is a hr.manager, he should do second validations
          # if self.pool.get('res.users').has_group(cr, uid, 'base.group_hr_manager'):
              #dom = ['|'] + dom + [('state', '=', 'prepost')]
           #   dom =  [('state', '=', 'approved')]
           

           #return dom 
#----------------------------------------
#loan suspend
#----------------------------------------
class hr_loan_suspend(osv.osv):
	_name = "hr.loan.suspend"
        _description = "Suspended Loan"
	_columns = {
		'loan_id' :fields.many2one("hr.employee.loan",'Loan', required= True),
		'start_date' :fields.date("Start Date", required= True),
		'end_date' :fields.date("End Date", required= True),
		'comments':fields.text("Comments",size=100),
	}
#----------------------------------------
#payroll main archive (inherit)
#----------------------------------------

class hr_payroll_main_archive(osv.Model):

	def total_allow_deduct(self,cr,uid,ids,name, args,context=None):
	        """
		Method for functional field that overwrites hr.payroll.main.archive 
		total_allow_deduct mehtod and caluclates the totals of employee's 
		allowances, deductions, tax, loans and gets the net.
                There are Options can be passed in dictionary:
			2- no_loans: Not calculate for total_loans 
		@param name: name of field to be updated
		@param args: other arguments
	        @return: Dictionary of values 
	        """
########################################################################################################	       
                emp_loan_obj = self.pool.get('hr.employee.loan')
	        loan_archive_obj = self.pool.get('hr.loan.archive')
	        wf_service = netsvc.LocalService("workflow")
		tax= self.pool.get('hr.tax')
                date= time.strftime('%Y-%m-%d')
		result={}
                #print"SSSSSSSSSSSSS",len(ids),">>>>>>>>",context
                query_start = time.time()
                cr.execute(""" select
				   ma.id , sum(a.amount) as amount, sum(tax_deducted) as tax_deducted, a.type, ad.taxable
				   from  hr_payroll_main_archive ma, 
				   hr_allowance_deduction_archive a,
				   hr_allowance_deduction ad
				   where a.main_arch_id = ma.id and ad.id=a.allow_deduct_id and ma.id in %s 
				   group by ma.id , a.type, ad.taxable
			      """ ,(tuple(ids),))
               	res1= cr.dictfetchall()
                #print">>>>>> Compute query time ", time.time() -query_start 
                dic_start = time.time()
                res2= defaultdict(list)
                count =0 
                for key, group in itertools.groupby(res1, lambda item: item['id']):
                    res2[key].extend([item for item in group])
                #print">>>>>>>>",res2
                total_part1 = 0
                total_part2 = 0
                #print">>>>>> Dictionary time ", time.time() - dic_start
		for rec in self.browse(cr, uid, ids, context=context):
                        part1_start = time.time()
			taxable_amount=0.0
			total_allowance=rec.basic_salary
			allowances_tax=0.0
			income_tax=0.0
			total_deduction=0.0

			'''cr.execute(""" select
				   sum(a.amount) as amount, sum(tax_deducted) as tax_deducted, a.type, ad.taxable
				   from  hr_payroll_main_archive ma, 
				   hr_allowance_deduction_archive a,
				   hr_allowance_deduction ad
				   where a.main_arch_id = ma.id and ad.id=allow_deduct_id and ma.id=%s 
				   group by a.type, ad.taxable
			      """ ,(rec.id,))
			res= cr.dictfetchall()'''
                        #Used to read from dictionary
                        #print">>>>>>>>>>>",res2.get(rec.id, [])
			for r in res2.get(rec.id, []):
			    if r['type'] =='allow':
				total_allowance += r['amount']
				allowances_tax += r['tax_deducted']
				if r['taxable'] and not rec.employee_id.tax_exempted:
				    taxable_amount += r['amount']*0.45
			    else:
			        total_deduction += r['amount']
			'''for line in rec.allow_deduct_ids:
				if line.type=='allow':
				    total_allowance+=line.amount
				    allowances_tax+=line.tax_deducted
				    if line.allow_deduct_id.taxable and not rec.employee_id.tax_exempted:
					taxable_amount+=line.amount*0.45
				else:
					total_deduction+=line.amount
					#if line.allow_deduct_id.taxable and not rec.employee_id.tax_exempted:
						#taxable_amount-=line.amount - line.allow_deduct_id.exempted_amount'''
			'''if not rec.employee_id.tax_exempted:
				taxable_amount+=rec.basic_salary*45/100
                                xx=taxable_amount-105
                                taxable_amount =xx-taxable_amount*8/100
				tax_id=tax.search(cr,uid,[('active','=','True'),('taxset_min','<=',taxable_amount),('taxset_max','>=',taxable_amount)])
			        if tax_id:
				     tax_rec=tax.browse(cr,uid,tax_id)[0]
				     taxable_amount = abs(taxable_amount ) 
				     income_tax=(((taxable_amount-tax_rec.taxset_min)*tax_rec.percent)/100) + tax_rec.previous_tax'''
                	#print "Time 4:    ", time.time()-time4      
			result[rec.id] = {
				'tax':income_tax,
				'total_allowance':total_allowance,
				'allowances_tax': allowances_tax,
				'total_deduction': total_deduction+allowances_tax+income_tax,
				'net':(total_allowance-allowances_tax-total_deduction-income_tax),
			}
                     
                        total_part1 += time.time() - part1_start
                        part2_start = time.time()
                        if context.get('with_loans', True):
                            total_loans = 0
      		            total_loans+= sum([l.loan_amount for l in rec.loan_ids])
		            result[rec.id].update({'total_loans':total_loans,
						   'net':result[rec.id]['net']-total_loans,})                   
                            total_part2 += time.time() - part1_start

                #print "**********Fields part1  ", total_part1, "**********Fields part2  ", total_part2
	   	return result

	_inherit="hr.payroll.main.archive"
	_columns={
		'loan_ids':fields.one2many('hr.loan.archive','main_arch_id',"Loans"),
		'total_loans': fields.function(total_allow_deduct, string='Total Loans', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
		'total_allowance' :fields.function(total_allow_deduct, string='Total Allowance', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
		'tax' :fields.function(total_allow_deduct, string='Income Tax', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
		'allowances_tax' :fields.function(total_allow_deduct, string='allowance Taxes', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
		'total_deduction' :fields.function(total_allow_deduct, string='Total Deduction', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
		'net' :fields.function(total_allow_deduct, string='Salary Net', type='float',
                                          digits_compute=dp.get_precision('Payroll'), multi='sum', readonly=True, store=True),
	}
class hr_loan_archive(osv.osv):
	_name = "hr.loan.archive"
        _description = "Loan Archive"
	_columns = {
		'payroll_id' : fields.many2one('hr.salary.scale', 'Salary',required=True ,readonly=True),
		'code': fields.char('Code', size=64),
		'employee_id' : fields.many2one('hr.employee',"Employee", required= True),
		'month' :fields.integer("Month", size=8, required= True),
		'year' :fields.integer("Year", size=8, required= True),
		'loan_id' :fields.many2one("hr.employee.loan",'Loan Name', required= True),
		'loan_amount' :fields.float("Loan Amount", digits=(18,2), required= True),
		'payment_type': fields.selection([('salary','Salary'),('addendum','Addendum'),('remission','Remission'),
					('payment','Payment'), ('termination','Termination')],
					'Payment Type',required=True),
		'main_arch_id' : fields.many2one('hr.payroll.main.archive', 'Payroll',ondelete='cascade'),
		'addendum_id' : fields.many2one('hr.allowance.deduction.archive', 'Addendum',ondelete='cascade'),
	}


        def unlink(self, cr, uid, ids, context=None):
            loan_obj = self.pool.get('hr.employee.loan')
            for rec in self.browse(cr, uid, ids, context=context):
                if rec.payment_type in ('salary','termination'):
                    raise osv.except_osv(_('Warning!'),_('You cannot delete this loan installment which is paid from payroll'))
                if rec.payment_type in ('remission') and rec.loan_id.acc_remission_no:
		    voucher = rec.loan_id.acc_remission_no 
		    if voucher.state in ('reversed'): continue
		    elif voucher.state in ('posted','paid'): 
			raise osv.except_osv(_('Warning!'),_('You cannot delete this loan installment, the remission \
							voucher is paid, reverse it first ')) 
		    else: 
			context.update({'unlink':True})
			if rec.payment_type == 'payment':
		    	    remission_id = self.pool.get('hr.loan.archive').search(cr, uid, \
						[('loan_id', '=', rec.loan_id.id), ('payment_type', '=', 'remission')]) 
			    if remission_id: self.unlink(cr, uid, remission_id, context)
			self.pool.get('account.voucher').unlink(cr, uid, [voucher.id], context)
            return super(hr_loan_archive, self).unlink(cr, uid, ids, context)

#----------------------------------------
#Payroll Calculation
#---------------------------------------- 
class hr_employee_salary_addendum(osv.osv):
    _inherit = 'hr.employee.salary.addendum'

    def get_loan(self, cr, uid ,ids,data,  context=None):
        loan_arc=[]
        for rec in self.browse(cr, uid, ids, context=context):
            for arc in rec.arch_ids:
                for loan in arc.loan_ids:
                     loan_arc.append(loan.id) 	
	if loan_arc:
            cr.execute("select distinct hr_loan.id from hr_loan_archive \
			left join hr_employee_loan  on (hr_loan_archive.loan_id = hr_employee_loan.id)\
			left join hr_loan  on (hr_employee_loan.loan_id = hr_loan.id) where hr_loan_archive.id in %s" , (tuple(loan_arc),))
            loan_ids = [r[0] for r in cr.fetchall()]
	return {'archive_ids':loan_arc, 'loan_ids':loan_arc and loan_ids or []}

    def pay(self, cr, uid ,ids,  context=None):
	loan_archive_obj = self.pool.get('hr.loan.archive')
	loan_obj = self.pool.get('hr.loan')
        data = self.get_data(cr, uid, ids, context = context)
	pay = super(hr_employee_salary_addendum, self).pay(cr, uid, ids, context) 
	data_loan = self.get_loan(cr, uid , ids, data,  context=None)
	if data_loan['archive_ids']:
	    res = {}    
	    for loan in loan_obj.browse(cr, uid, data_loan['loan_ids'], context):
		if not loan.loan_account_id:
		    raise osv.except_osv(_('ERROR'), _('Please enter account  for \
					Loan: %s')%(loan.name))
	        res[loan.id]  = {'account_id':loan.loan_account_id.id , 'amount':0, 'name':loan.name} 
	    for archive in loan_archive_obj.browse(cr, uid, data_loan['archive_ids'], context):
	        res[archive.loan_id.loan_id.id]['amount'] -= archive.loan_amount
	    if res: pay['lines']=pay['lines']+ res.values()
        return  pay	

    def compute(self, cr, uid, ids, context = {}):	
        """Compute salary/addendum for all employees or specific employees in specific month.
           Inherited to add computation of Loans
           @return: Dictionary 
        """
        first_start = time.time()
        main_arch_obj = self.pool.get('hr.payroll.main.archive')
	emp_loan_obj = self.pool.get('hr.employee.loan')
	loan_archive_obj = self.pool.get('hr.loan.archive')
        wf_service = netsvc.LocalService("workflow")
        date= time.strftime('%Y-%m-%d')        
        context.update({'calculate_functional_field':True, 'with_loans': False})
        super_start =time.time()
        res = super(hr_employee_salary_addendum, self).compute(cr, uid, ids, context)
        #print">>>>>>>>>>>>> Total time of super",time.time()- super_start
        loan_start = time.time()
        loan_archive_ids = []
	for rec in main_arch_obj.browse(cr, uid, res.get('archive_ids',[]), context=context):
		time5 = time.time()                                 
		loan_list=[]
		loan_amount=0.0
		total_loans = 0.0
		loan_dict={'payroll_id' :rec.employee_id.payroll_id.id,
			  'employee_id':rec.employee_id.id,
			  'month':rec.month,
			  'year':rec.year,
			  'payment_type':'salary',
			  'main_arch_id' :rec.id,}
		loan_addendum_dict={'payroll_id' :rec.employee_id.payroll_id.id,
			  'employee_id':rec.employee_id.id,
			  'month':rec.month,
			  'year':rec.year,
			  'payment_type':'addendum',
			  'main_arch_id' :rec.id,}
                #print"RRRRRRRRRR",rec.net
		net=rec.net
		loan_ids= emp_loan_obj.search(cr, uid,[('employee_id','=',rec.employee_id.id),('state','in',('paid','suspend','transfered')),('start_date','<=',rec.salary_date),('loan_id.refund_from','in',['salary','both'])])

		if loan_ids and rec.arch_id.type =='salary':	
		       loans_obj = emp_loan_obj.browse(cr,uid,loan_ids)
		       for loan in loans_obj:
				 time611 = time.time()                                                                  
			      #paid_installment= loan_archive_obj.search(cr,uid,[('employee_id','=',rec.employee_id.id),('loan_id','=',loan.id),('month','=',rec.month),('year','=',rec.year)])
				 amount = 0.0
			      #if not paid_installment:
				 # if loan installment not paid from loan paid wizard for current month then get installment loan amount for current month to deduct from salary 
				 if loan.remain_installment:
					if loan.loan_id.loan_type =='amount':
					       if loan.loan_amount <= net:
						      amount=loan.loan_amount
					       else:
						      amount=net
					else:
					       if loan.state <> 'suspend':
						      amount=loan.installment_amount
					       else:
						      #if loan susbend compare the end date of suspend with salary date  
						      for suspend in loan.loan_suspend_ids :
							 if suspend.start_date >= rec.salary_date or (suspend.start_date <= rec.salary_date and (suspend.end_date and suspend.end_date <= rec.salary_date)):
								amount=loan.installment_amount
								if suspend.start_date <= rec.salary_date and suspend.end_date <= rec.salary_date:
				                                       #print">>>>>>>>>>>>>>>>>>>>>>>>>"
								       res = wf_service.trg_validate(uid,'hr.employee.loan',loan.id, 'paid', cr)

				 	time622 = time.time()                                                                  
					if amount and net > 0.0 :
					       #TODO: what if (loan.remain_installment<loan.remission)??
					       if loan.remain_installment-loan.remission_amount < loan.installment_amount:
						      amount = loan.remain_installment-loan.remission_amount
			
					       if amount >= net:
						      amount= net

					       loan_dict.update({'loan_id':loan.id,'loan_amount':amount,})  
					       net-=amount
				               #print"FFFFFFFFFFFFFFFFFF",loan_dict
					       {'loan_id': 8102, 'employee_id': 735, 'payroll_id': 1, 'month': 5, 'loan_amount': 180.0, 'payment_type': 'salary', 'main_arch_id': 2243713, 'year': 2017}
			  		       loan_archive_obj.create(cr,uid,loan_dict, {'amount':amount})
                                               loan_archive_ids.append(rec.id)
		elif rec.arch_id.type =='addendum':
		   loans_ids= emp_loan_obj.search(cr, uid,[('employee_id','=',rec.employee_id.id),('state','in',('paid','suspend')),('start_date','<=',rec.salary_date),('loan_id.refund_from' ,'in',['addendum','both']),('loan_id.addendum_ids','in',[re.id for re in rec.arch_id.addendum_ids if re])])
		   #print">>>>>>>>>>loans_ids addendum>>>>>>>>>>>>>>>",loans_ids
		   if loans_ids:
		       alw_dec_arch=self.pool.get('hr.allowance.deduction.archive')
		       for loan in emp_loan_obj.browse(cr,uid,loans_ids):
			      #paid_installment= loan_archive_obj.search(cr,uid,[('employee_id','=',rec.employee_id.id),('loan_id','=',loan.id),('month','=',rec.month),('year','=',rec.year)])
				 amount = 0.0
			      
			      #if not paid_installment:
				 # if loan installment not paid from loan paid wizard for current month then get installment loan amount for current month to deduct from salary  
				 loan_adndm_ids= [ln.id for ln in loan.loan_id.addendum_ids]
				 if loan.remain_installment and len(loan_adndm_ids)>0 :
				     for adn in rec.arch_id.addendum_ids:
				        adndm_amount=0
				        if adn.id in loan_adndm_ids :
				            domn=[('allow_deduct_id','=',adn.id),('main_arch_id','=',rec.id)]
				            ad_arch_ids = alw_dec_arch.search(cr,uid,domn)
				            if ad_arch_ids:
				                ad_arch = alw_dec_arch.browse(cr,uid,ad_arch_ids)[0]
				                adndm_amount=ad_arch.amount-ad_arch.imprint-ad_arch.tax_deducted
				                ather_loan_ids = loan_archive_obj.search(cr,uid,[('addendum_id','=',ad_arch.id),('main_arch_id','=',rec.id)])
				                if ather_loan_ids:
				                    for sm in loan_archive_obj.browse(cr,uid,ather_loan_ids):
				                        adndm_amount-=sm.loan_amount
						if loan.loan_id.loan_type =='amount':
						       if loan.loan_amount <= adndm_amount:
							      amount=loan.loan_amount
						       else:
							      amount=adndm_amount
						else:
						       if loan.state <> 'suspend':
							      amount=loan.addendum_install
						       else:
							      #if loan susbend compare the end date of suspend with salary date  
							      for suspend in loan.loan_suspend_ids :
								 if suspend.start_date >= rec.salary_date or (suspend.start_date <= rec.salary_date and (suspend.end_date and suspend.end_date <= rec.salary_date)):
									amount=loan.installment_amount
									if suspend.start_date <= rec.salary_date and suspend.end_date <= rec.salary_date:
									       res = wf_service.trg_validate(uid,'hr.employee.loan',loan.id, 'paid', cr)
						if amount and adndm_amount > 0.0 :
						       #TODO: what if (loan.remain_installment<loan.remission)??
						       if loan.remain_installment-loan.remission_amount < loan.installment_amount:
							      amount = loan.remain_installment-loan.remission_amount
						       if amount >= adndm_amount:
							      amount= adndm_amount
						       loan_addendum_dict.update({'loan_id':loan.id, 											'loan_amount':amount,'addendum_id': ad_arch.id}) 
						       adndm_amount-=amount
				  		       loan_archive_obj.create(cr,uid,loan_addendum_dict)
                                                       loan_archive_ids.append(rec.id)

        #print">>. Toatal time of create loans", time.time() -loan_start
        second_write = time.time()
        context.update({'with_loans':True})
        main_arch_obj.write(cr, uid, loan_archive_ids, {}, context)
       # print">>>>>>>>>>>>> End of second write ",time.time() - second_write
       # print">>>>>>>>>>>>> END OF Last Computation", time.time() - first_start 
        #raise  
        return res 
#----------------------------------------
#delegation (inherit)
#----------------------------------------

class hr_employee_delegation(osv.osv):
	_inherit = "hr.employee.delegation"

        """
	Inherets hr.employee.delegation and adds function to check if the employee
	has loan befor delegating  him.
        """        
	_columns ={
			   'loan':fields.selection([('none','None'),('suspend','Suspend'), ('done','Done')]," Loans",readonly=True, states={'draft':[('readonly',False)]}),
	}
 
	def check_loan(self, cr, uid, ids, context=None):
		message = ''
		emp_loan_obj = self.pool.get('hr.employee.loan')
		for r in self.browse(cr, uid, ids):
			if r.loan!='none':
				state=['done','rejected']+[r.loan]
				loans=emp_loan_obj.search(cr,uid,[('end_date', '>=', r.start_date),('start_date', '<=', r.end_date),('state','not in',state),('employee_id','=',r.employee_id.id)],context=context)
				if loans:
					message = _('This employee has loan')
			if message:
				if not r.message:
					cr.execute('update hr_employee_delegation set message=%s where id=%s', (message, r.id))
				return False
		return True
#----------------------------------------
#Add  exception employee terminate
#----------------------------------------
class hr_employment_termination(osv.Model):
    """
    Inherits hr.employment.termination to add method that checks if the terminated 
    employee has remain loan to pay.
    """
    _inherit = "hr.employment.termination"
        
    def calculation(self, cr, uid, ids, transfer, context=None):
       
       
        transfer = transfer ==True and transfer or False
	emp_loan_obj = self.pool.get('hr.employee.loan')
        payroll = self.pool.get('payroll')
	termination_ids = super(hr_employment_termination, self).calculation(cr, uid, ids,transfer=False, context=context)
        for rec in self.browse(cr, uid, ids, context=context):
            loan_ids = emp_loan_obj.search(cr, uid, [('employee_id','=',rec.employee_id.id),\
								('remain_installment','<>',0)])
	    lines = []
	    for l in emp_loan_obj.browse(cr, uid, loan_ids, context):
		if not  l.loan_id.loan_account_id:
		    raise osv.except_osv('ERROR', 'Please enter account_loan for loan')
            	line_id = self.pool.get('hr.employment.termination.lines').create(cr, uid,
           				 {'termination_id':rec.id, 'account_id':l.loan_id.loan_account_id.id, 'name':l.name, 
					  'amount':-l.remain_installment})
		lines.append(line_id)
		if transfer:                
		    paid_dict = {
                       'payroll_id': rec.employee_id.payroll_id.id,
		       'employee_id': rec.employee_id.id,
		       'loan_id': l.id,
		       'loan_amount': l.remain_installment,
		       'month' : int(time.strftime('%m')),
		       'year' :  int(time.strftime('%Y')),
		       'comments': _('Termination'),
		       'payment_type':'termination',
	      		  }
                    self.pool.get('hr.loan.archive').create(cr, uid, paid_dict,context={})
        return lines + termination_ids
#----------------------------------------
# Inherit payroll class
#----------------------------------------
class payroll(osv.osv):

	_inherit = "payroll"
	
	def current_salary_status(self, cr, uid,ids, emp_obj, date):
		"""Retrieve employees's current salary amount.
			@param date: date
			@return: Current salary amount
		"""
		salary_status = super(payroll, self).current_salary_status(cr, uid,ids, emp_obj, date)
		loan_obj = self.pool.get('hr.loan')
		employee_loan_obj = self.pool.get('hr.employee.loan')
		loan_ids = loan_obj.search(cr, uid, [('refund_from','in',('salary','both'))])
		domain=[('start_date', '<=', date),('state','in',('paid','suspend')), ('remain_installment','>',0), ('employee_id','=', emp_obj.id),('loan_id','in',loan_ids)]
		employee_loan_ids = employee_loan_obj.search(cr, uid, domain)
		loan_amount = 0
		for loan in employee_loan_obj.browse(cr, uid, employee_loan_ids):
			if loan.installment_amount < loan.remain_installment:
				loan_amount += loan.installment_amount
			else: 
				loan_amount += loan.remain_installment
		salary_status.update({'total_loans': loan_amount})  
		salary_status['balance']-=loan_amount
		#print "++++++++++++++++++",salary_status['balance'],loan_amount
		return salary_status

#----------------------------------------
#Loan Payment
#----------------------------------------
class hr_employee_loan_paid(osv.osv):

    _name ='hr.employee.loan.paid'

    _description = "Employee's Out Of Salary Loan Payment"

    _columns = {
        'name' : fields.char("Name", size=64 , readonly=True ),
        'employee_id' :fields.many2one("hr.employee",'Employee', required= True , readonly= True,states={'draft':[('readonly',False)]}),
        'loan_id': fields.many2one('hr.employee.loan', 'Loan',required=True , readonly= True,states={'draft':[('readonly',False)]}),
        'loan_amount' :fields.float("Amount", digits=(18,2) , required= True, readonly= True,states={'draft':[('readonly',False)]}),
        'date' :fields.date("Date", required= True ,readonly= True,states={'draft':[('readonly',False)]}),
        'month': fields.selection([(1, '1'),(2,'2'),(3, '3'),(4, '4'),(5, '5'),(6, '6'),
                                   (7, '7'),(8, '8'),(9, '9'),(10, '10'),(11, '11'),(12, '12')],'Month',required= True,  readonly= True,states={'draft':[('readonly',False)]}),
        'year' :fields.integer("Year", required= True, readonly= True,states={'draft':[('readonly',False)]}),
        'note':fields.text("Notes",size=20),
        'pay_type':fields.selection([('installment','Installment') , ('once','Once')],"Pay Type",required= True,  readonly= True,states={'draft':[('readonly',False)]}),
        'installment_no' :fields.integer("Installments Number", readonly= True,states={'draft':[('readonly',False)]}),
        'rais' :fields.float("Rais", digits=(18,2), readonly= True,states={'draft':[('readonly',False)]}),
        'voucher_id' :fields.many2one("account.voucher",'Voucher',readonly=True),
        'state':fields.selection([('draft','Draft') ,('complete','Complete'),('confirm','Confirm'), ('paid','Paid'),('cancel','Cancel')],"status",readonly=True),
	'refund_remain_from':fields.selection([('salary','Salary'),('addendum','Addendum')],'Refund Remain From', required= False ),

         }
    _defaults={
        'name' :'/',
        'employee_id': False,
        'date':time.strftime('%Y-%m-%d'),
        'year': int(time.strftime('%Y')),
        'month': int(time.strftime('%m')),
        'pay_type':'once',
        'state':'draft',
        
    }
    def _loan_amount_check(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state =='draft' and rec.loan_amount > rec.loan_id.remain_installment:
                return False
        return True
        
    def _month_year_check(self, cr, uid, ids, context=None):
        loan_archive_obj = self.pool.get('hr.loan.archive')
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state =='draft' and  rec.pay_type=='installment':
                archive_ids= loan_archive_obj.search(cr,uid,[('loan_id','=',rec.loan_id.id),('month','=',rec.month),('year','=',rec.year)])
                if archive_ids:
                    return False
        return True
        
    _sql_constraints = [
       ('amount_check', 'CHECK (loan_amount > 0)', "Loan amount should be greater than Zero!"),
    ]
    _constraints = [
        (_month_year_check, _('Loan installment is already paid for selected month in selected year!'), []),
        (_loan_amount_check, "Amount is greater than remain amount", []), 
    ]
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, self._name)
        new_id = super(hr_employee_loan_paid, self).create(cr, user, vals, context)
        return new_id
        
    def unlink(self, cr, uid, ids, context=None):
        """
        This method prevent record deletion if it is not in draft state
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete an employee loan which in %s state.')%(rec.state))
        return super(hr_employee_loan_paid, self).unlink(cr, uid, ids, context)
        
    def copy(self, cr, uid, ids, default={}, context=None):
        """
        Inherit copy method that copies the current record to reset 
        the defualt values.

        @return: Super copy method
        """
        default.update({
            'state': 'draft',
            'name': '/',
            'voucher_id': False,
            'date':time.strftime('%Y-%m-%d') ,
        })
        return super(hr_employee_loan_paid, self).copy(cr, uid, ids, default, context) 

    def onchange_employee(self, cr, uid, ids, emp_id,context={}):
        #employee_type domain
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.loan_contractors
        employee = company_obj.loan_employee
        recruit = company_obj.loan_recruit
        trainee = company_obj.loan_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        employee_domain['employee_id'].append(('state', '=', 'approved'))
        domain = {'employee_id':employee_domain['employee_id']}
        return {'domain': domain}
        
    def onchange_pay_type(self,cr,uid, ids,loan_id,pay_type,loan_amount):
        """
        Retrieve number of installment to be paid if the pay type is monthly installments 
        based on paid amount and loan installment amount, and retrive the residual amount.
        """
        emp_loan_obj = self.pool.get('hr.employee.loan')
        installment_no=rais=0
        if loan_id:
            loan = emp_loan_obj.browse(cr, uid, loan_id)
            if loan.loan_id.loan_type=='amount':
                return {'value': {'pay_type':'once'}}
            if pay_type=='installment':
                installment_no= math.trunc(loan_amount/loan.installment_amount)
                rais = round(loan_amount - (loan.installment_amount * installment_no),2)
        return {'value': {'installment_no':installment_no,'rais':rais}}
        
    def set_to_draft(self, cr, uid, ids,context=None):
        """
        Method that resets the workflow and change loan's state to 'draft'.

        @return: Boolean True
        """
        self.write(cr, uid, ids, {'state': 'draft'},context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr.employee.loan.paid', id, cr)
            wf_service.trg_create(uid, 'hr.employee.loan.paid', id, cr)
        return True
        
    def confirm(self, cr, uid,ids,context=None):
        """
        Workflow function that transfers loan amount to voucher.

        @return: ID of the created voucher
        """
        voucher_obj = self.pool.get('account.voucher')
        
        for loan in self.browse(cr, uid, ids):
            if not  loan.loan_id.loan_id.loan_account_id:
                raise osv.except_osv('ERROR', 'Please enter account_loan for loan')
            date = time.strftime('%Y-%m-%d')
            reference = 'HR/Loans/ '+" / "+str(date)
            partner_id=loan.employee_id.address_id and loan.employee_id.address_id.id or False
            lines=[{
                'account_id': loan.loan_id.loan_id.loan_account_id.id,
                'amount': loan.loan_amount,
            }]
            voucher=self.pool.get('payroll').create_payment(cr, uid, ids,{'reference':reference,
                                                                          'lines':lines,
                                                                          'narration':"Employee's Out Of Salary Loan Payment",
                                                                          'ttype':'sale',
                                                                          'partner_id':partner_id},context=context)
            #voucher_id=voucher_obj.search(cr,uid,[('number','=',voucher)])
			#print">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>voucher_id" ,voucher_id
            #self.write(cr,uid,[loan.id],{'state':'confirm','voucher_id':voucher_id[0]})
            self.write(cr,uid,[loan.id],{'state':'confirm','voucher_id':voucher})
        return voucher

    def paid_loan(self,cr,uid, ids, context={}):
        """
        Paying loan for employee.
        """
        loan_archive_obj = self.pool.get('hr.loan.archive')
        loan_paid_obj = self.browse( cr, uid, ids)
        for rec in loan_paid_obj:
			loan_dict={
                    'payroll_id': rec.employee_id.payroll_id.id,
                    'employee_id': rec.employee_id.id,
                    'employee_id': rec.employee_id.id,
                    'loan_id': rec.loan_id.id,
                    'loan_amount': rec.loan_amount,
                    'month' : rec.month,
                    'year' : rec.year,
                    'comments': rec.note,
                    'payment_type' :'payment'
            }
			if rec.pay_type=='once': 
				loan_archive_obj.create(cr, uid, loan_dict,context={})
			else:
				installment=1
				month = int(rec.month)
				year =   rec.year
				while installment <= rec.installment_no:
					amount=rec.loan_id.installment_amount
					if installment==rec.installment_no and rec.rais > 0.0:
						amount+=rec.rais
					loan_dict.update({
                        'loan_amount': amount,
                        'month' : month,
                        'year' : year,
                        
                    })
					loan_archive_obj.create(cr, uid, loan_dict,context={})
					if month == 12:
						month = 1
						year = year+1
					else:
						month+=1
					installment+=1 
			if rec.refund_remain_from:
				paid_slary_amount = 0 
				paid_addendum_amount = 0
				paid_ids = loan_archive_obj.search(cr, uid, [('loan_id','=',rec.loan_id.id)])
				for paid in loan_archive_obj.browse(cr, uid, paid_ids):
					if paid.payment_type == 'salary': paid_slary_amount+= paid.loan_amount
					if paid.payment_type == 'addendum': paid_addendum_amount+= paid.loan_amount
					if rec.refund_remain_from == 'salary':
						rec.loan_id.write({'salary_plus': rec.loan_id.addendum_refund - paid_addendum_amount - rec.loan_amount})
					if rec.refund_remain_from == 'addendum':
						rec.loan_id.write({'addendum_plus':rec.loan_id.salary_refund - paid_slary_amount - rec.loan_amount})
        self.write(cr,uid,ids,{'state':'paid'})
        return True
