import calendar
from odoo import api, fields, models, exceptions, _
from datetime import date, datetime
from dateutil import relativedelta
from odoo.tools import ustr


class AccountFiscalYearBudget(models.Model):
    _name = 'account.fiscalyear.budget'

    name = fields.Char()
    code = fields.Char()
    type = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')], required=True, default='in')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', ondelete='restrict')
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.uid)
    account_budget_line = fields.One2many('fiscalyear.budget.lines', 'fiscalyear_budget_id', 'Budget Lines')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Canceld')], default='draft')
    intervals = fields.Many2one('fiscalyear.budget.config', string='Budgetary Intervals')
    date_from = fields.Date()
    date_to = fields.Date()
    amount = fields.Float(string='Amount')

    @api.multi
    def action_budget_draft(self):
        """
        Set State To Cancel
        :return:
        """
        self.write({'state': 'draft'})

    @api.multi
    def action_budget_cancel(self):
        """
        Set State To Cancel
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_budget_confirm(self):
        """
        Create and Distribute Budget Based on Intervals Value
        :return:
        """
        no_budget = 12 / int(self.intervals.months)
        no_months = int(self.intervals.months)
        date_from = self.date_from
        date_to = ''
        lines = []
        for i in range(int(no_budget)):
            if i == 0:
                date_to = datetime.strptime(date_from, '%Y-%m-%d')
                date_to = date_to.replace(month=date_to.month + no_months - 1)
                day = calendar.monthrange(date_to.year, date_to.month)[1]
                date_to = date_to.replace(day=day)
            elif i != 0:
                date_from = date_to.replace(month=date_to.month + 1, day=1)
                date_to = date_from.replace(month=date_from.month + no_months - 1)
                day = calendar.monthrange(date_to.year, date_to.month)[1]
                date_to = date_to.replace(day=day)

            for line in self.account_budget_line:
                lines += [(0, 6, {
                    'general_budget_id': line.general_budget_id.id,
                    'analytic_account_id': self.analytic_account_id.id,
                    'planned_amount': line.planned_amount / no_budget,
                    'date_from': date_from,
                    'date_to': date_to,
                })]

            self.env['crossovered.budget'].create(
                {
                    'name': self.name,
                    'date_from': date_from,
                    'date_to': date_to,
                    'analytic_account_id': self.analytic_account_id.id,
                    'company_id': self.company_id.id,
                    'creating_user_id': self.user_id.id,
                    'type': self.type,
                    'crossovered_budget_line': lines,
                }
            )
            lines = []
        self.write({'state': 'confirm'})

    @api.model
    def get_seq_to_view(self):
        """
        Get sequence in code filed in form view
        :return:
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        """
        set sequence number for any new record created
        :param vals: fields values from view
        :return: dict
        """
        account_code = self.env['account.analytic.account'].search([('id', '=', vals['analytic_account_id'])])
        # set new sequence number in code for every new record
        vals['name'] = self.env['ir.sequence'].get(self._name) + '-' + account_code.name + '-' + account_code.code or '/'
        return super(AccountFiscalYearBudget, self).create(vals)

    @api.constrains('date_from', 'date_to', 'amount')
    def field_validation(self):
        amount = 0
        date_from = datetime.strptime(str(self.date_from), '%Y-%m-%d')
        date_to = datetime.strptime(str(self.date_to), '%Y-%m-%d')
        periods = relativedelta.relativedelta(date_to, date_from)
        year = int(periods.years)
        months = int(periods.months)
        days = int(periods.days)
        if year != 0 or months != 11 or (days != 31 and days != 30):
            raise exceptions.ValidationError(_("Period Cannot Be More or Less Than one Year"))
        if self.date_to <= self.date_from:
            raise exceptions.ValidationError(_("Date From Must Be Greater Than Date To"))
        if self.amount <= 0:
            raise exceptions.ValidationError(_("Amount Must Be Greater Than Zero"))
        for i in self.account_budget_line:
            amount += i.planned_amount
        if amount < self.amount or amount > self.amount:
            raise exceptions.ValidationError(_("Amonut Must Equal Budget Line Amount"))


class FiscalyearBudgetLinesCustom(models.Model):
    _name = "fiscalyear.budget.lines"

    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position', required=True)
    fiscalyear_budget_id = fields.Many2one('account.fiscalyear.budget', 'Budget', ondelete='cascade', index=True,
                                           required=False)
    paid_date = fields.Date('Paid Date')
    planned_amount = fields.Float('Planned Amount', required=False, digits=0)
    practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount', digits=0)
    theoritical_amount = fields.Float(compute='_compute_theoritical_amount', string='Theoretical Amount', digits=0)
    percentage = fields.Float(compute='_compute_percentage', string='Achievement')
    company_id = fields.Many2one(related='fiscalyear_budget_id.company_id', comodel_name='res.company',
                                 string='Company', store=True, readonly=True)

    @api.multi
    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids            
            date_to = self.env.context.get('wizard_date_to') or line.fiscalyear_budget_id.date_to
            date_from = self.env.context.get('wizard_date_from') or line.fiscalyear_budget_id.date_from
            if line.fiscalyear_budget_id.analytic_account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id=%s
                        AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                        AND general_account_id=ANY(%s)""",
                                    (line.fiscalyear_budget_id.analytic_account_id.id, date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result

    @api.multi
    def _compute_theoritical_amount(self):
        today = fields.Datetime.now()
        for line in self:
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

    @api.multi
    def _compute_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.theoritical_amount) * 100
            else:
                line.percentage = 0.00
