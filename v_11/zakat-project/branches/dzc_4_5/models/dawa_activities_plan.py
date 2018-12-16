# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models,api, exceptions,_
import re
import calendar
from odoo.exceptions import ValidationError, AccessError 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

class DawaActivities(models.Model):
    _name = 'dzc_4_5.dawa.activities.plan'

    name = fields.Char(string="Plan Name", size=256)
    date = fields.Date(string="Order Date", default=datetime.today())
    code = fields.Char(string="Reference Number")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    type = fields.Selection([('year' , 'Year'),('month' , 'Month')])
    year = fields.Char(string="Year", default=lambda self: datetime.today().year)
    month = fields.Selection([('january','January'), ('february','February'), ('march','March'), ('april','April'),
     ('may' ,'May'), ('june','June'), ('july','July'), ('august','August'), ('september','September'),
      ('october','October'), ('november','November'), ('december','December')], string='Months')
    axis_id = fields.Many2one('dawa.axis' , string="Axis")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    state_id = fields.Many2one('zakat.state' , string="State" )
    activities_ids = fields.One2many('dzc_4_5.activities' ,'dawa_plan_id', string="Activities")
    state = fields.Selection([('draft' , 'Draft') , ('confirm' ,'Confirm'),('approve' ,'Approve') ,('done' ,'Done'),('cancel' ,'Cancel')], string="Status",default="draft")

    """
    Workflow states
    """
    @api.multi
    def confirm_action(self):
        if not self.activities_ids:
            raise ValidationError(_('You Must Have at least one Activity .'))
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
        vals['code'] = self.env['ir.sequence'].next_by_code('dawa.activities.plan.sequence') or '/'
        
        return super(DawaActivities, self).create(vals)
    
    @api.constrains('name')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.name.replace(" ","")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
   

  
class Activities(models.Model):
    _name = 'dzc_4_5.activities'

    activity_id = fields.Many2one('dawa.axis.sub')
    no_program = fields.Integer(string="No Program")
    cost = fields.Integer(string="Cost")
    execute = fields.Integer(string="Execute")
    dawa_plan_id = fields.Many2one('dzc_4_5.dawa.activities.plan')

    @api.constrains('no_program' , 'cost')
    def validate_nums(self):
        for rec in self:
            if rec.no_program <= 0 :
                raise ValidationError(_("No of Programs Cannot be zero or Negative"))
            if rec.cost <= 0:
                raise ValidationError(_("Cost of Activity Cannot be zero or Negative"))

