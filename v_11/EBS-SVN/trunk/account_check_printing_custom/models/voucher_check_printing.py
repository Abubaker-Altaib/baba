# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import math
from odoo.tools.translate import _
from odoo import tools
from odoo import models, fields, api , exceptions
from odoo.addons.account_check_printing_custom.models import amount_to_text_ar
from odoo.exceptions import UserError, ValidationError


class AccountVoucher(models.Model):
    """
    Inherit object account.voucher to add print checks appility 
    """
    _inherit = 'account.voucher'

    #v11 add sent to voucher state
    state = fields.Selection(selection_add=[('sent', 'Sent')], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated and voucher entries are created in account.\n"
             " * The 'Sent' status is used when the check is print in Pay Directly case.\n"
             " * The 'Cancelled' status is used when user cancel voucher.")

    check_manual_sequencing = fields.Boolean(related='journal_id.check_manual_sequencing')
    check_number = fields.Integer(string="Check Number", readonly=True, copy=False,
        help="The selected journal is configured to print check numbers. If your pre-printed check paper already has numbers "
             "or if the current numbering is wrong, you can change it in the journal configuration page.")
    check_amount_in_words = fields.Char(string="Amount in Words", compute='_onchange_amount')


    @api.multi
    def unmark_sent(self):
        self.write({'state': 'posted'})

    @api.one
    @api.depends('amount')
    def _onchange_amount(self):
        context = self._context or {}
        if hasattr(super(AccountVoucher, self), '_onchange_amount'):
            super(AccountVoucher, self)._onchange_amount()
        if context.get('lang') == 'ar_SY':
            self.check_amount_in_words = amount_to_text_ar.amount_to_text(self.amount, 'ar')
        else:
            self.check_amount_in_words = self.currency_id.amount_to_text(self.amount)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if hasattr(super(AccountVoucher, self), '_onchange_journal_id'):
            super(AccountVoucher, self)._onchange_journal_id()
        if self.journal_id.check_manual_sequencing:
            self.check_number = self.journal_id.check_sequence_id.number_next_actual

    @api.onchange('pay_now')
    def _onchange_pay_now(self):
        if self.pay_now == 'pay_now'\
                and self.check_manual_sequencing:
            sequence = self.journal_id.check_sequence_id
            self.check_number= sequence.next_by_id()

    @api.model
    def create(self, vals):
        res = super(AccountVoucher, self).create(vals)
        res.write({'check_number': False})
        return res
 
    @api.one
    def do_print_checks(self, new_check_no):
        """ Create a check.log """
        self.check_number = new_check_no
        context = self._context or {}
        cr = self._cr or False
        uid = self._uid or False
        ids = self._ids or []
        self.env['check.log'].create({
                'voucher_name': self.id,
                'status': 'active',
                'check_no': self.check_number,
                'journal_id': self.journal_id.id,
            })
        self.env['ir.sequence'].browse(self.journal_id.checkno_sequence_id.id).number_next =  self.check_number + 1
    @api.multi
    def print_check_report(self):
        if self.journal_id.check_dimension.id != False :
           res = {
                'voucher_date':self.date,
                'partner_name':self.partner_id and self.partner_id.name or "",
                'check_amount_in_words':self.check_amount_in_words,
                'amount_money':self.amount,
                'beneficiary':self.journal_id.check_dimension.beneficiary,
                'font_size':self.journal_id.check_dimension.font_size,
                'date':self.journal_id.check_dimension.date,
                'amount':self.journal_id.check_dimension.amount,
                'number':self.journal_id.check_dimension.number
                }
           datas = {
            'ids': self._ids,
            'model': 'account.voucher', # wizard model name
            'form': res,
            }

           dic=self.env.ref('account_check_printing_custom.print_voucher_check_qweb_report').report_action(self, data=datas)
           return dic
        else:
           raise UserError(_("Please add check dimensions to the selected journal in order to print a check."))

    @api.one
    def _get_next_check_no(self):
        """ @return: int next check number according to Journal's check_seq. """
        sequence = self.env['ir.sequence']
        if not self.journal_id.checkno_sequence_id:
            raise exceptions.ValidationError(_('Please add "Check Sequence" for journal %s')%(self.journal_id.name))
        seq_id = self.journal_id.checkno_sequence_id.id
        return  sequence.browse(seq_id).number_next 
 
    @api.multi
    def print_checks(self):
        """ Check that the recordset is valid, set the voucher state to sent and call do_print_checks() """
        #v11 voucher is paid (it's entry is reconciled) the check must not print
        self = self.filtered(lambda r: r.pay_now == 'pay_now' and not r.paid)

        if len(self) == 0:
            raise UserError(_("voucher to print as a checks must have 'Pay Directly' selected as payment method and "
                              "not have already been reconciled"))
        if any(voucher.journal_id != self[0].journal_id for voucher in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        self.filtered(lambda r: r.state == 'draft').proforma_voucher()
        self.write({'state': 'sent'})

        if not self[0].journal_id.check_manual_sequencing:
            is_printed = False
            if self.check_number != 0:
                is_printed = True
            return {
                'name': _('Print Check Report'),
                'type': 'ir.actions.act_window',
                'res_model': 'wiz.print.check',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'voucher_ids': self.ids,
                    'default_next_check_number': self._get_next_check_no()[0],
		            'default_preprinted': is_printed,
                }
            }
        else:
            return self.do_print_checks()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
