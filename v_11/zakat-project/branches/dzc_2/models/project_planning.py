import re
import math
from datetime import datetime ,date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError
from odoo.exceptions import UserError


class dzc_2ProjectPlanning(models.Model):
    _name = 'dzc2.project.planning'

    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    name = fields.Char(string="Plan Name" ,copy=False)
    code = fields.Char(string="PLAN/YEAR", readonly=True)
    date_of_plan = fields.Date(string="Date", default=datetime.today())
    total_budget = fields.Float(string="Total Budget" )
    total_project_target = fields.Float(string="Total Families Targeted" )
    duration_from  = fields.Date(string="Date From",copy=False, default=datetime.today() )
    duration_to = fields.Date(string="Date To",copy=False )
    duration = fields.Char(string= "Duration", readonly=True, compute="duration_compute")
    plan_ids = fields.One2many('dzc2.project.budget.planning' ,'project_plan_id',string="State" )
    total_execued_projects = fields.Float(copy=True ,compute="total_executed", String="Total Executed Projects",store=True)
    total_executed_budget = fields.Float(copy=True ,compute="total_executed" ,string="Total Executed Budget",store=True,)
    state = fields.Selection([('draft' , 'Draft') ,
     ('confirm' , 'Confirm') ,
      ('approve' , 'Approve') ,
       ('done' , 'Done') ,
        ('cancel' , 'Cancel')], string="Status", default='draft')

    

    @api.multi
    def confirm_action(self):
        self.env.context  = {'status_action' : True}
        if not self.plan_ids:
            raise ValidationError(_("There is no states plans to confirm ."))

        self.write({'state': 'confirm'})

    @api.multi
    def approve_action(self):
        self.env.context  = {'status_action' : True}
        self.write({'state': 'approve'})

    @api.multi
    def done_action(self):
        self.env.context  = {'status_action' : True}
        self.write({'state': 'done'})


    @api.multi
    def cancel_action(self):
        self.env.context  = {'status_action' : True}
        self.write({'state': 'cancel'})

    @api.multi
    def set_to_draft_action(self):
        self.env.context  = {'status_action' : True}
        self.write({'state': 'draft'})

###################### form sequence number (PLAN/Year/20../0000N)###########
    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(_('Sorry! You cannot delete plan not in Draft state.'))
        return models.Model.unlink(self)
    #************ SQL Constrains *********************#
    # _sql_constraints = [
    #     ('plan_name_unique', 'unique(name)',
    #      'Sorry! Project Plan Name Must Be Unique .')]

    #************ Validation Constrains ***************#
    ## name field (required - space validation)##
    @api.constrains('name')
    def name_validation(self):
        increment = 0
        if len(self.name) > 1 :
            for record in self.name[1:]:
                if record.isalpha() or record.isdigit():
                    increment +=1

                elif increment == 0 :
                    raise ValidationError(_("Sorry! Name Field is Required and Must begin with Char ."))

        elif len(self.name) <= 1 and self.name[0] == ' ':
            raise ValidationError(_("Sorry! Name Field is Required and Must begin with Char ."))


    @api.constrains('total_budget','total_project_target')
    def totals_validation(self):
        for record in self:
            if record.total_budget <= 0.0 :
                raise ValidationError(_('Sorry ! Budget Can Not Be Zero Or Negative .'))

            elif record.total_project_target <= 0.0 :
                raise ValidationError(_("Sorry! Target Projects Can Not Be Zero Or Negative ."))


    ## store total budget as float without decimal ##
    @api.onchange('total_project_target')
    def _onchange_total_budget(self):
        self.total_project_target = math.floor(self.total_project_target)

    @api.multi
    def copy(self, default=None ):
        self.env.context  = {'skip_duration_constraint' : True}
        default = dict(default or {})
        default.update({'plan_ids':self.get_lines() })
       
        return super(dzc_2ProjectPlanning, self).copy(default)

    @api.multi
    def get_lines(self):

        plan_line = []
        for d in self.plan_ids:
            plan_line +=  [(0, 6, {
            'state_plan_ids': d.state_plan_ids.id,
            'percentage': d.percentage,
            'share_from_budget': d.share_from_budget,
            'share_from_projects': d.share_from_projects,})]
        return plan_line
################################################ Total of persentages > 100##############
    # @api.constrains('total_project_target')
    # def total_persents(self):
    #     total = 0.0
    #     for record in self.plan_ids:
    #         total += record.percentage
    #     if total > 100.00 :
    #         raise ValidationError(_("Sorry! Total Of Persentages Can not Be Greater than 100 ."))
        
    # @api.constrains('duration_from' , 'duration_to')
    # def duration_validation(self):
    #     plans = self.env['dzc2.project.planning'].search([('duration_from' , '>=', self.duration_from) , ('duration_to' ,'<=' , self.duration_to),('id' , '!=' ,self.id)])
    #     if plans:
    #         raise ValidationError(_('Sorry! You cannot make Plan  with same duration.'))
    #         if self.duration_from > self.duration_to:
    #             raise ValidationError(_('Sorry! Begin Of Plan Date Must Be Before End Date ..'))
    #     else:
    #         True

    @api.model
    def create(self, vals):
        
        vals['code'] = self.sudo().env['ir.sequence'].sudo().next_by_code('dzc2.project.planning.sequence') or '/'
        
        if 'skip_duration_constraint' in self.env.context and self.env.context['skip_duration_constraint']:
            return super(dzc_2ProjectPlanning, self).create(vals)
         
        plans = self.env['dzc2.project.planning'].search([('duration_from' , '>=', vals['duration_from']) , ('duration_to' ,'<=' , vals['duration_to'])])

        if plans:
            raise ValidationError(_('Sorry! You cannot make Plan  with same duration.'))
        if vals['duration_from'] > vals['duration_to']:
            raise ValidationError(_('Sorry! Begin Of Plan Date Must Be Before End Date ..'))

        return super(dzc_2ProjectPlanning, self).create(vals)
    
    @api.multi
    def write(self , vals):

        if 'status_action' in self.env.context and self.env.context['status_action']:
            return super(dzc_2ProjectPlanning, self).write(vals)
        
        if 'request_cont' in self.env.context and self.env.context['request_cont']:
            return super(dzc_2ProjectPlanning, self).write(vals)
       
        if 'skip_duration_constraint' in self.env.context and self.env.context['skip_duration_constraint']:
            plans = self.env['dzc2.project.planning'].search([('duration_from' , '>=', self.duration_from) , ('duration_to' ,'<=' , self.duration_to),('id' , '!=' ,self.id)])
            if plans:
                raise ValidationError(_('Sorry! You cannot make Plan  with same duration.'))
                if self.duration_from > self.duration_to:
                    raise ValidationError(_('Sorry! Begin Of Plan Date Must Be Before End Date ..'))

        return super(dzc_2ProjectPlanning, self).write(vals)

    ##################*********** ********##########
            
class dzc_2ProjectBudgetPlanning(models.Model):
    _name = 'dzc2.project.budget.planning'

    name = fields.Char()
    state_plan_ids = fields.Many2one('zakat.state' , string="State" )
    project_plan_id = fields.Many2one('dzc2.project.planning' ,string="State Plan")
    percentage = fields.Float(string="Persentage")
    share_from_budget = fields.Float(readonly=False,compute="project_share_from_budget" ,string="Share From Total Budget" , default="0.0")
    share_from_projects = fields.Float(readonly=False ,compute="project_share_from_budget" ,string="Share From Total Project")
    execute_from_projects = fields.Float(string="Execute From Total Projects")
    execute_from_budget = fields.Float(string="Execute From Total budget")
    performance = fields.Float(string="Performance")

    @api.constrains('percentage' , 'share_from_budget' , 'share_from_projects' , 'execute_from_projects' , 'execute_from_budget')
    def numeric_validation(self):
        for record in self:
            if record.percentage <= 0.0 :
                raise ValidationError(_("Sorry! Persentage Can Not Be Zero Or Negative ."))
            elif record.share_from_budget < 0.0 :
                raise ValidationError(_("Sorry! Share From Budget Can Not Be Negative."))
            elif record.share_from_projects < 0.0 :
                raise ValidationError(_("Sorry! Share From Project Can Not Be Negative."))
            elif record.execute_from_projects < 0.0 :
                raise ValidationError(_("Sorry! Execute From Project Can Not Be Negative."))
            elif record.execute_from_budget < 0.0 :
                raise ValidationError(_("Sorry! Execute From Budget Can Not Be Negative."))


    @api.onchange('state_plan_ids')
    def _onchange_(self):
        self.name = self.state_plan_ids.name
    ##################*********** Calculations Functions ********##########
        ## Share from total budget , target depend on persentage  ##
    @api.one
    @api.depends('percentage' ,'project_plan_id.total_budget','project_plan_id.total_project_target' )
    def project_share_from_budget(self):
        if self.percentage > 0.0 :
            """
            Division by zero validation
            """
            self.share_from_budget = (self.project_plan_id.total_budget * self.percentage ) / 100
            self.share_from_projects = math.ceil((self.project_plan_id.total_project_target * self.percentage) / 100 )
        else:
            True
