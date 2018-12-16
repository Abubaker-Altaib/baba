# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from odoo import api, fields, models
from odoo.osv import osv

from odoo.tools.translate import _
from odoo import netsvc

#----------------------------------------
#loan names
#----------------------------------------

class hr_loan(models.Model):
    _name = "hr.loan"
    _description = "Loan configuration"

    @api.model
    def _get_company_ids(self):
        return [self.env.user.company_id.id]
    
    name = fields.Char(string="Name", size=50 , required= True,readonly= True,states={'draft':[('readonly',False)]},translate=True)
    loan_type = fields.Selection([('amount','whole Amount'),('installment','In Installment'),],'Refund', default ='installment' , required= True,readonly= True,states={'draft':[('readonly',False)]})
    installment_type = fields.Selection([('fixed','Fixed Price'),('salary','Based on Salary')],'Loan Amount',default='fixed', required= True,readonly= True,states={'draft':[('readonly',False)]})
    refund_from =fields.Selection([('salary','Salary'),('addendum','Addendum'),('both' ,'Salary and Addendum')],'Refund From', default='salary',readonly= True,states={'draft':[('readonly',False)]})
    loan_account_id =fields.Many2one('account.account',
                string="Loan Account",
                help="This account will be used for this loan",readonly= True,
                states={'draft':[('readonly',False)]})
    
    addendum_ids = fields.Many2many('hr.salary.rule', 'loan_salary_rel', 'loan_id', 'salary_rule_id','Addendum/s', 
                                      help="Addendums Related To This Loan.",readonly= True,states={'draft':[('readonly',False)]},)
    comments =fields.Text(string="Comments")
    active = fields.Boolean(string='Active',readonly= True,states={'draft':[('readonly',False)]} , default=lambda *a: 1)
    change_defult = fields.Boolean(string='Change Defult',readonly= True,states={'draft':[('readonly',False)]})
    code = fields.Char(string='Code', size=64,readonly= True,states={'draft':[('readonly',False)]})
    installment_no = fields.Integer(string="No of Salary Installments",default=1 , readonly= True,states={'draft':[('readonly',False)]},)
    company_ids = fields.Many2many('res.company', 'loan_company_rel', 'loan_id', 'company_id', 'Company', default=_get_company_ids,
                                      help="companys related to this loan.",readonly= True,states={'draft':[('readonly',False)]},)
    amount = fields.Float(string="Amount", digits=(18,2) ,readonly= True,states={'draft':[('readonly',False)]})
    factor =fields.Float(string="Factor", digits=(18,2) ,readonly= True,states={'draft':[('readonly',False)]})
    salary_rule_id =fields.Many2one('hr.salary.rule', 'Salary Rule', readonly= True,states={'draft':[('readonly',False)]})
    loan_limit =fields.Selection([('one','Once'),('unlimit','Unlimit'),],'Loan Limit', required= True, default='unlimit',readonly= True,states={'draft':[('readonly',False)]})
    year_employment =fields.Integer(string="Years of Employment",readonly= True,states={'draft':[('readonly',False)]})
    allow_interference = fields.Boolean(string='Allow Interference',readonly= True,states={'draft':[('readonly',False)]})
    job_ids = fields.Many2many('hr.job', 'loan_job_rel','loan_id','job_id','Job Position',readonly= True,states={'draft':[('readonly',False)]})  
    
    state=fields.Selection([('draft','Draft'),('confirmed','Confirmed'),
                              ('approved','Approved'),('cancel','Cancel')],"State",readonly= True,default='draft' , states={'draft':[('readonly',False)]})
    change_installment_no = fields.Boolean(string='Change Installment No',readonly= True,states={'draft':[('readonly',False)]})
    addendum_percentage = fields.Float(string='Addendum Percentage',readonly= True,states={'draft':[('readonly',False)]})
    adden_percentage_from =fields.Selection([('loan','Loan'),('addendum','Addendum'),],
        readonly= True,states={'draft':[('readonly',False)]})
    addendum_install_no = fields.Integer(string='No Of Addendum Installments' , default = 1)
    stop_loan = fields.Boolean(string="Stop Loan")
    times_stop_loan =fields.Integer(string="Times of Stop Loan",readonly= True,
        help='Number of times of loan suspend',states={'draft':[('readonly',False)]})
    months_stop_loan =fields.Integer(string="Months of Stop Loan",readonly= True,
        help='Number of months of suspension at a time',states={'draft':[('readonly',False)]})
    after_payment_time = fields.Float('Next Loan Request After (months)',help="Time Needed after payment to request a new loan")
    loan_journal_id = fields.Many2one('account.journal','Journal For Loan Request',readonly= True,states={'draft':[('readonly',False)]}, domain="[('type', '=', 'purchase')]")
    loan_journal_payment_id = fields.Many2one('account.journal','Journal For Loan Payment',readonly= True,states={'draft':[('readonly',False)]}, domain="[('type', '=', 'sale')]")


    def set_to_draft(self):
        self.write({'state': 'draft'})
        return True

    def confirmed(self):
        self.write({'state': 'confirmed'})
        return True    

    def approved(self):
        self.write({'state': 'approved'})
        return True       
        
    def cancel(self):
        self.write({'state': 'cancel'})
        return True    



    # def unlink(self, cr, uid, ids, context=None):
    #     employee_loan_pool = self.pool.get('hr.employee.loan')
    #     employee_loan_ids = employee_loan_pool.search(cr, uid, [('loan_id','in',ids)], context=context)
        
    #     loans_ids = self.read(cr, uid, ids, ['state'], context=context)
	   #  unlink_ids = []
	   #  for loan in loans_ids:
	   #     if loan['state'] in ['draft']:
	   #     unlink_ids.append(loan['id'])
	   #  else:
	   #     raise osv.except_osv(_('Invalid action !'), _('Can not delete the Approved Loans '))
	   #  if employee_loan_ids :
    #         raise osv.except_osv(_('Warning!'),_('You cannot delete this loan which is assign to employees'))
    #     return super(hr_loan, self).unlink(cr, uid, ids, context)

    #can not delete loan if state != draft or loan is used by employee in hr.loan.employee
    @api.multi
    def unlink(self):
        for loan in self:
            loan_request_ids = self.env['hr.loan.request'].search([('loan_id','=',loan.id)])

            if loan_request_ids :
                raise ValidationError(_('Can not  delete loan which is assign to employees'))
            if loan.state != 'draft':
                raise ValidationError(_('Can not  delete loan which is not in draft '))
        return super(hr_loan, self).unlink()

    '''
    _defaults = {
        'active' : lambda *a: 1,
        'remission_type': 'no',
        'installment_no':1,
        'loan_type' :'installment',
        'installment_type':'fixed',
        'loan_limit' :'unlimit',
        'addendum_install_no':1,
        'refund_from': 'salary',
		'state': 'draft',
    }
    '''

    _sql_constraints = [
       ('code_uniqe', 'unique (code)', ' You Can Not Have Two Loan Configuration Records With The Same Code !'),
       ('name_uniqe', 'unique (name)', ' You Can Not Have Two Loan Configuration Records With The Same name !'),
       ('installment_no_check', 'CHECK (installment_no > 0)', "The number of installment should be greater than or equal one !"),
       ('addendum_install_no_check', 'CHECK (addendum_install_no > 0)', "The number of installments should be greater than or equal one !"),
       ('amount_check', "CHECK (not(installment_type = 'fixed' and amount <= 0) )", "Loan amount should be greater than Zero!"),
       ('year_employment_check', 'CHECK (year_employment >= 0)', "years of employment should be greater than or equal Zero!"),
    ] 

#----------------------------------------
#Add loan policy to the company
#----------------------------------------

# class res_config_settings_inherit(models.TransientModel):

#     #_inherit = 'hr.config.settings'
#     _inherit = 'res.config.settings'

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    max_employee = fields.Float(string='Max Percentage for Total Loans Per Employee')
    max_department = fields.Float(string='Max Percentage for Total Loans Per Department')
    allowed_number = fields.Integer(string='Allowed Number',help='Number of loans per employee , if its 0 thats mean no limit for number of loans')
    # group_tax = fields.Boolean("Use Taxes" , default=False)
    salary_rule_id = fields.Many2one('hr.salary.rule','Salary')
    restrict_reject = fields.Boolean(string='Restrict Reject', default=False , 
                                 help='Restrict rejection of Loan Request \
                                        if the request does not meet all the conditions')



    @api.model    
    def create(self, vals):
        """Method that overwrites create method and check settings fields and change their values in
            res.company
        @param vals: dictionary contains the entered values 
        @return: the new record
        """

        res=super(ResConfigSettings, self).create(vals)
       
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id

        company.write({'max_employee':vals['max_employee'],'max_department':vals['max_department'],
                     'allowed_number':vals['allowed_number'],'salary_rule_id':vals['salary_rule_id'],
                     'restrict_reject' : vals['restrict_reject']})
        return res


    @api.multi
    def write(self, vals):
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id
        res = super(ResConfigSettings, self).write(vals)

        for rec in self :

            max_employee = rec.max_employee
            if 'max_employee' in vals :
                max_employee = vals['max_employee']
           
            max_department = rec.max_department
            if 'max_department' in vals :
                max_department = vals['max_department']

               
            allowed_number = rec.allowed_number    
            if 'allowed_number' in vals :
                allowed_number = vals['allowed_number']

            # group_tax = rec.group_tax    
            # if 'group_tax' in vals :
            #     group_tax = vals['group_tax']

            salary_rule_id = rec.salary_rule_id.id
            if 'salary_rule_id' in vals:
                salary_rule_id=vals['salary_rule_id']

            restrict_reject = rec.restrict_reject
            if 'restrict_reject' in vals :
                restrict_reject = vals['restrict_reject']

        

            company.write({'max_employee':max_employee,'max_department':max_department,
                  'allowed_number':allowed_number , 'salary_rule_id':salary_rule_id, 
                  'restrict_reject' : restrict_reject })
        
    #     return res


    @api.model
    def default_get(self, fields):

        res = super(ResConfigSettings, self).default_get(fields)
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id

        max_employee = company.max_employee
        max_department = company.max_department
        allowed_number = company.allowed_number
        # group_tax = company.group_tax
        salary_rule_id = company.salary_rule_id.id
        restrict_reject = company.restrict_reject

      
        res.update({'max_employee': max_employee , 'max_department':max_department,
                     'allowed_number':allowed_number , 'salary_rule_id':salary_rule_id, 
                     'restrict_reject' : restrict_reject })
        return res

    
    # @api.model
    # def default_get(self, fields):
    #     res = super(ResConfigSettings, self).default_get(fields)
    #     self.env.cr.execute("""
    #                 SELECT max_employee,max_department,allowed_number,group_tax
    #                 FROM res_config_settings
    #                 ORDER BY id DESC
    #                 LIMIT 1 """,)
    #     result = self.env.cr.fetchall()[0] or 0.0
    #     old_max_employee = result[0]
    #     old_max_department = result[1]
    #     old_allowed_number = result[2]
    #     old_group_tax = result[3]

    #     res.update({'max_employee': old_max_employee , 'max_department':old_max_department,
    #                  'allowed_number':old_allowed_number,'group_tax':old_group_tax})
    #     return res
