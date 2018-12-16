# -*- coding: utf-8 -*-

import re
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError, UserError


class MaytrFamilySupport(models.Model):
    _name = 'maytr.family.support'

    date = fields.Date(string="Order Date", default=datetime.today())
    order_ref = fields.Char("Order Sequence")
    name = fields.Char("Program Name")
    state_id = fields.Many2one('zakat.state')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    maytr_no = fields.Integer("Maytr No", compute='get_info')
    total_amount = fields.Integer("Total Amount", compute='get_info')
    lines_ids = fields.One2many('maytr.line', 'maytr_support', ondelete='restrict')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approval', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default='draft')

    @api.one
    @api.depends('lines_ids')
    def get_info(self):
        """
        To Get The Number of Social Supported Number and The Total Amount
        :return:
        """
        total = 0
        count = 0
        for record in self.lines_ids:
            count += 1
            total += record.amount
        self.total_amount = total
        self.maytr_no = count

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('order_ref', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['order_ref'] = self.env['ir.sequence'].next_by_code('maytr.family.support.sequance') or '/'
        return super(MaytrFamilySupport, self).create(vals)

    @api.multi
    def action_confirm(self):
        """
        Change State To Confirm
        :return:
        """
        if self.lines_ids:
            self.write({'state': 'confirmed'})
        else:
            raise ValidationError(_("You must have Maytrs in lines."))


    @api.multi
    def action_approve(self):
        """
        Change State To Approve
        :return:
        """
        self.write({'state': 'approval'})

    @api.multi
    def action_cancle(self):
        """
        Change State To Cancle
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_done(self):
        """
        Change State To Done
        :return:
        """
        maytr_line = []
        if self.company_id.property_fesabeelallah_account_id:
            for rec in self.lines_ids:
                maytr_line += [(0, 6, {
                    'account_id': self.company_id.property_fesabeelallah_account_id.id,
                    'quantity': 1,
                    'name': _('Maytr Family Support'),
                    'price_unit': rec.amount,
                    })]
                voucher = self.env['account.voucher'].create(
                    {
                    'name': '',
                    'journal_id': self.company_id.fesabeelallah_journal.id,
                    'company_id': self.company_id.id,
                    'pay_now': 'pay_later',
                    'partner_id': rec.maytr_id.partner_id.id,
                    'reference': rec.maytr_id.partner_id.name,
                    'voucher_type': 'purchase',
                    'line_ids': maytr_line,
                    })
                rec.write({'vaucher_id': voucher.id})
                maytr_line = []
        else:
            raise ValidationError(_("You Must specify Accounts for Fesabeel Allah in general setting"))

        self.write({'state': 'done'})

    @api.multi
    def action_set_draft(self):
        """
        Change State To Draft
        :return:
        """
        self.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete None Drafted Record"))
            else:
                return super(MaytrFamilySupport, self).unlink()


class MaytrFamilySupportLine(models.Model):
    _name = 'maytr.line'

    maytr_support = fields.Many2one('maytr.family.support')
    maytr_id = fields.Many2one('dzc_7.maytr', string="Maytr")
    amount = fields.Float("Amount")
    vaucher_id = fields.Many2one('account.voucher')
