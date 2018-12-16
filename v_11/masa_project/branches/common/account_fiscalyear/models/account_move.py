# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

#----------------------------------------------------------
# Entries Inherit
#----------------------------------------------------------
class AccountMove(models.Model):
    _inherit = "account.move"

    period_id= fields.Many2one('account.period', 'Period', domain="[('state', '=','open' )]", readonly=True)

    @api.model
    def create(self, vals):
        period_obj=self.env['account.period']
        ctx = dict(self._context or {}, account_period_prefer_normal=True)
        if 'period_id' in vals:
            if not vals['period_id']:
                period_id=period_obj.with_context(ctx).find(dt=vals['date'])
                vals['period_id']=period_id.id
        return super(AccountMove, self).create(vals)

    @api.multi
    @api.constrains('period_id', 'date')
    def _check_period(self):
        for rec in self:
            if rec.date and rec.period_id:
                if rec.date < rec.period_id.date_start or rec.date > rec.period_id.date_stop:
                    raise ValidationError(_('The date must be within the period duration. (The period: %s)') % rec.period_id.name)

    @api.multi
    @api.constrains('period_id')
    def _not_close_period(self):
        for line in self:
            if line.period_id.state=='done':
                raise Warning(_("Can not create move in close period!"))

    @api.onchange('date')
    def _onchange_date(self):
        if self.date:
            self.period_id = self.env['account.period'].search([('date_start', '<=', self.date), ('date_stop', '>=', self.date)], limit=1)

#----------------------------------------------------------
# Entries Lines Inherit
#----------------------------------------------------------
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    period_id= fields.Many2one(related='move_id.period_id', string='Period',store=True )


    @api.multi
    @api.constrains('period_id', 'date_maturity')
    def _check_period(self):
        for rec in self:
            if rec.date_maturity and rec.period_id:
                if rec.date_maturity < rec.period_id.date_start or rec.date_maturity > rec.period_id.date_stop:
                    raise ValidationError(_('The date must be within the period duration. (The period: %s)') % rec.period_id.name)

    @api.multi
    @api.constrains('period_id')
    def _not_close_period(self):
        for line in self:
            if line.period_id.state=='done':
                raise Warning(_("Can not create move in close period!"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
