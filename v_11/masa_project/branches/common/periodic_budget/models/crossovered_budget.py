from odoo import api, fields, models , _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import time


class AccountPeriodBudget(models.Model):
    _inherit = 'crossovered.budget'
    period = fields.Many2one('account.period' , string='Period')
    account_budget_line = fields.One2many('fiscalyear.budget.lines', 'fiscalyear_budget_id', 'Budget Lines')
    bugetary_position_id = fields.Many2one('account.budget.post' , string='Bugetary Position')
class accountPeriodLines(models.Model):
    _inherit = 'fiscalyear.budget.lines'
    budget_id = fields.Many2one('crossovered.budget')

