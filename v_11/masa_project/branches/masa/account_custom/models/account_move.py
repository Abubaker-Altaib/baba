# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, exceptions, tools, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class account_move_line(models.Model):
    _inherit ='account.move.line'


    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account' ,domain="[('type', '=', 'normal')]")

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id and self.account_id.analytic and self.account_id.analytic_account_ids:
            self.analytic_account_id=False
            analytics = self.account_id.analytic_account_ids.ids
            return {'domain': {'analytic_account_id': [('id', 'in', analytics)]}}

    @api.multi
    @api.constrains('account_id')
    def _nature_move_line_account(self):
        for record in self:
            if record.account_id.nature =='debit' and record.account_id.balance < 0 :
                raise Warning(_("The balance of debit account should not be less than zero !!!!!  \n -account:%s \n-balance:%s ")%(record.account_id.name,record.account_id.balance))

            elif record.account_id.nature =='credit' and record.account_id.balance > 0 :
                raise Warning(_("The balance of credit account should not be more than zero  !!!!!  \n -account:%s \n-balance:%s ")%(record.account_id.name,record.account_id.balance))





class AccountMoveCustom(models.Model):
    _inherit = 'account.move'

    payment_id = fields.Many2one('account.payment', string="Payment")
    state = fields.Selection(selection_add=[('reverse','Reverse')])

    @api.multi
    def reverse_moves(self, date=None, journal_id=None):
        reverse_moves = super(AccountMoveCustom, self).reverse_moves()
        for move in self.browse(reverse_moves):
            move.write({'state': 'reverse'})
        return reverse_moves

class AccountMoveReversalCustom(models.TransientModel):
    _inherit = 'account.move.reversal'

    @api.multi
    def reverse_moves(self):
        ac_move_ids = self._context.get('active_ids', False)
        move = self.env['account.move'].search([('id', 'in', ac_move_ids)])
        for voucher in move.payment_id.voucher_ids:
            voucher.state = 'cancel'
        for budget_confirm in move.line_ids:
            budget_confirm.budget_confirm_id.write({'state': 'cancel'})
        for rec in move.payment_id:
            rec.state = 'cancelled'
        return super(AccountMoveReversalCustom, self).reverse_moves()


