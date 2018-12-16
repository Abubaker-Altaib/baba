# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################



#from odoo.osv import  osv,orm
from odoo import api, fields, models , exceptions,_
import time
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import math
#from dateutil import relativedelta
from dateutil.relativedelta import relativedelta

#----------------------------------------
# Loan Request
#----------------------------------------
class HrLoanRequest(models.Model):

    _name = "hr.loan.request"

    _description = "Loan Request"
    _order = "id desc"


    def name_get(self):
        result = []
        for line in self:
            name = line.loan_id.name+"/"+str(line.start_date)
            result.append((line.id, name))
        return result


    def write(self,vals):
        '''
        Update Loan Amount if fixed or based on salary,
        Update Total installment and Installment Amount
        '''
        if vals.get('loan_id'):
            loan_id = self.env['hr.loan'].browse(vals.get('loan_id'))
        else:
            loan_id = self.loan_id
        if loan_id.installment_type == 'fixed':
            vals.update({'loan_amount' :loan_id.amount})
        else:

            if vals.get('employee_id'):
                employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            else:
                employee = self.employee_id
            contract = employee.contract_id
            rule = loan_id.salary_rule_id
            rule_amount = self.env['hr.payslip'].compute_rule_custom(rule.id,contract.id,employee.id)
            vals.update({'loan_amount' : rule_amount*loan_id.factor})
        vals.update({'total_installment' : loan_id.installment_no})
        if vals.get('total_installment') > 0:
            vals.update({'installment_amount' : vals.get('loan_amount') / vals.get('total_installment')})
        return super(HrLoanRequest,self).write(vals)


    @api.model
    def create(self,vals):
        '''
        Update Loan Amount if fixed or based on salary,
        Update Total installment and Installment Amount
        '''
        loan_id = self.env['hr.loan'].browse(vals.get('loan_id'))
        if loan_id.installment_type == 'fixed':
            vals.update({'loan_amount' :loan_id.amount})
        else:
            employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            contract = employee.contract_id
            rule = loan_id.salary_rule_id
            rule_amount = self.env['hr.payslip'].compute_rule_custom(rule.id,contract.id,employee.id)
            vals.update({'loan_amount' : rule_amount*loan_id.factor})
        
        vals.update({'total_installment' : loan_id.installment_no})
        if vals.get('total_installment') > 0:
            vals.update({'installment_amount' : vals.get('loan_amount') / vals.get('total_installment')})
        return super(HrLoanRequest,self).create(vals)

    @api.multi
    def unlink(self):
        if self.filtered(lambda line: line.state != 'draft' ):
            raise UserError(_("Cannot Delete un Draft Request!!"))
        super(HrLoanRequest, self).unlink()

    code = fields.Char(related='employee_id.user_id.partner_id.code',string='Code')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department',related='employee_id.department_id', string='Department')
    loan_id = fields.Many2one('hr.loan', string='Loan')
    loan_amount = fields.Float(string='Loan Amount')
    advance_amount = fields.Float(compute='_compute_loan_amounts',string='Advance Amount')
    remain_installment = fields.Float(compute='_compute_loan_amounts',string='Remain Amount')
    total_installment = fields.Integer(string='Total Installment')
    installment_amount = fields.Float(string='Installment Amount')
    # refund_from = fields.Float(string='Refund From')
    # remission_amount = fields.Float(string='Remission Amount')
    #guarantor_id = fields.Many2one('hr.employee', string='Guarantor')
    #guarantor = fields.Boolean(related="loan_id.guarantor", string="Need Guarantor")
    #validation = fields.Boolean(related="loan_id.validation",string="Double Validation")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    acc_number = fields.Many2one('account.voucher',string='Voucher', copy=False)
    acc_remission_no = fields.Many2one('account.voucher',string='Remission Voucher No')
    loan_arc_ids = fields.One2many('hr.loan.archive','loan_request_id',string='Installment Loan')
    comments = fields.Text()

    state = fields.Selection([('draft','Draft'),
    						  ('dept_approve','Waiting for Department Manager Recommendation'),
    						  ('direct_approve','Waiting for Director Manager Recommendation'),
                              ('general_approve','Waiting for General Manager Approve'),
                              ('hr_approve','Waiting for Human Resources Approve'),
                              ('transfered','Waiting for Accounting Management'),
                              ('rejected','Rejected'),
 							  ('paid','Paid'),
                              ('suspend','Suspend'),
 							  ('done','Done')], string='Status', copy=False, track_visibility='onchange', default='draft')

    satisfy_condition = fields.Boolean(default = False , help="If the Employee satisfy Loan conditions or Not" )
    
    # workflow functions for Loan Request
    def action_loan_draft(self):
        self.comments = False
        self.write({'state':'draft'})

    def action_loan_request(self):
        reject_reason = self.request_loan_check()
        if reject_reason != True:
            self.comments = reject_reason
            config_setting = self.env['res.company'].search([('id','=',self.employee_id.company_id.id)],
                                                                order='id desc',limit=1)
            # if the policy of company automatic reject the request or not
            if not config_setting.restrict_reject:
                self.write({'state':'rejected'})
            else:
                self.write({'state':'dept_approve','satisfy_condition':False})
        else:
            self.write({'state':'dept_approve','satisfy_condition':True})

    def action_loan_dept_approve(self):
        self.write({'state':'direct_approve'})

    def action_loan_direct_approve(self):
        self.write({'state':'general_approve'})

    def action_loan_general_approve(self):
        self.write({'state':'hr_approve'})

    def action_loan_hr_approve(self):
        self.create_loan_voucher()
        self.write({'state':'transfered'})

    def action_loan_suspend(self):
    	self.write({'state':'suspend'})

    def action_loan_reject(self):
        if not self.comments:
            raise UserError(_("Please Enter Reject Reson in Note before cancelling"))
        self.write({'state':'rejected'})

    # end of functions for Loan Request 

    @api.multi
    @api.depends('loan_id')
    def _compute_loan_amounts(self):
        '''
        Calculate Remain Amount and Advance Amount
        '''
        for line in self:
            if len(line.loan_arc_ids) > 0:
                paid_archive = self.env['hr.loan.archive'].search([('loan_request_id','=',line.id),('state','=','paid')])
                advance_amount = sum([g.loan_amount for g in paid_archive])
                draft_archive = self.env['hr.loan.archive'].search([('loan_request_id','=',line.id),('state','=','draft')])
                remain_installment = sum([g.loan_amount for g in draft_archive])

                if not draft_archive and line.state != 'done':
                    line.write({'state':'done'}) 

                line.update({
                             'advance_amount':round(advance_amount,2),
                             'remain_installment':round(remain_installment,2)})

    ################Fetching Loan Type Data##########################
    @api.onchange('loan_id','employee_id')
    def onchange_loan_id(self):
        '''
        Calculate Loan Amount, Total Installment and Installment Amount
        '''
        if self.loan_id and self.employee_id:
            if self.loan_id.installment_type == 'fixed':
                self.loan_amount = self.loan_id.amount
            #############Loan Amount Based On Salary #######################
            else:
                if not self.employee_id.contract_id or self.employee_id.contract_id.state != 'open' and \
                 self.state == 'draft':
                    raise UserError(_('Employee Has No Running Contract'))
                contract = self.employee_id.contract_id
                rule = self.loan_id.salary_rule_id
                # this line written to test 'compute_rule_custom' function
                rule_amount = self.env['hr.payslip'].compute_rule_custom(rule.id,contract.id,self.employee_id.id)
                # rule_amount = self.env['hr.payslip'].compute_rule_amount(rule,contract,self.employee_id.id)
                self.loan_amount = rule_amount*self.loan_id.factor
            self.total_installment = self.loan_id.installment_no
            if self.total_installment > 0:
                self.installment_amount = self.loan_amount / self.total_installment



    def request_loan_check(self):

        if datetime.strptime(self.start_date, '%Y-%m-%d') > datetime.today():
            raise UserError(_("Loan Request Date is Bigger than Current Date"))

        # Loan Not Allowed for The Jop Position of Employee
        for job in self.loan_id.job_ids :
            if self.employee_id.job_id.id !=job.id:
                return _("Loan Not Allowed For This Employee's Job Position")
                
        
        # Loan Limit is Once and Already Taken
        if self.loan_id.loan_limit == 'one':
        	all_loan_ids = self.env['hr.loan.request'].search([('employee_id','=',self.employee_id.id),
                                                                ('loan_id','=',self.loan_id.id),
                                                                ('state','not in',['draft','rejected'])])
        	if len(all_loan_ids) > 0:
        		return _("Loan Limit is Once and Already Taken")

        # Interference Between same Loan Not Allowed
        if self.loan_id.loan_limit == 'unlimit' and  not self.loan_id.allow_interference:
            all_loan_ids = self.env['hr.loan.request'].search([('employee_id','=',self.employee_id.id),
                                                                ('loan_id','=',self.loan_id.id),
                                                                ('state','not in',['draft','rejected','done'])])
            if len(all_loan_ids) > 0:
                return _("Interference Between same Loan Not Allowed")

        # Employment years for Employee Not Fit employment Years for The Loan
        emp_loan_year = datetime.strptime(self.start_date, '%Y-%m-%d').year
        if self.loan_id.year_employment > 0:
            emp_contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),
                                                                ('state','=','open')],order='date_start asc',limit=1)
            if emp_contract.id:
                emp_contract_year = datetime.strptime(emp_contract.date_start, '%Y-%m-%d').year
                if int(emp_loan_year) - int(emp_contract_year) < self.loan_id.year_employment :
                    return _("Employment years for Employee Not Fit employment Years for The Loan")
            else:
                return _("The Employee has no running contract")

        # Pension Reached Before Fininshig Loan Installments
        config_setting = self.env['res.company'].search([('id','=',self.employee_id.company_id.id)],order='id desc',limit=1)
        if config_setting.id:
            if config_setting.age_pension > 0:
                if not self.employee_id.birthday:
                    return _("You must enter employee birth date")
                emp_age = datetime.strptime(self.employee_id.birthday, '%Y-%m-%d').year
                emp_remain_pension = config_setting.age_pension - (int(emp_loan_year) - int(emp_age))
                if emp_remain_pension < self.loan_id.installment_no / 12 :
                    return _("Pension Reached Before Finishing Loan Installments")

            # Max Employee Salary
            if config_setting.max_employee:
                if not config_setting.salary_rule_id:
                    return _("Please Choose A Salary To Be Used In Computation")
                employee_loans = self.search([('employee_id','=',self.employee_id.id),('state','=','paid')])
                if employee_loans:
                    total_installments_amount = sum([loan.installment_amount for loan in employee_loans])
                    max_amount = self.env['hr.payslip'].compute_rule_custom(config_setting.salary_rule_id.id,self.employee_id.contract_id.id,self.employee_id.id)
                    if max_amount:
                        max_amount+=self.installment_amount
                        max_amount*=(config_setting.max_employee/100)
                        if total_installments_amount>max_amount:
                            return _("Max Installments Amount Exceeded")
                    else:
                        return _("Please Review Payroll Configuration")

            # Exceed Allowed Number
            if config_setting.allowed_number:
                employee_loans = self.search([('employee_id','=',self.employee_id.id),('state','=','paid')])
                if employee_loans:
                    if len(employee_loans)>=config_setting.allowed_number:
                        return _("You've Exceeded The Allowed Number")

        # After Payment Time
        if self.loan_id.after_payment_time:
            archives = []
            loans = self.env['hr.loan.request'].search([('employee_id','=',self.employee_id.id),
                                                        ('loan_id','=',self.loan_id.id),('state','=','done')])
            for loan in loans:
                archives.extend(loan.loan_arc_ids.mapped(lambda r:(r.year,r.month)))
            if archives:
                last_installment = max(archives)
                last_installment_month = last_installment[1]
                last_installment_year = last_installment[0]
                allowed_month = 0
                allowed_year = 0
                if self.loan_id.after_payment_time+last_installment_month<=12:
                    allowed_month = self.loan_id.after_payment_time+last_installment_month
                    allowed_year = last_installment_year
                if self.loan_id.after_payment_time+last_installment_month>12:
                    allowed_year = last_installment_year+1
                    allowed_month = last_installment_month+self.loan_id.after_payment_time-12
                current_month = fields.Date.from_string(time.strftime('%Y-%m-%d')).month
                current_year = fields.Date.from_string(time.strftime('%Y-%m-%d')).year
                if (current_year,current_month)<(allowed_year,allowed_month):
                    return _("You Are Not Allowed To Take This Loan Yet")
            




        # else:
        #     raise UserError(_("Employee settings not configured"))
        # Total Loans Installments for The Employee Exceed Max Percentage
        # Total Loans Installments for The Department Exceed Max Percentage
        return True

    def create_loan_voucher(self):
        '''
        create employee loan voucher
        '''
        if not self.loan_id.loan_account_id.id:
            raise UserError(_("Please enter account loan for %s loan" % self.loan_id.name))
        # Voucher Data
        date = time.strftime('%Y-%m-%d')
        reference = 'HR/Loans/ '+" / "+str(date)
        partner_id = self.employee_id.user_id.partner_id.id or False
        account_id = self.employee_id.user_id.partner_id.property_account_payable_id.id or False
        journal_id = self.loan_id.loan_journal_id and self.loan_id.loan_journal_id.id or False
        currency_id_ebs = self.env['res.company'].search([('id','=',self.employee_id.company_id.id)]).currency_id.id
        user_id = self.env.user.id
        department_id = self.department_id.id
        company_id = self.employee_id.company_id.id
        if not account_id:
            raise UserError(_("The Partner has no payable account"))
        if not journal_id:
            raise UserError(_("This Loan has no journal, Please go to HR Loans"))
        voucher = {'date':date,
                   'account_date':date,
                   'reference':reference,
                   'partner_id':partner_id,
                   'journal_id':journal_id,
                   'currency_id_ebs':currency_id_ebs,
                   'state':'draft',
                   'user_id':user_id,
                   'department_id':department_id,
                   'company_id':company_id,
                   'account_id':account_id,
                   'voucher_type':'purchase',
                   'payment_type':'direct_payment',
                   'loan_request':self.id}
        print(">>>>>>>>>>>voucher :",voucher.get('loan_request',False))
        voucher_id = self.env['account.voucher'].create(voucher)

        lines = {'name':self.loan_id.name,
                 'account_id':self.loan_id.loan_account_id.id,
                 'account_analytic_id':self.department_id.analytic_account_id.id,
                 'price_unit':self.loan_amount,
                 'price_subtotal':self.loan_amount,
                 'voucher_id':voucher_id.id}
        voucher_line_id = self.env['account.voucher.line'].create(lines)
        self.acc_number = voucher_id.id

    def create_loan_archive(self):

        installment_no = self.total_installment
        month = datetime.strptime(self.start_date, '%Y-%m-%d').month
        year = datetime.strptime(self.start_date, '%Y-%m-%d').year

        archive_obj = self.env['hr.loan.archive']

        vals = {'employee_id':self.employee_id.id,
                'loan_request_id':self.id,
                'loan_amount':self.installment_amount,
                'month':month,
                'year':year,
                'state':'draft'}

        while installment_no > 0 :
            if installment_no == 1:
                loan_amount = self.loan_amount - (self.total_installment-1) * self.installment_amount
                vals.update({'loan_amount':loan_amount})

            archive_obj.create(vals)
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            installment_no-=1
            vals.update({'month':month,'year':year})

    def loan_request_paid(self):
        # Make Loan Request in 'paid' state and create Loan Archives
        self.state = 'paid'
        self.create_loan_archive()



class hr_loan_archive(models.Model):
    _name = "hr.loan.archive"
    _description = "Loan Archive"

    def name_get(self):
        result = []
        for line in self:
            name = line.loan_request_id.loan_id.name+"/"+str(line.month)+"-"+str(line.year)
            result.append((line.id, name))
        return result

    employee_id = fields.Many2one('hr.employee','Employee')
    month = fields.Integer('Month')
    year = fields.Integer('Year')
    loan_request_id = fields.Many2one('hr.loan.request',string='Loan Name')
    loan_amount = fields.Float('Loan Amount')

    state = fields.Selection([('draft','Draft'),
                              ('suspend','Suspend'),
                              ('delay','Delay'),
                              ('suspend_penalty','Suspension due to financial penalty'),
                              ('paid','Paid')], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.multi
    def unlink(self):
        raise UserError(_("Installments can not be deleted"))
        return super(hr_loan_archive,self).unlink()


class accountVoucher(models.Model):
    _inherit = 'account.voucher'

    loan_request = fields.Many2one('hr.loan.request', help='The requested Loan related to this Voucher')

    @api.multi
    def write(self,vals):
        rec = super(accountVoucher, self).write(vals)
        for line in self:
            if line.paid and line.loan_request :
                line.loan_request.loan_request_paid()
        return rec



#----------------------------------------
#loan suspend
#----------------------------------------
class hr_loan_suspend(models.Model):
    _name = "hr.loan.suspend"
    _description = "Suspended Loan"


    def name_get(self):
        result = []
        for line in self:
            if line.suspend_type == 'suspend':
                name = line.loan_id.loan_id.name
            else:
                name = line.loan_type_id.name

            name +="/"+str(line.start_date)+"-"+str(line.end_date)
            result.append((line.id, name))
        return result

    loan_id = fields.Many2one("hr.loan.request",'Loan')
    employee_id = fields.Many2one('hr.employee','Employee')
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    comments = fields.Text("Comments")
    state = fields.Selection([('draft','Draft'),
                              ('requested','Requested'),
                              ('approved','Approved'),
                              ('rejected','Rejected')], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    suspend_type = fields.Selection([('suspend','Suspend'),('delay','Delay')],'Suspend Type',default='suspend')
    loan_type_id = fields.Many2one('hr.loan','Loan Type')


    def check_stop_loan_request(self):
        months_stop_loan = self.loan_id.loan_id.months_stop_loan
        start_stop_loan = datetime.strptime(self.start_date, '%Y-%m-%d')
        end_stop_loan = datetime.strptime(self.end_date, '%Y-%m-%d')
        duration = (end_stop_loan - start_stop_loan).days

        if months_stop_loan < duration/30 :
            return "the Suspend Duration is bigger than allowed suspend duration"

        stop_loan = self.env['hr.loan.suspend'].search([('loan_id','=',self.loan_id.id),('state','in',['requested','approved'])])
        if len(stop_loan) >= self.loan_id.loan_id.times_stop_loan:
            return "The allowed Number of stop Loan to "+self.loan_id.loan_id.name+"/"+self.loan_id.start_date+" is Exceeded"
        arc_to_stop = self.env['hr.loan.archive'].search([('loan_request_id','=',self.loan_id.id),
                                                          ('state','=','draft'),
                                                          ('month','>=',start_stop_loan.month),
                                                          ('year','>=',start_stop_loan.year),
                                                          ('month','<=',end_stop_loan.month),
                                                          ('year','<=',end_stop_loan.year)])
        if not arc_to_stop:
            return "Can't find non Paid Installment in selected date range "

        return True

    def suspend_loan_request(self):
        for rec in self:
            if rec.suspend_type == 'suspend':
                reject_reson = self.check_stop_loan_request()
                if reject_reson == True:
                    self.write({'state':'requested'})
                else:
                    self.comments = reject_reson
                    self.write({'state':'rejected'})
            else:
                self.write({'state':'requested'})

    def suspend_loan_approve(self):
        start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
        stop_dates = []
        archive_obj = self.env['hr.loan.archive']
        while start_date < end_date:
            stop_dates.append((int(start_date.year),int(start_date.month)))
            start_date += relativedelta(months=1)

        if self.suspend_type == 'suspend':
            loan_archive = archive_obj.search([('loan_request_id','=',self.loan_id.id),('state','=','draft')])
        else:
            loan_archive = archive_obj.search([('loan_request_id.loan_id','=',self.loan_type_id.id),('state','=','draft')])
        last_arc = loan_archive[len(loan_archive)-1]

        month = last_arc.month
        year = last_arc.year
        for arc in loan_archive:
            if (arc.year,arc.month) in stop_dates:
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1

                archive_obj.create({'employee_id':arc.employee_id.id,
                                    'loan_request_id':arc.loan_request_id.id,
                                    'loan_amount':arc.loan_amount,
                                    'month':month,
                                    'year':year,
                                    'state':'draft'})
                if self.suspend_type =='suspend':
                    arc.write({'state':'suspend'})
                else:
                    arc.write({'state':'delay'})

        self.write({'state':'approved'})

    def suspend_loan_cancel(self):
        self.write({'state':'rejected'})

    def suspend_loan_draft(self):
        self.comments = False
        self.write({'state':'draft'})



    @api.onchange('suspend_type')
    def onchange_suspend_type(self):
        if self.suspend_type =='suspend':
            employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)])
            if employee:
                self.employee_id=employee.id
        else:
            self.employee_id=False






        
