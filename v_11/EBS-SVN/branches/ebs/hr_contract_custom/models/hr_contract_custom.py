# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta, MO
import math
import dateutil.parser


class ContractType(models.Model):
    _name = 'hr.contract.type'
    _inherit = ['mail.thread', 'hr.contract.type']

    
    code = fields.Char(string = "Code" ,required=True ,size=5 , readonly=True,states={'draft': [('readonly', False)]})
    sequence_id = fields.Many2one('ir.sequence', string='Contract Sequence',
        help="This field contains the information related to the numbering of the journal entries of this journal.", required=True, copy=False)
    #term_ids = fields.One2many('hr.contract.term', 'contract_type_id' ,string ="Terms", readonly=True,states={'draft': [('readonly', False)]})
    tag_id = fields.Many2one('hr.employee.category' ,string = "Employee Tag",  readonly=True,states={'draft': [('readonly', False)]})
    resource_calendar_id = fields.Many2one('resource.calendar' ,string = "working schedule",  readonly=True,states={'draft': [('readonly', False)]})
    trial_period = fields.Integer("Trial Period", default=3, required=True,  readonly=True,states={'draft': [('readonly', False)]})
    trial_period_times = fields.Integer("Trial Period Times", default=3, required=True,  readonly=True,states={'draft': [('readonly', False)]})
    temporary_period=fields.Integer("Temporary Period")
    type = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
    ],string='Type',required=True,  readonly=True,states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Closed'),
    ], string='Status', default='draft', track_visibility='onchange')
    number_dependents=fields.Integer("Dependents Number",  readonly=True,states={'draft': [('readonly', False)]})
    active = fields.Boolean(default=True)

    @api.multi
    def write(self, vals):
        for ttype in self:
            if ('code' in vals and ttype.code != vals['code']):
                if self.env['hr.contract'].search([('type_id', 'in', self.ids)], limit=1):
                    raise UserError(_('This Type already contains contracts, therefore you cannot modify its short name.'))
                if ttype.sequence_id:
                    ttype.sequence_id.write({'prefix': vals['code']})
                else:
                    name= 'name' in vals and vals['name'] or ttype.name
                    vals.update({'sequence_id': self.sudo()._create_sequence({'code':vals['code'], 'name':name}).id})
        result = super(ContractType, self).write(vals)
        
    @api.model
    def create(self, vals):
        if not vals.get('sequence_id'):
            vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        return super(ContractType, self).create(vals)

    @api.model
    def _create_sequence(self, vals):
        prefix = vals['code'] + '/'
        seq = {
            'name': vals['name'] ,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
        }
        seq = self.env['ir.sequence'].create(seq)
        return seq


# class ContractTypeTerms(models.Model):
#     _name = "hr.contract.term"
#     _description = 'Contract Terms'
#     _order = 'term_no'

#     name = fields.Char(string='Term' ,required=True)
#     term_no = fields.Integer("Term Number", required=True)
#     description = fields.Text('Description')
#     type = fields.Selection([
#         ('mandatory', 'Mandatory'),
#         ('optional', 'Optional')], string='Type', default='mandatory', required=True)
#     contract_type_id = fields.Many2one("hr.contract.type")


class Contract(models.Model):
    _inherit = 'hr.contract'

    name = fields.Char('Contract Reference', required=False, readonly=True)
    type = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
    ],string='Type')
    number_dependents=fields.Integer("Dependents Number")
    state = fields.Selection([
        ('draft', 'New'),
        ('approval', 'Waiting For Approval'),
        ('check', 'Waiting For Check'),
        ('fit', 'Medically Fit'),
        ('test', 'Under Test'),
        ('administration_approval', 'Waiting For Administration Approval'),
        ('public_administration_approval', 'Waiting For Public Administration Approval'),
        ('general_manager_approval', 'Waiting For General Manager Approval'),
        ('hr_approval', 'Waiting For HR Approval'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
        ('reject', 'Rejected'),
        ('unfit', 'Medically Unfit')
    ], string='Status', group_expand='_expand_states',
       track_visibility='onchange', help='Status of the contract', default='draft')
    trial_period_times = fields.Integer("Trial Period Times", default=0,readonly=True)
    # is_suspended =  fields.Boolean(string='Is Salary Suspended', deafult=False )
    # tax_exempted = fields.Boolean(string = 'Tax Exempted', default=False)

    ##### new code
    notification_days = fields.Integer('Days To Notify')
    type = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
    ],string='Type')
    notify = fields.Boolean("Notify",compute="notification_calc")
    days_to_end = fields.Integer("Days to end",compute="days_to_end_method",store=True)

    @api.depends('notify')
    def notification_calc(self):
        for rec in self.filtered(lambda r:r.trial_date_end):
            if rec.trial_date_end and rec.notification_days:
                notification_date=fields.Date.from_string(rec.trial_date_end)+relativedelta(days=-rec.notification_days)
                if str(notification_date)<=fields.Date.today() and rec.trial_date_end>=fields.Date.today():
                    rec.notify=True

    @api.depends('trial_date_end')
    def days_to_end_method(self):
        for rec in self:
            if rec.trial_date_end:
                trial = dateutil.parser.parse(rec.trial_date_end).date()
                now = datetime.now().date()
                days = trial - now
                rec.days_to_end = days.days 

                            

        ##### end of new code

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.multi
    def action_confirm(self):
        return self.write({'state': 'approval'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'check'})

    @api.multi
    def action_modify(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_fit(self):
        return self.write({'state': 'fit'})

    @api.multi
    def action_unfit(self):
        return self.write({'state': 'unfit'})

    @api.multi
    def action_under_test(self):
        date_start = fields.Datetime.from_string(self.date_start)
        trial_period_times = self.trial_period_times+1
        if trial_period_times == self.type_id.trial_period_times:
            raise UserError(_('You can not repetition the trial period, therefore start with new job.'))
        trial_date_end = date_start + relativedelta(months=self.type_id.trial_period *trial_period_times)
        return self.write({'state': 'test', 'trial_date_end':trial_date_end, 'trial_period_times':trial_period_times})

    @api.multi
    def action_administration_approval(self):
        return self.write({'state': 'public_administration_approval'})

    @api.multi
    def action_public_administration_approval(self):
        return self.write({'state': 'general_manager_approval'})

    @api.multi
    def action_general_manager_approval(self):
        return self.write({'state': 'hr_approval'})

    @api.multi
    def action_hr_approval(self):
        return self.write({'state': 'open'})

    @api.multi
    def action_reject(self):
        return self.write({'state': 'reject'})


    @api.multi
    def action_termination(self):
        return self.write({'state': 'close'})

    @api.multi
    def action_set_to_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_full_designation(self):
        return self.write({'state': 'open'})

    @api.multi
    def action_close(self):
        return self.write({'state': 'close'})

    @api.multi
    def action_trial(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_renewal(self):
        return self.write({'state': 'pending'})

    @api.model
    def create(self, vals):
        type_id =vals['type_id']
        seq_result = self.env['hr.contract.type'].search([('id','=',type_id)])
        seq = seq_result.sequence_id
        if seq :
            new_name = seq.next_by_id()
            vals['name'] = new_name
        return super(Contract, self).create(vals)

    @api.onchange('type_id')
    def onchange_type(self):
        if self.type_id:
            date_start = fields.Datetime.from_string(self.date_start)
            self.trial_date_end = date_start + relativedelta(months=self.type_id.trial_period)
            if self.type_id.type=='temporary':
                self.date_end = date_start+relativedelta(months=self.type_id.temporary_period)
            self.type == self.type_id.type 
        
