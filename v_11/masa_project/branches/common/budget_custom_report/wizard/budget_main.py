# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


####################################### Budget Custom Reports ##################################################################


class BudgetReportMain(models.TransientModel):
    _name = 'budget.custom.report.main'
    _inherit = 'budget.custom.report'

    report_show = fields.Selection([('sum', 'Summation'),
                                    ('details', 'Details')],default ='sum')

    report_type = fields.Selection([('cost_center', 'By Cost Centers'),
                                    ('bud_position', 'By Budgetry Position')],
                                   required=1, default='cost_center')



    budgetry_position_show = fields.Selection([('without_analytic','Only Budgetry Positons'),
                                               ('with_analytic','With Analytics')],default='without_analytic')



    def print_report(self,data):

        if self.date_from > self.date_to:
            raise ValidationError(_('Start Date must be equal to or less than Date To'))

        # starter filter ^_^
        data = data 

        #Get all filter in data Dict
        data.update({'report_type': self.report_type})
        data.update({'report_show': self.report_show})
        data.update({'budget_type': self.budget_type})
        data.update({'date_from': self.date_from})
        data.update({'date_to': self.date_to})

        #read_group filters and pass it to all functions we need
        filters = [('date_from', '>=', self.date_from),
                   ('date_to', '<=', self.date_to),
                   ('general_budget_id.type', '=', self.budget_type)
                   ]

        data.update({'filters': filters})

        #read_group fields , pass it to all functions that have read_group
        budget_fields = ['general_budget_id', 'general_budget_id.code', 'analytic_account_id', 'planned_amount',
                         'practical_amount', 'total_operation', 'transfer_amount', 'confirm','residual','percentage',
                         'deviation']

        data.update({'fields': budget_fields})

        if self.report_type == 'cost_center':
            #if user not select any analytic then select all analytics
            if len(self.mapped('analytic_account_ids')) == 0:
                analytic_ids = self.env['account.analytic.account'].search([],order='code').ids
            else:
                tuple_analytic_ids = tuple(self.mapped('analytic_account_ids').ids)
                analytic_ids = tuple([line.id for line in self.env['account.analytic.account'].search([('id','child_of',tuple_analytic_ids)])])

            data.update({'analytic_ids':analytic_ids})

        elif self.report_type == 'bud_position':
            #budgetry_position_type
            data.update({'budgetry_position_show': self.budgetry_position_show})

            # if user not select any Budgetary then select all Budgetaries
            if len(self.mapped('budgetry_position_ids')) == 0:
                budgetary_ids = self.env['crossovered.budget.lines'].search([]).ids
            else:
                tuple_budgetary_ids = tuple(self.mapped('budgetry_position_ids').ids)
                budgetary_ids = tuple([line.id for line in self.env['crossovered.budget.lines'].search(
                    [('id', 'in', tuple_budgetary_ids)])])

            data.update({'budgetary_ids': budgetary_ids})

            if self.budgetry_position_show == 'with_analytic':
                # if user not select any analytic then select all analytics
                if len(self.mapped('analytic_account_ids')) == 0:
                    analytic_ids = self.env['account.analytic.account'].search([], order='code').ids
                else:
                    tuple_analytic_ids = tuple(self.mapped('analytic_account_ids').ids)
                    analytic_ids = tuple([line.id for line in self.env['account.analytic.account'].search(
                        [('id', 'child_of', tuple_analytic_ids)])])

                data.update({'analytic_ids': analytic_ids})


        return self.env.ref('budget_custom_report.action_budget_custom_report').with_context(landscape=True).report_action(
            self, data=data)







class budgetCustomReport(models.AbstractModel):
    _name = 'report.budget_custom_report.budget_main_report_tamplate'

    @api.model
    def get_report_values(self, docids, data=None):
        return {
            'data': data,
            'get':self.env['budget.custom.report'],
            'current_model': self.env['budget.custom.report.main']
        }
