# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from random import choice
from string import digits

from odoo import api , fields, models,_
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit = "hr.employee"

    def _default_random_barcode(self):
        barcode = None
        while not barcode or self.env['hr.employee'].search([('barcode', '=', barcode)]):
            barcode = "".join(choice(digits) for i in range(8))
        return barcode

    state = fields.Selection([
        ('draft', 'Employ an initial'),
        ('experiment', 'In Experiment'),
        ('approved', 'In Service'),
        ('suspend','Temporary suspension'),
        ('refuse', 'Out of Service')], string='State', default='draft')

    religion = fields.Selection([
        ('muslim', 'Muslim'),
        ('christian', 'Christian'),
        ('other', 'Other')
        ], default="muslim")


    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", default=_default_random_barcode, copy=False)

    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_experiment(self):
        return self.write({'state': 'experiment'})

    @api.multi
    def action_approved(self):
        return self.write({'state': 'approved'})

    @api.multi
    def action_suspend(self):
        return self.write({'state': 'suspend'})

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refuse'})


class Job(models.Model):
    _inherit = 'hr.job'

    @api.model
    def _default_address_id(self):
        return self.env.user.company_id.partner_id

    name = fields.Char(string='Job Name', required=True, index=True ,readonly=True, states={'draft':[('readonly',False)]} ,translate=True)
    code = fields.Char(string="Job Code", readonly=True, states={'draft':[('readonly',False)]})
    categ_id = fields.Many2one("hr.job.category", string="Job Category", readonly=True, states={'draft':[('readonly',False)]})
    description = fields.Html(string="Job Description" ,translate=True, readonly=True, states={'draft':[('readonly',False)]})
    goals = fields.Html(string="Job Objectives", translate=True, readonly=True, states={'draft':[('readonly',False)]})
    tasks = fields.Html(string="Job Tasks", translate=True, readonly=True, states={'draft':[('readonly',False)]})
    personal_chars = fields.Html(string="Personal Attributes", translate=True, readonly=True, states={'draft':[('readonly',False)]})
    work_situations = fields.Html(string="Work Situations", translate=True,readonly=True, states={'draft':[('readonly',False)]})
    department_ids = fields.One2many('hr.job.department','job_id',string="Department", readonly=True, states={'draft':[('readonly',False)]})
    skills_ids = fields.Many2many("hr.skills", string="Skills", readonly=True, states={'draft':[('readonly',False)]})
    degree_ids = fields.Many2many("hr.job.degree", string="Degrees", readonly=True, states={'draft':[('readonly',False)]})
    general_experience = fields.Float(string="General Experience", readonly=True, states={'draft':[('readonly',False)]})
    specialize_experience = fields.Float(string="Specialized Experience", readonly=True, states={'draft':[('readonly',False)]})
    lang_ids = fields.One2many("hr.job.lang", "job_id" ,string="Languages", readonly=True, states={'draft':[('readonly',False)]})
    next_job_id = fields.Many2one("hr.job", string="Parent Job", readonly=True, states={'draft':[('readonly',False)]})
    margin = fields.Float(string="Default Time Margin", readonly=True, states={'draft':[('readonly',False)]})
    approved_date = fields.Date(string="Approved Date", readonly=True)
    approved_user_id = fields.Many2one("res.users", string="Approved User", readonly=True)
    address_id = fields.Many2one('res.partner', "Job Location", default=_default_address_id,
        states={'approved':[('readonly',True)]},
        help="Address where employees are working")
    user_id = fields.Many2one('res.users', "Recruitment Responsible", track_visibility='onchange' ,readonly=True, states={'draft':[('readonly',False)]})
    hr_responsible_id = fields.Many2one('res.users', "HR Responsible", track_visibility='onchange',
        help="Person responsible of validating the employee's contracts.", readonly=True, states={'draft':[('readonly',False)]})
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, states={'draft':[('readonly',False)]})
    sequence = fields.Integer(string="Sequence", readonly=True, states={'draft':[('readonly',False)]})
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('cancel', 'Cancelled'),
            ('merge', 'Merged')], string='Status',readonly=True, required=True, track_visibility='always', default='draft')
    expected_employees = fields.Integer(compute=False, string='Plan Number', required=True, default=1, track_visibility='onchange')
    no_of_employee = fields.Integer(compute='_compute_employees', string="Current Number", store=True,
        help='Number of employees currently occupying this job position.')
    no_of_recruitment = fields.Integer(compute='_compute_employees', string='Free Number', store=True)

    @api.depends('expected_employees', 'employee_ids.job_id', 'employee_ids.active')
    def _compute_employees(self):
        employee_data = self.env['hr.employee'].read_group([('job_id', 'in', self.ids)], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in employee_data)
        for job in self:
            job.no_of_employee = result.get(job.id, 0)
            job.no_of_recruitment = job.expected_employees - result.get(job.id, 0)
            
    @api.constrains('expected_employees','department_ids')
    def _check_plan(self):
        for job in self:
            if  int(sum(job.mapped('department_ids.no_of_plan'))) > job.expected_employees:
                raise ValidationError(_('Error! You cannot exceed Plan Number of job.'))

    @api.multi
    def action_approved(self):
        for record in self:
            self.approved_user_id = self.env.user.id
            self.approved_date =fields.Date.today()
            if self.tasks =="<p><br></p>" or self.goals =="<p><br></p>" or self.description =="<p><br></p>":
                raise ValidationError(_("You can't change state to approved without enter job tasks or job objectives or job description"))
        return self.write({'state': 'approved'})

    @api.multi
    def unlink(self):
        for record in self :
            if record.state != 'draft' and False :
                raise ValidationError(_('Deletion is forbbiden'))
        return super(Job, self).unlink()

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id:
            skills = self.categ_id.skill_ids
            return {'domain': {'skills_ids': [('id', 'in', skills.ids)]} }

    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})


class JobDepartment(models.Model):
    _name = "hr.job.department"

    job_id = fields.Many2one("hr.job", readonly=True, states={'draft':[('readonly',False)]})
    department_id = fields.Many2one('hr.department', string="Department", required=True, readonly=True, states={'draft':[('readonly',False)]})
    no_of_employee = fields.Integer(compute='_compute_employees', string="Current Number", store=True)
    no_of_plan = fields.Integer(string='Plan Number' , required=True)
    no_of_free = fields.Integer(compute='_compute_employees', string="Free Number", store=True)
    state = fields.Selection([
         ('draft', 'Draft'),
         ('approved', 'Approved'),
         ('cancel', 'Cancelled'),
         ('merge', 'Merged')
    ], related='job_id.state', string='Status', readonly=True, copy=False, store=True, default='draft')

    @api.multi
    @api.depends('no_of_plan', 'job_id.employee_ids.job_id', 'job_id.employee_ids.active')
    def _compute_employees(self):
        for job in self:
            emps = self.env['hr.employee'].search([('job_id', '=', job.job_id.id),
                 ('department_id', '=', job.department_id.id)])
            result = len(emps) 
            job.no_of_employee = result
            job.no_of_free = job.no_of_plan - result 
            
            
class Skills(models.Model):
    _name = "hr.skills"

    name = fields.Char(string="Name" ,required=True)
    color = fields.Integer('Color Index', default=5)


class HrJobLanguage(models.Model):
    _name = "hr.job.lang"
    _rec_name = 'lang_id'

    lang_id = fields.Many2one("res.lang" ,string = "Language" ,required=True)
    tpye = fields.Selection([
        ('read','Read') ,
        ('write','Write') ,
        ('listen','Listen')] ,string = "Type", required=True)
    level =fields.Selection([
        ('beginner','Beginner') ,
        ('intermediate','Intermediate') ,
        ('professional','Professional')] ,string = "Level", required=True)
    job_id = fields.Many2one("hr.job")


class JobCategory(models.Model):
    _name = "hr.job.category"

    name = fields.Char(string='Name', required=True, index=True,translate=True)
    skill_ids = fields.Many2many("hr.skills" ,string="Skills")
    job_ids = fields.One2many("hr.job", "categ_id", string="Jobs")

class JobDegree(models.Model):
    _name = "hr.job.degree"
    _description = "Degree of Job"

    name = fields.Char("Degree", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order when displaying a list of degrees.")
    amount = fields.Float(required=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the Degree of Job must be unique!'),
        ('seq_uniq', 'unique (sequence)', "Sequence name already exists!")
    ]
    
class Department(models.Model):
    _inherit = "hr.department"
    
    jobs_ids = fields.One2many('hr.job.department', 'department_id', string='Jobs')
    no_of_employee = fields.Integer(compute='_compute_employees', string="Current Number of Employees", store=True )
    no_of_job = fields.Integer(compute='_compute_jobs', string="Current Number of Employees", store=True )
    @api.depends('member_ids.department_id', 'member_ids.active')
    def _compute_employees(self):
        employee_data = self.env['hr.employee'].read_group([('department_id', 'in', self.ids)], ['department_id'], ['department_id'])
        result = dict((data['department_id'][0], data['department_id_count']) for data in employee_data)
        for department in self:
            department.no_of_employee = result.get(department.id, 0)
            
    @api.depends('jobs_ids.department_id', 'jobs_ids.state')
    def _compute_jobs(self):
        employee_data = self.env['hr.job.department'].read_group([('department_id', 'in', self.ids),('state', '=', 'approved')], ['department_id'], ['department_id'])
        result = dict((data['department_id'][0], data['department_id_count']) for data in employee_data)
        for department in self:
            department.no_of_job = result.get(department.id, 0)

    
