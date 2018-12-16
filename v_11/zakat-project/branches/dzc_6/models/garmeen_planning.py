# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, exceptions, _
import re
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class dzc6GarmeenPlanning(models.Model):
    _name = 'dzc_6.gorm.plan'

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    name = fields.Char(string="Plan Name", copy=False, size=256)
    code = fields.Char(string="PLAN/MONTH/YEAR", readonly=True)
    date_of_plan = fields.Date(string="Date", default=datetime.today())
    duration_from = fields.Date(string="Date From", copy=False, default=datetime.today())
    duration_to = fields.Date(string="Date To", copy=False)
    state_id = fields.Many2one('zakat.state', string="State")
    local_state_id = fields.Many2one('zakat.local.state', string="Local State")
    total_amount = fields.Float(string="Total Amount")
    order_lines_ids = fields.One2many('dzc_6.gorm.order.line', 'plan_id', string="Order Lines")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('approve', 'Approve'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default='draft')

    @api.multi
    def confirm_action(self):
        if not self.order_lines_ids:
            raise ValidationError(_('You Must Have at least one Type .'))
        else:
            self.write({'state': 'confirm'})

    @api.multi
    def approve_action(self):
        self.write({'state': 'approve'})

    @api.multi
    def done_action(self):
        self.write({'state': 'done'})

    @api.multi
    def cancel_action(self):
        self.write({'state': 'cancel'})

    @api.multi
    def set_to_draft_action(self):
        self.write({'state': 'draft'})

    ###################### form sequence number (PLAN/Year/20../0000N)###########
    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('dzc6.garmeen.planning.sequence') or '/'

        return super(dzc6GarmeenPlanning, self).create(vals)

    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(_('Sorry! You cannot delete plan not in Draft state.'))
        return models.Model.unlink(self)

    # ************ SQL Constrains *********************#
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Sorry! Plan Name Must Be Unique .')]

    @api.multi
    def copy(self, default=None):
        self.env.context = {'skip_duration_constraint': True}
        default = dict(default or {})

        return super(dzc6GarmeenPlanning, self).copy(default)

    # ************ Validation Constrains ***************#
    ## name field (required - space validation)##
    @api.constrains('name')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))

    # Duration start > end date , cannot make two plans with same duration
    @api.constrains('duration_from', 'duration_to', 'total_amount')
    def duration_validate(self):
        if 'skip_duration_constraint' in self.env.context and self.env.context['skip_duration_constraint']:
            return

        plans = self.env['dzc_6.gorm.plan'].search(
            ['&', ('duration_from', '>=', self.duration_from), ('duration_to', '<=', self.duration_to), '&',
             ('state_id', '=', self.state_id.id), ('local_state_id', '=', self.local_state_id.id),
             ('id', '!=', self.id)])
        if plans:
            raise ValidationError(_('Sorry! You cannot make Plan  with same duration.'))

        if self.duration_from > self.duration_to:
            raise ValidationError(_('Sorry! Begin Of Plan Date Must Be Before End Date ..'))

        if self.total_amount <= 0.0:
            raise ValidationError(_('Sorry! Total Amount cannot be zero or negative..'))


class dzc6GarmeenOrderLines(models.Model):
    _name = 'dzc_6.gorm.order.line'

    plan_id = fields.Many2one('dzc_6.gorm.plan')
    type_id = fields.Many2one('dzc_6.gorm.types', string="Type")
    planned = fields.Float(compute="plan_lines_calc", string='Planned')
    executing_actual = fields.Float(string="Executing Actual")
    percentage = fields.Float(string="Percentage")
    no_of_orders = fields.Float(string="Total Cost")

    # Claculation of planning lines
    @api.multi
    @api.depends('plan_id.total_amount')
    def plan_lines_calc(self):
        for rec in self:
            plan = rec.type_id.persentage * rec.plan_id.total_amount
            rec.planned = plan
