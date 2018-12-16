# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_permanent = fields.Boolean("Is Permanent")

class ResJournal(models.Model):
    _inherit = 'account.journal'

    is_resource = fields.Boolean("Is Resource")
    Partner_id=fields.Many2one('res.partner', 'Customer')
    analytic_account_id=fields.Many2one('account.analytic.account', 'Analytic Account')

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    is_resource = fields.Boolean("Is Resource")


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
    
    res_journal_id=fields.Many2one('account.journal', 'Bank Account')

class PermanentOrder(models.Model):
    _name = 'permanent.order'

    Partner_id=fields.Many2one('res.partner', 'Customer')
    analytic_account_id=fields.Many2one('account.analytic.account', 'Analytic Account')
    payment_journal_id=fields.Many2one('account.journal', 'Payment Journal')
    start_date= fields.Date('Start Date')
    end_date= fields.Date('End Date')
    payment_date= fields.Date('Payment Date')
    amount= fields.Float(string="Amount")
    payment_amount= fields.Float(string="Payment Amount")
    payment_ids=fields.Many2one('account.move.line', 'Payment')
    active = fields.Boolean("Active")
    