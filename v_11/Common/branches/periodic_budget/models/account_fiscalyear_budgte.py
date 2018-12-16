from odoo import api, fields, models , _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import time


class AccountFiscalYearBudget(models.Model):
    _inherit = 'account.fiscalyear.budget'
    period_id = fields.Many2one('account.fiscalyear' , string='Period')
    bugetary_position_id = fields.Many2one('account.budget.post' , string='Bugetary Position')
    @api.model
    def create(self, vals):
        """
        set sequence number for any new record created
        :param vals: fields values from view
        :return: dict
        """
  
        # set new sequence number in code for every new record
        analytic_account = self.env['account.analytic.account'].search([('id' , '=' , vals['analytic_account_id'])])
        vals['name'] = self.env['ir.sequence'].get(self._name) + '-' + analytic_account.code or '/'
        return super(AccountFiscalYearBudget, self).create(vals)
    @api.constrains('amount')
    def field_validation(self):
        if self.amount<=0:
            raise ValidationError(_("Amount Must Be Greater Than Zero"))
    @api.multi
    def action_budget_confirm(self):
        """
        Create and Distribute Budget Based on Intervals Value
        :return:
        """
        lines = []
        for i in self.period_id.period_ids:
            for line in self.account_budget_line:
                lines += [(0, 6, {
                    'general_budget_id': line.general_budget_id.id,
                    'analytic_account_id': self.analytic_account_id.id,
                    'planned_amount': line.planned_amount / len(self.period_id.period_ids),
                    'date_from': i.date_start,
                    'date_to': i.date_stop,
                })]

            self.env['crossovered.budget'].create(
                {
					'date_from':i.date_start,
                    'date_to':i.date_stop,
                    'amount':self.amount/len(self.period_id.period_ids),
                    'name': i.name,
                    'period': i.id,
                    'analytic_account_id': self.analytic_account_id.id,
                    'company_id': self.company_id.id,
                    'creating_user_id': self.user_id.id,
                    'type': 'out',
                    'crossovered_budget_line': lines,
                    
                }
            )
            lines = []
        self.write({'state':'confirm'})
    
    @api.multi
    def action_budget_draft(self):
        self.write({'state':'draft'})
    @api.multi
    def action_budget_cancel(self):
        self.write({'state':'cancel'})
class FiscalyearBudgetLinesCustom(models.Model):
     _inherit = 'fiscalyear.budget.lines'
     @api.multi
     def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            if not acc_ids:
                raise exceptions.UserError(_("The Budget '%s' has no accounts!") % ustr(line.general_budget_id.name))
            if line.fiscalyear_budget_id.analytic_account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id=%s
                        AND general_account_id=ANY(%s)""",
                                    (line.fiscalyear_budget_id.analytic_account_id.id, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result

     @api.multi
     def _compute_theoritical_amount(self):
        today = fields.Datetime.now()
        '''for line in self:
            # Used for the report

            if self.env.context.get('wizard_date_from') and self.env.context.get('wizard_date_to'):
                date_from = fields.Datetime.from_string(self.env.context.get('wizard_date_from'))
                date_to = fields.Datetime.from_string(self.env.context.get('wizard_date_to'))
                if date_from < fields.Datetime.from_string(line.date_from):
                    date_from = fields.Datetime.from_string(line.fiscalyear_budget_id.date_from)
                elif date_from > fields.Datetime.from_string(line.fiscalyear_budget_id.date_to):
                    date_from = False

                if date_to > fields.Datetime.from_string(line.fiscalyear_budget_id.date_to):
                    date_to = fields.Datetime.from_string(line.fiscalyear_budget_id.date_to)
                elif date_to < fields.Datetime.from_string(line.fiscalyear_budget_id.date_from):
                    date_to = False

                theo_amt = 0.00
                if date_from and date_to:
                    line_timedelta = fields.Datetime.from_string(
                        line.fiscalyear_budget_id.date_to) - fields.Datetime.from_string(line.date_from)
                    elapsed_timedelta = date_to - date_from
                    if elapsed_timedelta.days > 0:
                        theo_amt = (
                                           elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
            else:
                if line.paid_date:
                    if fields.Datetime.from_string(line.fiscalyear_budget_id.date_to) <= fields.Datetime.from_string(
                            line.paid_date):
                        theo_amt = 0.00
                    else:
                        theo_amt = line.planned_amount
                else:
                    line_timedelta = fields.Datetime.from_string(
                        line.fiscalyear_budget_id.date_to) - fields.Datetime.from_string(
                        line.fiscalyear_budget_id.date_from)
                    elapsed_timedelta = fields.Datetime.from_string(today) - (
                        fields.Datetime.from_string(line.fiscalyear_budget_id.date_from))

                    if elapsed_timedelta.days < 0:
                        # If the budget line has not started yet, theoretical amount should be zero
                        theo_amt = 0.00
                    elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(
                            line.fiscalyear_budget_id.date_to):
                        # If today is between the budget line date_from and date_to
                        theo_amt = (
                                           elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                    else:
                        theo_amt = line.planned_amount

            line.theoritical_amount = theo_amt
'''
