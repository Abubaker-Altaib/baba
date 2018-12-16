from odoo import api , fields,exceptions, models,_
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError


class print_budget_lines_wizard(models.TransientModel):
    _name = "print.budget.lines.wizard"

    parent_account_id = fields.Many2one('account.account', string='Parent Account' )
    analatic_account_id = fields.Many2one('account.analytic.account' , string='Analytic Account' , required=True)
    year = fields.Char('Year' , required=True)

    def print_report(self, data):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'crossovered.budget.lines',
            'parent_account_id': data['parent_account_id'],
            'analatic_account_id': data['analatic_account_id'],
            'year': data['year']
            }
        return self.env.ref('account_budget_ebs.print_budget_lines').report_action(self, data=datas)
