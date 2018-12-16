# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError


class RecruitmentPlan(models.Model):
    _name = "hr.recruitment.plan"
    _inherit = "mail.thread"
    _order = 'id desc'

    name = fields.Char(string="Name", required=True, readonly=True, states={'draft':[('readonly',False)]})
    date = fields.Date(string='Date', default=fields.Date.today() , required=True, readonly=True, states={'draft':[('readonly',False)]})
    need_start_date = fields.Date(string='Need Start Date', default=fields.Date.today() , required=True)
    need_end_date = fields.Date(string='Need End Date', default=fields.Date.today() , required=True)
    
    year = fields.Many2one("account.fiscalyear", string="Year", domain=[('state','=','draft')], readonly=True, states={'draft':[('readonly',False)]})
    

    budget = fields.Float(string="Budget" ,compute="calc_budget")
    plan_type = fields.Selection([
         ('em_plan','Emergency Plan') ,
         ('an_plan','Annual plan')], required=True, string="Plan Type" ,default="an_plan", readonly=True, states={'draft':[('readonly',False)]})
    state = fields.Selection([
        ('draft','Draft'),
        ('hr','Waiting Human Resources Manager'),
        ('finance','Waiting Finance Department'),
        ('executive','Waiting Executive manager'),
        ('done','Done'),
        ('refused', 'Refused')], string="State", default="draft", track_visibility='onchange')
        
    need_ids = fields.One2many("hr.recruitment.needs", 'plan_id', domain=[('state','in',('approve','done'))],  string="Needs", readonly=True, states={'draft':[('readonly',False)]})
    group_need_ids = fields.One2many("hr.recruitment.needs.grouping",'plan_id', domain=[('state','in',('approve','done'))] ,string="Needs By Job")
    notes = fields.Text()

    @api.multi
    def action_compute(self):
        for plan in self:
            plan.need_ids.action_compute()
        return True

    @api.multi
    def action_confirm(self):
        return self.write({'state': 'hr'})
        
    @api.multi
    def action_hr_confirm(self):
        return self.write({'state': 'finance'})
        
    @api.multi
    def action_finance_confirm(self):
        return self.write({'state': 'executive'})
        
    @api.multi
    def action_done(self):
        self.need_ids.action_done()
        self.group_need_ids.action_done()
        return self.write({'state': 'done'})

    @api.multi
    def action_refused(self):
        return self.write({'state': 'refused'})
                
    @api.multi
    def set_to_draft(self):
        return self.write({'state': 'draft'})

    @api.one
    @api.depends('need_ids')
    def calc_budget(self):
        budget_count = 0
        if self.need_ids:
            for record in self.need_ids:
                if record.state != 'refused':
                    budget_count += record.budget
        self.budget = budget_count
        
        
class RecruitmentNeedsGrouping(models.Model):
    _inherit = "mail.thread"
    _name = "hr.recruitment.needs.grouping"
    _rec_name = "job_id"
    _order = 'id desc'

    date = fields.Date(string='Date', default=fields.Date.today() , required=True, readonly=True, states={'draft':[('readonly',False)]})
    job_id = fields.Many2one("hr.job", string="Job", domain=[('state','=','approved')], readonly=True, states={'draft':[('readonly',False)]})
    needs_ids = fields.One2many('hr.recruitment.needs', 'grouping_id', string='Needs')
    plan_id = fields.Many2one('hr.recruitment.plan', string="Plan", readonly=True, states={'draft':[('readonly',False)]})
    state = fields.Selection([
            ('draft','Draft') ,
            ('confirm','Confirm'),
            ('approve','Approve'),
            ('done','Done'),
            ('refused', 'Refused')] , string="State", default="draft" ,track_visibility='onchange')
    
    need = fields.Integer(compute="_compute_need" ,string="Need" )
    approve = fields.Integer(compute="_compute_need", string="Approved")
    budget = fields.Float(compute="_compute_need" ,string="Budget")
    notes = fields.Text()

    j_type = fields.Selection([
        ('educational','Educational') ,
        ('general','General Administration')], related='job_id.j_type', string="Type", default="general" )
    

    @api.one
    @api.depends('needs_ids')
    def _compute_need(self):
        need_group = 0
        approve_group = 0
        budget_group = 0.0
        if self.needs_ids:
            for record in self.needs_ids:
                if record.state != 'refused':
                    need_group += record.need
                    approve_group += record.approve
                    budget_group += record.budget
        self.need = need_group
        self.approve = approve_group
        self.budget = budget_group
        
            
    @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'approve'})
        
    @api.multi
    def action_refused(self):
        return self.write({'state': 'refused'})
                
    @api.multi
    def set_to_draft(self):
        return self.write({'state': 'draft'})
        
    @api.multi
    def action_done(self):
        return self.write({'state': 'done'})
        

class RecruitmentNeeds(models.Model):
    _inherit = "mail.thread"
    _name = "hr.recruitment.needs"
    _rec_name = "department_id"
    _order = 'id desc'

    department_id = fields.Many2one("hr.department", string="Department",readonly=True, states={'draft':[('readonly',False)]})
    date = fields.Date(string='Date', default=fields.Date.today() , required=True, readonly=True, states={'draft':[('readonly',False)]})
    job_id = fields.Many2one("hr.job", string="Job", domain=[('state','=','approved')], readonly=True, states={'draft':[('readonly',False)]})
    plan_id = fields.Many2one('hr.recruitment.plan', string="Plan", readonly=True, states={'draft':[('readonly',False)]})
    grouping_id = fields.Many2one('hr.recruitment.needs.grouping', string="Grouping", readonly=True, states={'draft':[('readonly',False)]})
    need = fields.Integer(string="Need", required=True, default=1, readonly=True, states={'draft':[('readonly',False)]})
    month = fields.Integer(string="Month", required=True, default=12)
    approve = fields.Integer(string="Approved", required=True, states={'done':[('readonly',True)]}, track_visibility='onchange')
    salary = fields.Float(string="Salary", states={'done':[('readonly',True)]})
    budget = fields.Float(compute="_compute_budget", string="Budget")
    need_type = fields.Selection([
        ('new','New Need'),
        ('exist','Existing Job')] ,string="Need Type" ,default="exist",required=True, readonly=True, states={'draft':[('readonly',False)]})
    job_name = fields.Char(string="Job Name", readonly=True, states={'draft':[('readonly',False)]})
    duty = fields.Html(string="Job Responsibilities", readonly=True, states={'draft':[('readonly',False)]})
    description = fields.Html(string="Job Description", readonly=True, states={'draft':[('readonly',False)]})
    goals = fields.Html(string="Job Goals", readonly=True, states={'draft':[('readonly',False)]})
    missions = fields.Html(string="Job Missions", readonly=True, states={'draft':[('readonly',False)]})
    user_id = fields.Many2one("res.users" , string="Applicant" ,readonly=True)
    state = fields.Selection([
            ('draft','Draft') ,
            ('confirm','Confirm'),
            ('approve','Approve'),
            ('done','Done'),
            ('refused', 'Refused')], string="State", default="draft" ,track_visibility='onchange')
    notes = fields.Text()

    j_type = fields.Selection([
        ('educational','Educational') ,
        ('general','General Administration')], related='department_id.j_type', string="Type", default="general" )
    

        
    @api.multi
    @api.depends('salary', 'approve', 'month')
    def _compute_budget(self):
        budget = 0.0
        for record in self:
            record.budget = record.salary *  record.approve * record.month
          
            
    @api.onchange('need')
    def onchange_need(self):
        self.approve = self.need

    @api.multi
    def _compute_rule(self, rule,  degree_id):
 
        if rule.amount_select == 'fix':
            return rule.amount_fix
        elif rule.amount_select == 'levels':
            fix_amount = 0.0
            if rule.salary_amount_ids:
                record = self.env['hr.salary.amount'].search([('salary_rule_id','=',rule.id),
                    ('level_id','=',degree_id.level_id.id)])
                fix_amount = record.amount
            else:
                fix_amount = degree_id.level_id.amount
            return fix_amount
        elif rule.amount_select == 'grades':
            fix_amount = 0.0
            if rule.salary_amount_ids:
                record = self.env['hr.salary.amount'].search([('salary_rule_id','=',rule.id),
                    ('grade_id','=',degree_id.parent_id.id)])
                fix_amount = record.amount
            else:
                fix_amoun =degree_id.parent_id.amount
                return fix_amoun
        elif rule.amount_select == 'degrees':
            fix_amount = 0.0
            if rule.salary_amount_ids:
                record = self.env['hr.salary.amount'].search([('salary_rule_id','=',rule.id),
                        ('degree_id','=',degree_id.id)])
                fix_amount = record.amount
            else:
                fix_amount = degree_id.amount
            return fix_amount
        elif rule.amount_select == 'percentage':
            fix_amount = 0.0
            for x in rule.amount_percentage_base:
                if x.rule_type == 'allowance':
                    fix_amount +=  self._compute_rule(x, degree_id)
                elif x.rule_type == 'deduction':
                    fix_amount -= self._compute_rule(x, degree_id)
            return fix_amount
        else:
            return 0.0
            
                
    @api.multi
    def action_compute(self):
        for rec in self:
            salary = 0.0
            if rec.job_id.grade_id:
                grade_id = rec.job_id.grade_id
                degree_id = self.env['hr.payroll.structure'].search([('sequence', '=', 1), 
                    ('parent_id', '=', grade_id.id)], limit=1)
                if degree_id:
                    for rule in grade_id.structure_id.rule_ids:
                        if rule.rule_type == 'allowance' and rule.type == 'public':
                            salary += self._compute_rule(rule, degree_id)
            rec.salary = salary
        return True
        
        
    @api.multi
    def action_confirm(self):
        self.user_id = self.env.user.id
        if self.need_type =='new':
            if self.duty =="<p><br></p>" or self.goals =="<p><br></p>" or self.description =="<p><br></p>" or self.missions =="<p><br></p>":
                raise ValidationError(_("You can't change state to confirm without enter job description or job goals or job missions or job responsibilities"))
            if  not self.job_id:
                res = {
                    'name': self.job_name,
                    'tasks': self.missions,
                    'description': self.description,
                    'goals': self.goals, 
                }
                job_id = self.env['hr.job'].create(res)
                self.write({'job_id': job_id.id})
               
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'approve'})
        
    @api.multi
    def action_refused(self):
        return self.write({'state': 'refused'})
                
    @api.multi
    def set_to_draft(self):
        return self.write({'state': 'draft'})
        
    @api.multi
    def action_done(self):
        for need in self:
            need.job_id.write({'expected_employees': need.job_id.expected_employees + need.approve})
            needs = self.env['hr.job.department'].search([('job_id', '=', need.job_id.id),
                ('department_id', '=', need.department_id.id)])
            if not needs:
                needs = self.env['hr.job.department'].create({
                    'job_id': need.job_id.id,
                    'department_id': need.department_id.id,
                    'no_of_plan': need.approve
                 })
            needs.write({'no_of_plan': needs.no_of_plan + need.approve})
        return self.write({'state': 'done'})
        
class Applicant(models.Model) :
    _inherit = "hr.applicant"

    gender = fields.Selection([
        ('male','Male') ,
        ('female','Female')] , string = "Gender",default = "male")
    marital = fields.Selection([
        ('single','Single') ,
        ('married','Married') ,
        ('widower','Widower') ,
        ('divorced','Divorced')] , string = "Marital")
    country_id = fields.Many2one("res.country" , string = "Nationality")
    Official_time = fields.Many2one("resource.calendar" , string = "Official Time")
    skills_ids = fields.Many2many("hr.skills" , string = "Skills")
    qualified_year = fields.Date(string = "Graduation Year")
    score = fields.Selection([
            ('excellent','Excellent'),
            ('vgood','Very Good'),
            ('good','Good'),
            ('acceptable','Acceptable'),
            ])
    institute = fields.Char(string = "Institute")
    general_experience = fields.Float(string="General Experience")
    specialize_experience = fields.Float(string = "Specialize Experience")
    date_of_Birth= fields.Date('Date of Birth')
    address = fields.Char(string = "Address")
    last_salary= fields.Float(String="Last Salary")
    type_of_target = fields.Selection([
        ('male','Arenas of Male') ,
        ('female','Schools Of Female')] , string = "Targeted",default = "male")
        


    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            else :
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({
                    'name': applicant.partner_name or contact_name,
                    'job_id': applicant.job_id.id,
                    'address_home_id': address_id,
                    'department_id': applicant.department_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                            and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.phone or False,
                    'gender': applicant.gender,
                    'marital' : applicant.marital,
                    'country_id': applicant.country_id and applicant.country_id.id,
                    'birthday': applicant.date_of_Birth
                    }
                    )
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window
        
