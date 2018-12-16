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
    
class account_payment(models.Model):
    _inherit = "account.payment"

    payment_transfer_date = fields.Date(string='Payment Transfer Date', default=fields.Date.context_today, required=True, copy=False)
    name = fields.Char(readonly=True, copy=False, default=_("Draft Payment"))

    @api.multi
    def send(self):
        for rec in self:
            # Use the right sequence to set the name
            sequence_code = 'account.payment.transfer'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name :
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
            transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
            rec.write({'state': 'sent', 'move_name': move.name})

    @api.multi
    def confirm(self):
        for rec in self:
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            transfer_debit_aml = rec._create_transfer_entry(amount)
            rec.write({'state': 'posted'})

    def _create_transfer_entry(self, amount):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconciliable move line
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, dummy = aml_obj.with_context(date=self.payment_transfer_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        amount_currency = self.destination_journal_id.currency_id and self.currency_id.with_context(date=self.payment_date).compute(amount, self.destination_journal_id.currency_id) or 0

        dst_move = self.env['account.move'].create(self._get_move_vals(self.destination_journal_id, self.payment_transfer_date))

        dst_liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, dst_move.id)
        dst_liquidity_aml_dict.update({
            'name': _('Transfer from %s') % self.journal_id.name,
            'account_id': self.destination_journal_id.default_credit_account_id.id,
            'currency_id': self.destination_journal_id.currency_id.id,
            'journal_id': self.destination_journal_id.id})
        aml_obj.create(dst_liquidity_aml_dict)

        transfer_debit_aml_dict = self._get_shared_move_line_vals(credit, debit, 0, dst_move.id)
        transfer_debit_aml_dict.update({
            'name': self.name,
            'account_id': self.company_id.transfer_account_id.id,
            'journal_id': self.destination_journal_id.id})
        if self.currency_id != self.company_id.currency_id:
            transfer_debit_aml_dict.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.amount,
            })
        transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        dst_move.post()
        return transfer_debit_aml

    def _get_move_vals(self, journal=None,date=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
        if date:
            return {
                'name': name,
                'date':date,
                'ref': self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
                 }
        else:
            return {
                'name': name,
                'date': self.payment_date,
                'ref': self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
                 }


