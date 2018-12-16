# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError


class BudgetReportComparison(models.TransientModel):
    _name = 'budget.custom.report.comparison'
    _inherit = 'budget.custom.report'

    # default date is first day of the previous year
    date_from_s = fields.Date(required=1,string='Date From', default=lambda self: date(date.today().year-1 , 1, 1))
    # default date is last day of the previous year
    date_to_s = fields.Date(required=1,string='Date To', default=lambda self: date(date.today().year-1 , 12, 31))

    def print_report(self,data):

        if self.date_from >= self.date_to:
            raise UserError(_('Start Date must be equal to or less than Date To'))

        if len(self.analytic_account_ids) == 0:
            raise UserError(_('You must atleast select one analytic account'))

        data = data

        # Get all filter in data Dict
        data.update({'date_from': self.date_from})
        data.update({'date_to': self.date_to})
        data.update({'date_from_s': self.date_from_s})
        data.update({'date_to_s': self.date_to_s})

        # read_group filters and we pass it to read_group
        # first period
        filters = [('date_from', '>=', self.date_from),
                   ('date_to', '<=', self.date_to),
                   ('general_budget_id.type', '=', self.budget_type),
                   ]

        # read_group filters and we pass it to read_group
        # second period
        filters_2 = [
                   ('date_from', '>=', self.date_from_s),
                   ('date_to', '<=', self.date_to_s),
            ('general_budget_id.type', '=', self.budget_type),
                   ]

        data.update({'filters':filters})
        data.update({'filters_sec':filters_2})

        # read_group fields , we pass it to read_group
        budget_fields = ['general_budget_id', 'general_budget_id.code', 'analytic_account_id', 'planned_amount',
                         'practical_amount', 'total_operation', 'transfer_amount', 'confirm', 'residual', 'percentage',
                         'deviation']

        data.update({'fields': budget_fields})

        #get all child ids
        analytic_ids = tuple(
            [line.id for line in self.env['account.analytic.account'].search(
            [('id', 'child_of', tuple(self.mapped('analytic_account_ids').ids))]
            )])

        data.update({'analytic_ids': analytic_ids})
        data2= data.copy()
        data2.update({'filters' : [('date_from', '>=', self.date_from_s),
                   ('date_to', '<=', self.date_to_s) ]})





        data.update({'analytic_ids': analytic_ids})


        data.update({'budget_type': self.budget_type})
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>")

        return self.env.ref('budget_custom_report.action_budget_comparison_report').with_context(
            landscape=True).report_action(
            self, data=data)










class budgetCustomReport(models.AbstractModel):
    _name = 'report.budget_custom_report.budget_comparison_report_tamplate'

    @api.model
    def get_report_values(self, docids, data=None):
        return {
            'data': data,
            'get':self.env['budget.custom.report'],

        }