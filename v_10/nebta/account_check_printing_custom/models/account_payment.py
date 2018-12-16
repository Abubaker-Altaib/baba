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
from odoo.tools import amount_to_text_en, float_round
from odoo.addons.account_check_printing_custom.models import amount_to_text_ar
from odoo.exceptions import UserError, ValidationError



class account_move(models.Model):
    _inherit = 'account.move'

    canceled_chk = fields.Boolean('Cancel Check')

class AccountJournal(models.Model):
    _inherit = "account.journal"

    checkno_sequence_id = fields.Many2one('ir.sequence', 'Check No. Sequence', copy=False,
        help="Checks numbering sequence.")
    grace_period = fields.Integer('Grace Period',help="Number of month that each entry of this journal is not received after this period will cancelled")
    check_dimension = fields.Many2one('account.check.dimension', 'Check dimension')

 
class check_log(models.Model):
    """
    This class for storing some data for each printed check as a 
    summary log display check info and it's state.
    """
    _name = 'check.log'
    _description = 'Check Log'
    
    signed = fields.Boolean(String='Signed')
    name = fields.Many2one('account.payment',String='Payment Amount', ondelete='cascade')
    reason = fields.Selection([('void', 'Void'), ('loss', 'Loss'), ('cancelation','Cancelation'), ('unk', 'Unknown')], String="Reason")
    check_no = fields.Char('Check Number', size=128)
    journal_id = fields.Many2one('account.journal', String='Bank', readonly=True)   
    date_due = fields.Date(related='name.payment_date', String='Due Date', store=True)
    partner_id = fields.Many2one(related='name.partner_id', String='Beneficiary', store=True, readonly=True)
    company_id = fields.Many2one(related='name.company_id', String='Company', store=True, readonly=True)
    #'date': fields.Related('name', 'date', type='date', string='Date', store=True, readonly=True),
    status = fields.Selection([('active', 'Active'), ('canceled','Canceled'), ('deleted','Deleted')], String="Check Status")

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


class account_payment(models.Model):
    """
    Inherit object payment to add function that 
    """
    _inherit = 'account.payment'

    check_amount_in_words = fields.Char(string="Amount in Words", compute='_onchange_amount')



    @api.model
    def create(self, vals):
        #To a void KeyError on payment_method_id
        if not self.payment_method_id:
            vals.update({'payment_method_id': ''})
        res = super(account_payment, self.sudo()).create(vals)
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
                'name': self.id,
                'status': 'active',
                'check_no': self.check_number,
                'journal_id': self.journal_id.id,
            })
        self.env['ir.sequence'].browse(self.journal_id.checkno_sequence_id.id).number_next =  self.check_number + 1
    @api.model
    def print_check_report(self):
        if self.journal_id.check_dimension.id != False :
           res = {
                'payment_date':self.payment_date,
                #'partner_name':self.partner_id.name,
                'partner_name':self.beneficiary_id.name,
                'check_amount_in_words':self.check_amount_in_words,
                'amount_money':self.amount,
                'beneficiary':self.journal_id.check_dimension.beneficiary,
                'font_size':self.journal_id.check_dimension.font_size,
                'date':self.journal_id.check_dimension.date,
                'amount':self.journal_id.check_dimension.amount,
                'number':self.journal_id.check_dimension.number
                }
           data = self.read(self)[0]
           datas = {
            'ids': self._ids,
            'model': 'account.payment', # wizard model name
            'form': res,
            'context':self.env.context
            }
           dic = {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_check_printing_custom.print_check_custom',#module name.report template name
            'datas': datas,
               } 
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
        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        self = self.filtered(lambda r: r.payment_method_id.code == 'check_printing' and r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(_("Payments to print as a checks must have 'Check' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        self.filtered(lambda r: r.state == 'draft').post()
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
                    'payment_ids': self.ids,
                    'default_next_check_number': self._get_next_check_no()[0],
		            'default_preprinted': is_printed,
                }
            }
        else:
            return self.do_print_checks()

    def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'account.payment',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_check_printing_custom.bank_letter_report',
            'datas': datas,
            }
    
    @api.one
    @api.depends('amount')
    def _onchange_amount(self):
        context = self._context or {}
        if hasattr(super(account_payment, self), '_onchange_amount'):
            super(account_payment, self)._onchange_amount()
        if context.get('lang') == 'ar_SY':
            self.check_amount_in_words = amount_to_text_ar.amount_to_text(self.amount, 'ar')


class account_check_dimension(models.Model):
 
    _name = 'account.check.dimension'

    name = fields.Char('Name', size=54, required=True, Translate=True)
    font_size = fields.Integer('Font Size', size=54, required=True, Translate=True)
    date = fields.Char('Date', size=54, required=True, Translate=True)
    beneficiary = fields.Char('Beneficiary', size=54 , required=True, Translate=True)
    amount = fields.Char('Written Amount', size=54, required=True, Translate=True)
    number = fields.Char('Amount', size=54, required=True, Translate=True)


class account_payment_custom(models.Model):
    _inherit = "account.payment"

    #V9:this field was add to add constrain to the print check button that not appear when the type is cash
    journal_type = fields.Selection(related='journal_id.type')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
