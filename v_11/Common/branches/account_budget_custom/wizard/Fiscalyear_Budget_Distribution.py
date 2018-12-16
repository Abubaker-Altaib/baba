# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class fiscalyear_budget_distribution(models.TransientModel):
    """
        Budget Distribution
    """
    _name = "fiscalyear.budget.distribution"
    _description = "Budget Distribution"


    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic account", required=True, domain=[('type', '=', 'normal')])
    fiscal_year_id = fields.Many2one('account.fiscalyear', string="year", required=True, domain=[('state', '=', 'draft')])
    amount = fields.Float('Amount')

    @api.multi
    @api.constrains('amount')
    def _check_amount(self):
        for obj in self:
            if obj.amount <= 0:
                raise ValidationError(_('The Amount must be grater than zero.'))

    @api.multi
    def Budget_Distribution(self):
        """
            This function distribute budget
        """  
        periods = self.env['account.period'].search([('fiscalyear_id','=',self.fiscal_year_id.id),('special','!=',True)])

        # create crossovered.budget for every period 
        for period in periods:
            name = self.analytic_account_id.name+"/"+period.name
            analytic_account_id = self.analytic_account_id.id
            creating_user_id = self.analytic_account_id.user_id
            date_from = period.date_start
            date_to = period.date_stop
            period_amount = self.amount/period_num
            values = {
                'name': name,
                'creating_user_id': creating_user_id.id,
                'date_from':date_from,
                'date_to': date_to,
                'amount': period_amount,
                'analytic_account_id': analytic_account_id,
            }
            self.env['crossovered.budget'].create(values)

