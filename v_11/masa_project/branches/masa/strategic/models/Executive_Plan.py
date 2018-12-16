# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError

class ExecutivePlan(models.Model):
    _name ="plan.excutive"
    _description = "ExecutivePlan"

    name=fields.Char(string='Name', required=True, index=True)
    active=fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide the project without removing it.")
    sequence=fields.Integer(default=10, help="Gives the sequence order when displaying a list of Projects.",required=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic',
        ondelete="cascade", required=True,domain="[('project','=', True)]")
    user_id=fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user, track_visibility="onchange",required=True)
    date_start=fields.Date(string='Start Date',required=True)
    date=fields.Date(string='Expiration Date', index=True, track_visibility='onchange')
    subtask_executive_Plan_id=fields.Many2one('plan.excutive', string='Sub-task Project', ondelete="restrict")
    objective_ids =fields.Many2one('strategic.objective')
    kpi_ids=fields.One2many('strategic.kpi','executive_Plan_id',string="Strategic Kpi")
    department_id=fields.Many2one('hr.department')
    strategic_plan_id=fields.Many2one('strategic.plan',required=True)
    target_value=fields.Float(string="Target Value",required=True)
    actual_value=fields.Float(string="Actual Value",required=True)
    percentage=fields.Float(string="Progress",required=True)
    plan_amount=fields.Float(string="Plan Amount",required=True)
    approve_amount=fields.Float(string="Approve Amount",required=True)
    description=fields.Text(string='Description')
    note=fields.Text(string='Description')
    budget_ids=fields.Many2many('crossovered.budget',String="Budget")
    state=fields.Selection([
            ('draft','Draft'),
            ('confirmed','Confirmed'),
            ('approved','Approved')],default="draft",index=True,required=True,readonly=True,copy=False
            )
    date_start = fields.Datetime(string='Starting Date',
    default=fields.Datetime.now,
    index=True, copy=False,required=True)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False,required=True)
    task_ids = fields.One2many('plan.task', 'plan_excutive_id', string='Tasks')
    request_count = fields.Integer(compute='_compute_request_count', type='integer', string="Request Count")


    @api.multi
    def _compute_request_count(self):
        request=self.env['account.voucher']
        self.request_count=request.search_count([('account_analytic_id', '=', self.analytic_account_id.id)])

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def set_confirmed(self):
        self.write({'state': 'confirmed'})

    @api.multi
    def set_approved(self):
        self.write({'state': 'approved'})

    @api.multi
    def get_request(self): 
        return {
            'name': _('Request'),
            'domain':[('account_analytic_id','=', self.analytic_account_id.id)],
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
        }


class PLanTask(models.Model):
    _name = "plan.task"
    _description = "Task"

    active = fields.Boolean(default=True)
    name = fields.Char(string='Task Title', track_visibility='always', required=True, index=True)
    description = fields.Html(string='Description')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ], default='0', index=True, string="Priority")
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of tasks.")
    create_date = fields.Datetime(index=True)
    write_date = fields.Datetime(index=True)  #not displayed in the view but it might be useful with base_automation module (and it needs to be defined first for that)
    date_start = fields.Datetime(string='Starting Date',
    default=fields.Datetime.now,
    index=True, copy=False)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False)
    notes = fields.Text(string='Notes')
    planned_hours = fields.Float(string='Initially Planned Hours', help='Estimated time to do the task, usually set by the project manager when the task is in draft state.')
    remaining_hours = fields.Float(string='Remaining Hours', digits=(16,2), help="Total remaining time, can be re-estimated periodically by the assignee of the task.")
    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
        index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner',
        string='Customer')
    company_id = fields.Many2one('res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    parent_id = fields.Many2one('plan.task', string='Parent Task')
    child_ids = fields.One2many('plan.task', 'parent_id', string="tasks")
    task_count = fields.Integer(compute='_compute_task_count', type='integer', string="task count")
    plan_excutive_id = fields.Many2one('plan.excutive',
        string='Excutive plan',
        index=True)
    weight = fields.Float('Weight')
    verified= fields.Float('Verified')
    progress=fields.Float(string="Progress",compute="_compute_progress",widgets='Percentage')
    main = fields.Boolean('Main')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    line_ids=fields.One2many('plan.task.line', 'task_id')
    plan_excutive_id=fields.Many2one('plan.excutive')
    kpi_id=fields.Many2one('strategic.kpi')

    @api.one
    @api.depends('weight','verified')
    def _compute_progress(self):
        if self.weight != 0:
            self.progress=(self.verified/self.weight)*100

    @api.multi
    def _compute_task_count(self):
        for task in self:
            task.task_count = self.search_count([('id', 'child_of', task.id), ('id', '!=', task.id)])

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'plan.task'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for plan in self:
            plan.attachment_number = attachment.get(plan.id, 0)


    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'plan.task'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'plan.task', 'default_res_id': self.id}
        return res


class PLanTaskLine(models.Model):
    _name = "plan.task.line"
    _description = "Task"

    name = fields.Char(string='Task Title', track_visibility='always', required=True, index=True)
    sequence = fields.Integer(string='Sequence', index=True, default=10)
    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
        index=True, track_visibility='always')
    task_id=fields.Many2one('plan.task',ondelete='cascade', index=True, required=True)

class ResPartner(models.Model):
    """ Inherits partner and adds Tasks information in the partner form """
    _inherit = 'res.partner'

    task_ids = fields.One2many('plan.task', 'partner_id', string='Tasks')


class StrategicPlan(models.Model):
    _name ="strategic.plan"
    _description = "strategic Plan"

    name = fields.Char(string='Name', required=True, index=True)
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide the project without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Projects.",required=True)
    vision =fields.Text(String="Vision",required=True)
    value =fields.Text(String="Value",required=True)
    mission =fields.Text(String="Mission",required=True)
    partnerships_ids =fields.Many2many('strategic.partnerships')
    initiatives_ids =fields.Many2many('strategic.initiatives')
    target_value= fields.Float(string="Target Value",required=True)
    actual_value= fields.Float(string="Actual Value",required=True)
    percentage=fields.Float(string="Progress",required=True)
    date_start = fields.Datetime(string='Starting Date',
    default=fields.Datetime.now,
    index=True, copy=False,required=True)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False,required=True)
    state=fields.Selection([
            ('draft','Draft'),
            ('inprogress','InProgress'),
            ('done','Done'),],default="draft",index=True, required=True, readonly=True, copy=False)


    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def set_inprogress(self):
        self.write({'state': 'inprogress'})


    @api.multi
    def set_done(self):
        self.write({'state': 'done'})


class AccountBudgetOperation(models.Model):

    _inherit="account.budget.operation"

    target = fields.Selection([
        ('analytic', 'Analytic'),
        ('project', 'Project'),
        ], default='analytic',index=True,string="Target")

