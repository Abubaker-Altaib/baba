# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from datetime import date, datetime, timedelta

################################################# Budget Custom Reports Common ######################################
#All budge custom report functions HERE ^_^
#WE used read_group in all functions , just send the right parameters and your day will be saved ^_^
#Any Question just Ask Me Mudathir

class budgetCustomReport(models.TransientModel):
    _name = 'budget.custom.report'

    analytic_account_ids = fields.Many2many('account.analytic.account',domain=[('type','=','view')])
    budgetry_position_ids = fields.Many2many('account.budget.post')
    budget_type = fields.Selection([('in', 'Revenue'),
                                    ('out', 'Expense')],
                                   required=1, default='out')

                                        # default date is first day of the current year
    date_from = fields.Date(required=1, default=lambda self: date(date.today().year, 1, 1))
                                        # default date is last day of the current year
    date_to = fields.Date(required=1, default=lambda self: date(date.today().year, 12, 31))


    @api.onchange('budget_type')
    def empty_budgetry_position(self):
        """
        In case user select budgetry postion belong to expense then change budget type to Revenue or vise versa
        """
        self.budgetry_position_ids = False




    def get_analytic_info(self, id, data):
        """
        Desc : pass id of analytic account to get all data about it

        """
        info = self.env['account.analytic.account'].search([('id','=',id)])
        return info


    def get_analytic_summation(self,id,data):
        """
        Desc : get total data of analytic without budgetry positiin filter in search domain

        """

        analytic_ids = data.get('analytic_ids')
        filters = data['filters'].copy()
        filters.append(['analytic_account_id','child_of',id])

        data = self.env['crossovered.budget.lines'].read_group(filters,data['fields'],
                                                               [])

        return data[0]['practical_amount'] != None and data or []


    def get_analytic_summation_with_budgetry(self,id,data):
        """
        Desc: get data of analytic for spicific budgetry positions

        """

        analytic_ids = data.get('analytic_ids')
        budgetry = data.get('budgetary_ids')
        filters = data['filters'].copy()
        filters.append(['analytic_account_id', 'child_of', id])
        filters.append(['general_budget_id', 'in', budgetry])

        data = self.env['crossovered.budget.lines'].read_group(filters, data['fields'],
                                                               [])
        return data[0]['practical_amount'] != None and data or []




    def get_analytic_budgetry_positions(self , id , data):
        """
        Desc: get analytic budgetry data grouped by budgetry position
        """
        analytic_ids = data.get('analytic_ids')
        filters = data['filters'].copy()
        filters.append(['analytic_account_id', 'child_of', id])

        #in case user select budgetry positon
        if data.get('budgetary_ids',False):
            budgetry_ids = data.get('budgetary_ids',False)
            filters.append(['general_budget_id', 'in', budgetry_ids])

        data = self.env['crossovered.budget.lines'].read_group(filters, data['fields'],['general_budget_id'])

        return data[0]['practical_amount'] != None and data or []


    def get_budgetry_positions(self,data):
        """
        Desc : Get budget information about budgetry position
        """

        budgetry_ids = data.get('budgetary_ids')

        filters = data['filters'].copy()
        # we can also use len(budgetry_ids) != 0: ^_^
        if len(budgetry_ids) > 0:
            filters.append(['general_budget_id', 'in', budgetry_ids])
        data = self.env['crossovered.budget.lines'].read_group(filters, data['fields'] ,['general_budget_id'])
        return data[0]['practical_amount'] != None and data or []




    def get_analytic_summation_period(self,id,data):
        """
        Desc : get budget data of analytic in 2 periods to compare between them
        """
        # First Periode
        analytic_ids = data.get('analytic_ids')
        filters = data['filters'].copy()
        filters.append(['analytic_account_id','child_of',id])

        first_period_result = self.env['crossovered.budget.lines'].read_group(filters,data['fields'],
                                                               [])
        #Second Periode
        filters_sec = data['filters_sec'].copy()
        filters_sec.append(['analytic_account_id', 'child_of', id])

        second_period_result = self.env['crossovered.budget.lines'].read_group(filters_sec, data['fields'],
                                                               [])
        # return result
        return first_period_result,second_period_result