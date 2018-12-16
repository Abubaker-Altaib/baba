# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class AppointmentTerms(models.Model):

    _name = "hr.appointment.term"
    _description = 'Appointment Terms'

    name = fields.Char(string='Appointment Terms', required=True , Translate=True)


class ContractType(models.Model):

    _name = 'hr.contract.type'
    _inherit = ['mail.thread', 'hr.contract.type']

    code = fields.Char(string="Code",required=True, size=5, 
        readonly=True, states={'draft': [('readonly', False)]})
    sequence_id = fields.Many2one('ir.sequence', string='Contract Sequence', required=True, copy=False)
    app_term_ids = fields.Many2many('hr.appointment.term', string="Appointment Terms", 
        readonly=True, states={'draft': [('readonly', False)]})
    term_ids = fields.One2many('hr.contract.term', 'contract_type_id', string="Terms", 
        readonly=True, states={'draft': [('readonly', False)]})
    tag_id = fields.Many2one('hr.employee.category', string="Employee Tag",  
        readonly=True, states={'draft': [('readonly', False)]})
    resource_calendar_id = fields.Many2one('resource.calendar', string="working schedule",  
       readonly=True,states={'draft': [('readonly', False)]})
    trial_period = fields.Integer("Trial Period", default=3, required=True,  
        readonly=True, states={'draft': [('readonly', False)]})
    trial_period_times = fields.Integer("Trial Period Times", default=3, required=True,  
        readonly=True, states={'draft': [('readonly', False)]})
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


class ContractTypeTerms(models.Model):

    _name = "hr.contract.term"
    _description = 'Contract Terms'
    _order = 'term_no'

    name = fields.Char(string='Term' ,required=True)
    term_no = fields.Integer("Term Number", required=True)
    description = fields.Text('Description')
    type = fields.Selection([
        ('mandatory', 'Mandatory'),
        ('optional', 'Optional')], string='Type', default='mandatory', required=True)
    contract_type_id = fields.Many2one("hr.contract.type")


class Contract(models.Model):

    _inherit = 'hr.contract'

    name = fields.Char('Contract Reference', required=False, readonly=True)
    type = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
    ],string='Type')
    
    medical_insurance = fields.Boolean('Medical Insurance?')
    medical_insurance_ids = fields.One2many('hr.employee.insurance','contract_id', string="Medical Insurance")
    number_dependents=fields.Integer("Dependents Number")
    state = fields.Selection([
        ('draft', 'New'),
        ('approval', 'Waiting For Approval'),
        ('check', 'Waiting For Check'),
        ('fit', 'Medically Fit'),
        ('test', 'Under Test'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
        ('unfit', 'Medically Unfit')
    ], string='Status', group_expand='_expand_states',
       track_visibility='onchange', help='Status of the contract', default='draft')
    trial_period_times = fields.Integer("Trial Period Times", default=0,readonly=True)
       
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.multi
    def action_confirm(self):
        return self.write({'state': 'approval'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'check'})

    @api.multi
    def action_refusal(self):
        return self.write({'state': 'cancel'})

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
        new_name = seq.next_by_id()
        vals['name'] = new_name
        return super(Contract, self).create(vals)

    @api.onchange('type_id')
    def onchange_type(self):
        if self.type_id:
            date_start = fields.Datetime.from_string(self.date_start)
            self.trial_date_end = date_start + relativedelta(months=self.type_id.trial_period)
            if self.type_id.type =='temporary':
                self.date_end = date_start+relativedelta(months=self.type_id.temporary_period)
            self.type == self.type_id.type 
 
    
class Employee(models.Model):

    _inherit = "hr.employee"

    children = fields.Float('Number of Children', compute='_compute_children')
    contract_id = fields.Many2one('hr.contract', compute='_compute_contract_id', string='Current Contract')
    
    @api.multi
    def _compute_children(self):
        for employee in self:
            children = employee.family_ids.filtered(lambda family: family.relation in ['son','daughter'] )
            employee.children = len(children)
            
    def _compute_contract_id(self):
        Contract = self.env['hr.contract']
        for employee in self:
            contract_id = False
            contract_id = Contract.search([
                ('employee_id', '=', employee.id),('type', '=','permanent')], order='date_start desc', limit=1) 
            if not contract_id:
                 contract_id = Contract.search([('employee_id', '=', employee.id)], order='date_start desc', limit=1)
            employee.contract_id = contract_id     
class InsuranceEmployee(models.Model):

    _inherit = "hr.employee.insurance"
    
    contract_id = fields.Many2one('hr.contract', 'Contract')
