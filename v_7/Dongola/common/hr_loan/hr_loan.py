# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc

#----------------------------------------
#loan names
#----------------------------------------

class hr_loan(osv.Model):
    _name = "hr.loan"
    _description = "Loan configuration"
    _columns = {
        'name' :fields.char("Name", size=50 , required= True,readonly= True,states={'draft':[('readonly',False)]}),
        'loan_type' :fields.selection([('amount','whole Amount'),
                                       ('installment','In Installment')
                                       ,],'Refund', required= True,readonly= True,states={'draft':[('readonly',False)]}),
        'installment_type':fields.selection([('fixed','Fixed Price'),
                                             ('salary','Based on Salary')],'Loan Amount', required= True,readonly= True,states={'draft':[('readonly',False)]}),
        'refund_from' :fields.selection([('salary','Salary'),
                                         ('addendum','Addendum'),
                                         ('both' ,'Salary and Addendum')],'Refund From', required= True,readonly= True,states={'draft':[('readonly',False)]}),
        'loan_account_id' :fields.property('account.account',type='many2one',relation='account.account',string="Loan Account",view_load=True,
        domain="[('user_type.report_type','=','expense'),('type','!=','view')]",help="This account will be used for this loan",readonly= True,states={'draft':[('readonly',False)]}),
        'addendum_ids' : fields.many2many('hr.allowance.deduction', 'loan_allow_ded_rel3', 'loan_id', 'allow_ded_id','Addendum/s', domain=[('name_type','=','allow'),('in_salary_sheet','=',False)],
                                          help="Addendums Related To This Loan.",readonly= True,states={'draft':[('readonly',False)]},),
        #'loan_journal_id': fields.property('account.journal',type='many2one',relation='account.journal',string="Loan Journal",view_load=True,
        #help="This journal will be used for this loan"),
        #'loan_account_analytic_id': fields.property('account.analytic.account',type='many2one',relation='account.journal',string="Analytic Account",     view_load=True  ,help="This analytic account will be used for this loan"),
        'comments':fields.text("Comments"),
        'active' : fields.boolean('Active',readonly= True,states={'draft':[('readonly',False)]}),
        'change_defult' : fields.boolean('Change Defult',readonly= True,states={'draft':[('readonly',False)]}),
        'code': fields.char('Code', size=64,readonly= True,states={'draft':[('readonly',False)]}),
        'installment_no' :fields.integer("No of Salary Installments",readonly= True,states={'draft':[('readonly',False)]},),
        'company_ids' : fields.many2many('res.company', 'loan_company_rel', 'loan_id', 'company_id', 'Company',
                                          help="companys related to this loan.",readonly= True,states={'draft':[('readonly',False)]},),
        'amount' :fields.float("Amount", digits=(18,2) ,readonly= True,states={'draft':[('readonly',False)]}),
        'factor' :fields.float("Factor", digits=(18,2) ,readonly= True,states={'draft':[('readonly',False)]}),
        'allowances_id' :fields.many2one('hr.allowance.deduction'  , 'Allowance' , domain=[('name_type','=','allow')],readonly= True,states={'draft':[('readonly',False)]}),#,('allowance_typ','=','3')
        'loan_limit' :fields.selection([('one','Once'),('unlimit','Unlimit'),],'Loan Limit', required= True,readonly= True,states={'draft':[('readonly',False)]}),
        'year_employment' :fields.integer("Years of Employment",readonly= True,states={'draft':[('readonly',False)]}),
        'allow_interference' : fields.boolean('Allow Interference',readonly= True,states={'draft':[('readonly',False)]}),
        'degree_ids': fields.many2many('hr.salary.degree', 'loan_degree_rel','loan_id','degree_id','Degrees',readonly= True,states={'draft':[('readonly',False)]}),

        'remission_type' :fields.selection([('no','No Remission'),('amount','Amount'),('percentage','Percentage'),],'Remission Type', required= True,readonly= True,states={'draft':[('readonly',False)]}),
        'loan_remission_account_id' :fields.property('account.account',type='many2one',relation='account.account',
						string="Remission Account",view_load=True, domain="[('type','in',('payable','receivable','other'))]",
						help="This account will be used to transfer the the amount of remission of the loan",readonly= True,states={'draft':[('readonly',False)]}),

        'remission' : fields.float('Remission Amount/percentage',readonly= True,states={'draft':[('readonly',False)]}),
		'state':fields.selection([('draft','Draft'),('confirmed','Confirmed'),
                                  ('approved','Approved'),('cancel','Cancel')],"State",readonly= True,states={'draft':[('readonly',False)]}),
        'change_installment_no': fields.boolean('Change Installment No',readonly= True,states={'draft':[('readonly',False)]}),
        'addendum_percentage': fields.float('Addendum Percentage',readonly= True,states={'draft':[('readonly',False)]}),
        'adden_percentage_from' :fields.selection([('loan','Loan'),('addendum','Addendum'),],'Addendum Percentage From', readonly= True,states={'draft':[('readonly',False)]}),
        'addendum_install_no' : fields.integer('No Of Addendum Installments'),

                }

    def set_to_draft(self, cr, uid, ids,context=None):
		"""
		Method that resets the workflow and change loan's state to 'draft'.

		@return: Boolean True
		"""
		self.write(cr, uid, ids, {'state': 'draft'},context=context)
		wf_service = netsvc.LocalService("workflow")
		for id in ids:
			wf_service.trg_delete(uid, 'hr.loan', id, cr)
			wf_service.trg_create(uid, 'hr.loan', id, cr)
		return True

    def unlink(self, cr, uid, ids, context=None):
        employee_loan_pool = self.pool.get('hr.employee.loan')
        employee_loan_ids = employee_loan_pool.search(cr, uid, [('loan_id','in',ids)], context=context)

        loans_ids = self.read(cr, uid, ids, ['state'], context=context)
	unlink_ids = []
	for loan in loans_ids:
	    if loan['state'] in ['draft']:
	       unlink_ids.append(loan['id'])
	    else:
	       raise osv.except_osv(_('Invalid action !'), _('Can not delete the Approved Loans '))
	if employee_loan_ids :
            raise osv.except_osv(_('Warning!'),_('You cannot delete this loan which is assign to employees'))
        return super(hr_loan, self).unlink(cr, uid, ids, context)
    
    _defaults = {
        'active' : lambda *a: 1,
        'remission_type': 'no',
        'installment_no':1,
        'addendum_install_no':1,
        'refund_from': 'salary',
		'state': 'draft',
                }
    _sql_constraints = [
       ('code_uniqe', 'unique (code)', ' You Can Not Have Two Loan Configuration Records With The Same Code !'),
       ('name_uniqe', 'unique (name)', ' You Can Not Have Two Loan Configuration Records With The Same name !'),
       ('installment_no_check', 'CHECK (installment_no > 0)', "The number of installment should be greater than or equal one !"),
       ('addendum_install_no_check', 'CHECK (addendum_install_no > 0)', "The number of installments should be greater than or equal one !"),
       ('amount_check', "CHECK (installment_type = 'fixed' and amount > 0)", "Loan amount should be greater than Zero!"),
       ('year_employment_check', 'CHECK (year_employment >= 0)', "years of employment should be greater than or equal Zero!"),
                 ] 

#----------------------------------------
#Add loan policy to the company
#----------------------------------------

class res_companyy(osv.Model):
    """Inherits res.company to add company's general conditions on the loans.
    """
    _inherit = "res.company"
    _columns = {
        'max_employee' :fields.float("Max Percentage for Total Loans Per Employee", digits=(18,2) ),
        'max_department' :fields.float("Max Percentage for Total Loans Per Department", digits=(18,2) ),
        'comments': fields.text("Comments"),
        'allowed_number' :fields.integer("Allowed Number",help='Number of loans per employee , if its 0 thats mean no limit for number of loans'),
    }

    _sql_constraints = [
       ('max_employee_check', 'CHECK (max_employee > 0)', "Max Percentage for employee should be greater than Zero!"),
       ('max_department_check', 'CHECK (max_department > 0)', "Max Percentage for Department should be greater than Zero!"),
       ('allowed_number_check', 'CHECK (allowed_number >= 0)', "Allowed number should be greater than or equal Zero!"),
   		  ]

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        raise osv.except_osv(_('Warning!'),_('You cannot duplicate company'))
        return super(res_company, self).copy(cr, uid, id, default, context=context)

