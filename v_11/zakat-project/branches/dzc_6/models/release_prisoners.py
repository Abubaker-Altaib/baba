# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, exceptions, _
import re
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ReleasePrisoners(models.Model):
    _name = 'release.prisoners'

    name = fields.Char("Name")
    date = fields.Date(string='Date', default=datetime.today())
    code = fields.Char(string='Ref')
    partner_id = fields.Many2one('res.partner')
    total_approve_amount = fields.Float(compute='total_calculation')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    state_id = fields.Many2one('zakat.state')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('done', 'Done'), ('cancel', 'Cancel')], default="draft", string="Status")
    prisoners_ids = fields.One2many('prisoners', 'release_id', ondelete='restrict', string="Prisoners")
    vaucher_id = fields.Many2one('account.voucher')

    @api.constrains('name')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and self.search([('id', '!=', self.id), ('name', '=', self.name)]):
            raise exceptions.ValidationError(_("name must not be duplicated"))

    @api.multi
    def total_calculation(self):
        if self.prisoners_ids:
            for rec in self.prisoners_ids:
                self.total_approve_amount += rec.approved_amount
            return self.total_approve_amount

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.sequence.number_next_actual

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('release.prisoners') or '/'
        return super(ReleasePrisoners, self).create(vals)

    # @api.model
    # def create(self, vals):
    # 	vals['code'] = self.env['ir.sequence'].next_by_code('release.prisoners') or '/'
    # 	return super(ReleasePrisoners, self).create(vals)

    @api.multi
    def action_confirm(self):
        """
        Change Status To Confirm
        :return:
        """
        if self.prisoners_ids:
            settings = self.env['zakat.settings'].search([('write_date', '<=', self.date)], order='id desc', limit=1)
            print("\n\n\n\nthis is settings:", settings, "\n\n")
            if settings.property_prisoners_account_id and settings.property_prisoners_analytic_account_id and settings.property_prisoners_journal:
                self.write({'state': 'confirm'})
            else:
                raise ValidationError(
                    _("this order can't be confirmed, you need to add accounts in general settings of zakat"))
        else:
            raise ValidationError(_("This order can't be confirmed, you need to add prisoners first"))

    @api.multi
    def action_cancle(self):
        """
        Change state To Cancle
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_done(self):
        """
        Change state To Done
        :return:
        """
        settings = self.env['zakat.settings'].search([('write_date', '<=', self.date)], order='id desc', limit=1)

        prisoners_line = []
        for rec in self.prisoners_ids:
            prisoners_line += [(0, 6, {
                'name': rec.name,
                'account_id': settings.property_prisoners_account_id.id,
                'quantity': 1,
                'name': self.partner_id.name,
                'price_unit': rec.approved_amount,
            })]

        voucher = self.env['account.voucher'].create(
            {
                'name': self.name,
                'journal_id': settings.property_prisoners_journal.id,
                'company_id': self.company_id.id,
                'pay_now': 'pay_later',
                'partner_id': self.partner_id.id,
                'reference': self.partner_id.name,
                'voucher_type': 'purchase',
                'amount': self.total_approve_amount,
                'line_ids': prisoners_line,
            })
        self.vaucher_id = voucher.id
        self.write({'state': 'done'})

    @api.multi
    def action_set_draft(self):
        """
        Change status To Draft
        :return:
        """
        self.write({'state': 'draft'})

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_("You Can\'t Delete None Drafted Record"))
        else:
            return super(ReleasePrisoners, self).unlink()


class Prisoners(models.Model):
    _name = 'prisoners'

    name = fields.Char(string="Name", related='prisoner_id.name', store=True)
    prisoner_id = fields.Many2one('res.partner')
    court = fields.Char(string="Court")
    execute_no = fields.Integer("Execute Number")
    execute_amount = fields.Float("Executed Amount")
    approved_amount = fields.Float("Approved Amount")
    release_id = fields.Many2one('release.prisoners')

    @api.constrains('court')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.court.replace(" ", "")):
            raise ValidationError(_('court Field must be Literal'))
        if self.court and (len(self.court.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("court must not be spaces"))

    @api.constrains('execute_no', 'execute_amount', 'approved_amount')
    def check_ne(self):
        if self.execute_no:
            if self.execute_no <= 0.0:
                raise ValidationError(_("Execute Number can't be Zero or less"))
        if self.execute_amount:
            if self.execute_amount <= 0.0:
                raise ValidationError(_("Execute Amount can't be Zero or less"))
        if self.approved_amount:
            if self.approved_amount <= 0.0:
                raise ValidationError(_("Approved Amount can't be Zero or less"))
            if self.approved_amount > self.execute_amount:
                raise ValidationError(_("Approved Amount can't be more than the Executed Amount"))


class InheritedPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('presoners', []):
            illness_id = self.env['release.prisoners'].resolve_2many_commands('prisoners_ids',
                                                                              self._context.get('presoners', []))
            args.append(('id', 'not in',
                         [isinstance(d['prisoner_id'], tuple) and d['prisoner_id'][0] or d['prisoner_id']
                          for d in illness_id]))
        return super(InheritedPartner, self).name_search(name, args=args, operator=operator, limit=limit)
