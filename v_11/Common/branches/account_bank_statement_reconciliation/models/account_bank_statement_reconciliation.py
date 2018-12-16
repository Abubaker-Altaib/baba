# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models,_
from odoo.osv import expression


#----------------------------------------------------------
# Entries Inherit
#----------------------------------------------------------
class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.model
    def _default_opening_journal_balance(self):
        #Search last bank statement and set current opening journal balance as closing journal balance of previous one
        journal_id = self._context.get('default_journal_id', False) or self._context.get('journal_id', False)
        if journal_id:
            return self._get_opening_journal_balance(journal_id)
        return 0

    @api.multi
    def _get_opening_balance(self, journal_id):
        last_bnk_stmt = self.search([('journal_id', '=', journal_id),('id', '!=', self._origin.id),('state', '=', 'confirm')], limit=1)
        if last_bnk_stmt:
            return last_bnk_stmt.balance_end
        return 0

    balance_Journal_end = fields.Float('Journal Ending Balance',compute='_Journal_end_balance',store=True)
    balance_Journal_start = fields.Float('Journal Start Balance',states={'confirm': [('readonly', True)]}, default=_default_opening_journal_balance)
    bank_total_of_debit= fields.Monetary('Journal Start Balance',compute='_balance_end_real')
    bank_total_of_credit= fields.Monetary('Journal Start Balance',compute='_balance_end_real')
    total_of_debit= fields.Monetary('Journal Start Balance',compute='_Journal_end_balance')
    total_of_credit= fields.Monetary('Journal Start Balance',compute='_Journal_end_balance')
    move_line_to_reconcile_ids = fields.One2many('account.move.line', 'statement_to_reconcile_id', string='Entry lines To Reconcile', states={'confirm': [('readonly', True)]},domain=[('statement_line_id', '=', False)])
    journal_debit_account_id=fields.Many2one('account.account', related='journal_id.default_debit_account_id',readonly=True)
    journal_credit_account_id=fields.Many2one('account.account', related='journal_id.default_credit_account_id',readonly=True)
    balance_end = fields.Monetary('Computed Balance', compute='_end_balance_compute', store=True, help='Balance as calculated based on Reconciled transaction')

    @api.multi
    def _get_opening_journal_balance(self, journal_id):
        last_bnk_stmt = self.search([('journal_id', '=', journal_id),('id', '!=', self._origin.id),('state', '=', 'confirm')], limit=1)
        if last_bnk_stmt:
            return last_bnk_stmt.balance_Journal_end
        return 0

    @api.one
    @api.depends('move_line_ids')
    def _end_balance_compute(self):
        if self.move_line_ids:
            self.balance_end=sum([line.debit for line in self.move_line_ids]) - sum([line.credit for line in self.move_line_ids])

    @api.multi
    def _set_opening_balance(self, journal_id):
        self.balance_Journal_start = self._get_opening_journal_balance(journal_id)
        return super(AccountBankStatement, self)._set_opening_balance(journal_id)


    @api.multi
    def account_statement_line_refresh(self):
        if self.line_ids:
            for line in self.line_ids :
                if line.ref:
                    if not line.partner_id:
                        payment=self.env['account.payment']
                        payment_part=payment.search([('communication','=', line.ref)])
                        for par in payment_part:

                            line.partner_id=par.partner_id

    @api.multi
    def get_to_reconcile_lines(self):
        domin=[]
        reconciliation_aml_accounts = [self.journal_id.default_credit_account_id.id, self.journal_id.default_debit_account_id.id]
        domin = [('reconciled', '=', False),('statement_line_id', '=', False), ('account_id', 'in', reconciliation_aml_accounts), ('date_maturity','<=',self.date),('payment_id','<>', False),('move_id.state','=','posted')]
        line_ids = self.env['account.move.line'].search(domin,order="date_maturity desc, id desc")
        line_ids.write({'statement_to_reconcile_id':self.id})
    
    @api.one
    @api.depends('journal_id','move_line_ids')
    def _Journal_end_balance(self):
        default_debit_account,default_credit_account=False,False
        if self.journal_id and self.journal_id.default_debit_account_id and self.journal_id.default_credit_account_id:
            default_debit_account=self.journal_id.default_debit_account_id.id
            default_credit_account=self.journal_id.default_credit_account_id.id
        self.env.cr.execute("SELECT sum(aml.debit) as debit FROM account_move_line aml join account_move m on (aml.move_id = m.id) \
            WHERE m.state = 'posted' AND aml.account_id =%s AND aml.date <= %s" ,(default_debit_account,self.date))
        debit=self.env.cr.dictfetchall()[0]['debit'] or 0.0

        self.env.cr.execute("SELECT sum(aml.credit) as credit FROM account_move_line aml join account_move m on (aml.move_id = m.id) \
            WHERE m.state = 'posted' AND aml.account_id =%s AND aml.date <= %s" ,(default_credit_account,self.date))
        credit=self.env.cr.dictfetchall()[0]['credit'] or 0.0

        self.balance_Journal_end= debit - credit
        lists = []
        params = {'account_id': self.journal_id.default_debit_account_id.id,}
        sql_query="SELECT aml.balance ,aml.id FROM account_move_line aml WHERE aml.reconciled = false AND aml.account_id =%(account_id)s"
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.dictfetchall()
        for line in results:
            if line['balance']>0:
                self.total_of_debit+=line['balance']
            else:
                self.total_of_credit+=line['balance']
        self.total_of_credit=abs(self.total_of_credit)


    @api.one
    @api.depends('line_ids.journal_entry_ids','balance_Journal_end',)
    def _balance_end_real(self):
        lists = []
        params = {'account_id': self.journal_id.default_debit_account_id.id,}
        sql_query="SELECT aml.balance ,aml.id FROM account_move_line aml WHERE aml.reconciled = false AND aml.account_id =%(account_id)s"
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.dictfetchall()
        for line in results:
            if line['balance'] > 0:
                self.bank_total_of_debit+=line['balance']
            else:
                self.bank_total_of_credit+=line['balance']
        self.bank_total_of_credit=abs(self.bank_total_of_credit)

    @api.one
    @api.depends('line_ids', 'balance_start', 'line_ids.amount',"line_ids.journal_entry_ids", 'balance_end_real')
    def _end_balance(self):
        self.total_entry_encoding = sum([line.amount for line in self.line_ids])
        self.difference = self.balance_end_real - self.balance_end

    @api.multi
    def reconcilation_report(self):
        return self.env.ref('account_bank_statement_reconciliation.report_reconcilation').report_action(self)


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.multi
    def button_cancel_reconciliation(self):
        aml_to_unbind = self.env['account.move.line']
        aml_to_cancel = self.env['account.move.line']
        payment_to_unreconcile = self.env['account.payment']
        payment_to_cancel = self.env['account.payment']
        for st_line in self:
            aml_to_unbind |= st_line.journal_entry_ids
            for line in st_line.journal_entry_ids:
                payment_to_unreconcile |= line.payment_id
                if st_line.move_name and line.payment_id.payment_reference == st_line.move_name:
                    #there can be several moves linked to a statement line but maximum one created by the line itself
                    aml_to_cancel |= line
                    payment_to_cancel |= line.payment_id
        aml_to_unbind = aml_to_unbind - aml_to_cancel

        if aml_to_unbind:
            aml_to_unbind.write({'statement_line_id': False})

        payment_to_unreconcile = payment_to_unreconcile - payment_to_cancel
        if payment_to_unreconcile:
            payment_to_unreconcile.unreconcile()

        if aml_to_cancel:
            aml_to_cancel.remove_move_reconcile()
            moves_to_cancel = aml_to_cancel.mapped('move_id')
            moves_to_cancel.button_cancel()
            moves_to_cancel.unlink()
        if payment_to_cancel:
            payment_to_cancel.unlink()



#For Revert Bank Reconciliations
class AccountJournal(models.Model):
    _inherit = "account.journal"

    journal_parent = fields.Many2one('account.journal',string='Journal Parent')
    update_posted = fields.Boolean(string='Allow Cancelling Entries' ,default = True ,
        help="Check this box if you want to allow the cancellation the entries related to this journal or of the invoice related to this journal")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    statement_to_reconcile_id = fields.Many2one('account.bank.statement', index=True, string='Bank statement line To be reconciled with this entry', copy=False, readonly=True)

    @api.multi
    def do_reconcile_lines(self):
        for line in self:
            flag=False
            if line.statement_to_reconcile_id.line_ids:
                for stm_line in line.statement_to_reconcile_id.line_ids:
                    if (stm_line.amount < 0 and abs(stm_line.amount) == line.debit) and line.ref == stm_line.ref:
                        if stm_line.partner_id:
                            if stm_line.partner_id == line.partner_id:
                                flag=True
                                line.write({'statement_id':line.statement_to_reconcile_id.id})
                                line.write({'statement_line_id':stm_line.id})
                        else:
                            flag=True
                            line.write({'statement_id':line.statement_to_reconcile_id.id})
                            line.write({'statement_line_id':stm_line.id})
                    elif (stm_line.amount > 0 and stm_line.amount == line.credit) and line.ref == stm_line.ref:
                        if stm_line.partner_id:
                            if stm_line.partner_id == line.partner_id:
                                flag=True
                                line.write({'statement_id':line.statement_to_reconcile_id.id})
                                line.write({'statement_line_id':stm_line.id})
                        else:
                            flag=True
                            line.write({'statement_id':line.statement_to_reconcile_id.id})
                            line.write({'statement_line_id':stm_line.id})
                if not flag:
                    line.write({'statement_id':line.statement_to_reconcile_id.id})
                    new_stm_line=self.env['account.bank.statement.line'].create({'statement_id':line.statement_to_reconcile_id.id,
                                                                    'amount':line.debit and abs(line.debit) or abs(line.credit),
                                                                    'date':line.date,'ref':line.ref,'name':line.name,'partner_id':line.partner_id and line.partner_id.id or False,
                                                                    })
                    line.write({'statement_line_id':new_stm_line.id})
            else:
                line.write({'statement_id':line.statement_to_reconcile_id.id})
                new_stm_line=self.env['account.bank.statement.line'].create({'statement_id':line.statement_to_reconcile_id.id,
                                                                'amount':line.debit and abs(line.debit) or line.credit * -1,
                                                                'date':line.date,'ref':line.ref,'name':line.name,'partner_id':line.partner_id and line.partner_id.id or False,
                                                                })
                line.write({'statement_line_id':new_stm_line.id})

