# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.addons.account_check_printing_custom.models import amount_to_text_ar
from odoo.exceptions import UserError, ValidationError

class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.one
    @api.depends('outbound_payment_method_ids')
    def _compute_transfer_payment_method_selected(self):
        self.transfer_payment_method_selected = any(pm.code == 'transfer' for pm in self.outbound_payment_method_ids)

    check_dimension = fields.Many2one('account.check.dimension', 'Check dimension')
    transfer_sequence_id = fields.Many2one('ir.sequence', 'Transfer Sequence', copy=False,help="Transfer numbering sequence.")
    transfer_payment_method_selected = fields.Boolean(compute='_compute_transfer_payment_method_selected',
        help="Technical feature used to know whether transfer was enabled as payment method.")

 
class CheckLog(models.Model):
    """
    This class for storing some data for each printed check as a 
    summary log display check info and it's state.
    """
    _name = 'check.log'
    _description = 'Check Log'

    #TODO
    signed = fields.Boolean(String='Signed')
    name = fields.Many2one('account.payment',String='Payment Amount', ondelete='cascade')
    #TODO
    reason = fields.Selection([('void', 'Void'), ('loss', 'Loss'), ('cancelation','Cancelation'), ('unk', 'Unknown')], String="Reason")
    check_no = fields.Char('Check Number', size=128)
    journal_id = fields.Many2one('account.journal', String='Bank', readonly=True)   
    date_due = fields.Date(related='name.payment_date', String='Due Date', store=True)
    partner_id = fields.Many2one(related='name.partner_id', String='Beneficiary', store=True, readonly=True)
    company_id = fields.Many2one(related='name.company_id', String='Company', store=True, readonly=True)
    status = fields.Selection([('active', 'Active'), ('canceled','Canceled'), ('deleted','Deleted')], String="Check Status")
    release_at = fields.Char('Release At', size=54, Translate=True)
    description = fields.Char('Description', size=128, Translate=True)

    @api.multi
    @api.constrains('journal_id', 'check_no')
    def _check_no(self):
        """
        Constrain method to prohibit system from duplicating check no for the same 
        bank account / journal.
        
        @return: Boolean True or False
        """
        for log in self:
            checks = self.search([('journal_id','=',log.journal_id.id),('check_no','=',log.check_no),('status','!=','deleted')])
            if len(checks)>1:
                raise ValidationError(_('This check no.(%s) is already exist!') % log.check_no)

class AccountPayment(models.Model):

    _inherit = 'account.payment'

    transfer_number = fields.Integer(string="Transfer Number", readonly=True, copy=False)
    release_at = fields.Char('Release At', size=54, Translate=True)
    description = fields.Char('Description', size=128, Translate=True)


    @api.onchange('amount')
    def _onchange_amount(self):
        context = self._context or {}
        if hasattr(super(AccountPayment, self), '_onchange_amount'):
            super(AccountPayment, self)._onchange_amount()
        if context.get('lang') == 'ar_SY':
            self.check_amount_in_words = amount_to_text_ar.amount_to_text(self.amount, 'ar')
 
    @api.one
    def create_check_log(self,new_check_no,release_at):
        """ Create a check.log """
        context = self._context or {}
        cr = self._cr or False
        uid = self._uid or False
        ids = self._ids or []
        self.env['check.log'].create({
                'name': self.id,
                'status': 'active',
                'check_no': new_check_no,
                'journal_id': self.journal_id.id,
                'release_at':release_at,
                'description':self.description,
            })
    
    @api.multi
    def do_print_checks(self):
        if self.journal_id.check_dimension.id != False :
            res = {
                'payment_date':self.payment_date,
                'partner_name':self.partner_id.name,
                'check_amount_in_words':self.check_amount_in_words,
                'amount_money':self.amount,
                'release_at_name':self._context.get('release_at', False) or self.release_at,
                'description_name':self.description,
                'beneficiary':self.journal_id.check_dimension.beneficiary,
                'font_size':self.journal_id.check_dimension.font_size,
                'date':self.journal_id.check_dimension.date,
                'amount':self.journal_id.check_dimension.amount,
                'number':self.journal_id.check_dimension.number,
                'release_at':self.journal_id.check_dimension.release_at,
                'description':self.journal_id.check_dimension.description,
                }
            datas = {
            'ids': self._ids,
            'model': 'account.payment', 
            'form': res,
            }
            self.write({'state': 'sent'})
            dic=self.env.ref('account_check_printing_custom.print_check_qweb_report').report_action(self, data=datas)
            return dic
        else:
            raise UserError(_("Please add check dimensions to the selected journal in order to print a check."))


    @api.multi
    def print_checks(self):
        """ 
        Inherit to call wiz.print.check
        """
        self = self.filtered(lambda r: r.payment_method_id.code == 'check_printing' and r.state != 'reconciled')
        if len(self) == 0:
            raise UserError(_("Payments to print as a checks must have 'Check' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))
        if not self[0].journal_id.check_manual_sequencing:
            is_printed = False
            if self.check_number != 0:
                is_printed = True
            last_printed_check = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            next_check_number = last_printed_check and last_printed_check.check_number + 1 or 1
            return {
                'name': _('Print Check Report'),
                'type': 'ir.actions.act_window',
                'res_model': 'wiz.print.check',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                    'default_preprinted': is_printed,
                }
            }
        else:
            return self.do_print_checks()

    @api.multi
    def print_transfer_report(self):
        datas = {}
        [data] = self.read()
        data['payment_ids']=self.ids
        datas = {
             'ids': self._ids,
             'model': 'account.payment',
             'form': data
                }
        last_printed_transfer = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('transfer_number', '!=', 0),
                ('payment_method_code','=','transfer')], order="transfer_number desc", limit=1)
        next_transfer_number = last_printed_transfer and last_printed_transfer.transfer_number + 1 or 1
        self.write({'state': 'sent','transfer_number':next_transfer_number})
        return self.env.ref('account_check_printing_custom.bank_transfer_report_action').report_action(self, data=datas)

    def splite_amount_total(self,amount):
        """
        This method split the amount number into tow parts, before decimal point and after
        @return: list of string with tow parts
        """
        split_num = str(amount).split('.')
        return split_num 

class account_check_dimension(models.Model):
 
    _name = 'account.check.dimension'

    name = fields.Char('Name', size=54, required=True, Translate=True)
    font_size = fields.Integer('Font Size', size=54, required=True, Translate=True)
    date = fields.Char('Date', size=54, required=True, Translate=True)
    beneficiary = fields.Char('Beneficiary', size=54 , required=True, Translate=True)
    amount = fields.Char('Written Amount', size=54, required=True, Translate=True)
    number = fields.Char('Amount', size=54, required=True, Translate=True)
    release_at = fields.Char('Release At', size=54, required=True, Translate=True)
    description = fields.Char('Description', size=128, required=True, Translate=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the check dimension without removing it.")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
