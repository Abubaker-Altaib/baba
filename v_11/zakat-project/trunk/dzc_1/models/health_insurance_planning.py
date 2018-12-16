
from odoo import fields, models, api, exceptions, _
import re
import math
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Health Insurance planning 
class HealthInsurancePlan(models.Model):
    _name = 'dzc1.health.insurance.plan'

    # _sql_constraints = [('uniq_insurance_plan', 'unique(duration_to,state_id ,company_id)',
    #                      _("You cannot make twice Plan for this state for same year!"))]


    name = fields.Char(string="Subject", size=256)
    date = fields.Date(string="Order Date", default=datetime.today())
    code = fields.Char(string="Reference Number")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    no_of_family = fields.Integer(string="No Of Families")
    state_id = fields.Many2one('zakat.state')
    duration_from = fields.Date(string="From")
    duration_to = fields.Date(string="To" )
    loacl_states_ids = fields.One2many('localstates.health.insurance.plan' , 'insurance_plan_id' , string="Local States")
    state = fields.Selection([('draft' , 'Draft') , ('confirm' ,'Confirm'),('approve' ,'Approve') ,('done' ,'Done'),('cancel' ,'Cancel')], string="Status", default="draft")
    """
    Workflow states
    """
    @api.multi
    def confirm_action(self):
        if not self.loacl_states_ids:
            raise ValidationError(_('There is no plans for local states specified.'))

        else:
            self.write({'state': 'confirm'})

    @api.multi
    def cancel_action(self):
          self.write({'state': 'cancel'})

    @api.multi
    def approve_action(self):
          self.write({'state': 'approve'})

    @api.multi
    def done_action(self):
          self.write({'state': 'done'})
    
    @api.multi
    def set_to_draft_action(self):
          self.write({'state': 'draft'})

    """
    unlinke can not be in done state
    """
    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(_('Sorry! You Cannot Delete Order In Not Draft State.'))
        return models.Model.unlink(self)

    """
    sequence of form (Reference)
    """
    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('health.insurance.plan.sequence') or '/'
        plans = self.env['dzc1.health.insurance.plan'].search([('state_id' ,'=' , vals['state_id']) ,('duration_from' , '>=', vals['duration_from']) , ('duration_to' ,'<=' , vals['duration_to'])])
        if plans:
            raise ValidationError(_('Sorry! You cannot make Plan for this state with same duration.'))
        else:
            True 
        return super(HealthInsurancePlan, self).create(vals)


    """
    Constrains
    """
    @api.constrains('no_of_family')
    def no_of_family_validation(self):
        for record in self:
            if record.no_of_family <= 0.0 :
                raise ValidationError(_('Sorry ! No Of Families Can Not Be Zero Or Negative .'))

    @api.constrains('duration_from', 'duration_to')
    def compare_date(self):
        for rec in self:
            if rec.duration_from < rec.duration_to:
                return True
            else:
                raise ValidationError(_("Start Date must Be Before the End Date"))

    @api.constrains('name')
    def name_validation(self):
        increment = 0
        if len(self.name) > 1 :
            for record in self.name[1:]:
                if record.isalpha() or record.isdigit():
                    increment +=1

                elif increment == 0 :
                    raise ValidationError(_("Sorry! Subject Field is Required and Must begin with Char ."))

        elif len(self.name) <= 1 and self.name[0] == ' ':
            raise ValidationError(_("Sorry! Subject Field is Required and Must begin with Char ."))

# Health Insurance planning of Local States
class LocalStatesHealthInsurancePlan(models.Model):
    _name = 'localstates.health.insurance.plan'

    name = fields.Char()
    insurance_plan_id = fields.Many2one('dzc1.health.insurance.plan')
    loacl_states_id = fields.Many2one('zakat.local.state')
    no_families = fields.Integer(compute="calculation_fields" , string="No Of families")
    families_per_month = fields.Integer(compute="calculation_fields", string="No families per month")
    families_per_week = fields.Integer(compute="calculation_fields", string="No families per week")
    actual_execute = fields.Integer(string="Actual Execute")


    @api.onchange('loacl_states_id')
    def _onchange_(self):
        self.name = self.loacl_states_id.name

    @api.one
    @api.depends('loacl_states_id' , 'insurance_plan_id.no_of_family')
    def calculation_fields(self):
        for ls in self:
            poor_persent = (ls.loacl_states_id.poor_percentage / 100)
            families = math.floor(ls.insurance_plan_id.no_of_family * poor_persent ) 
            ls.no_families = families
            ls.families_per_month = math.ceil(families / 12 )
            ls.families_per_week =  math.ceil(families / 48 )
