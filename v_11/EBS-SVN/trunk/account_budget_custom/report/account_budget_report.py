# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import tools
from odoo import models, fields, api


class AccountBudgetReport(models.Model):
    _name = "account.budget.report"
    _description = "Budget Statistics"
    _auto = False

            
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    tags = fields.Many2one('account.analytic.tag', 'Analytic tags')
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position', required=True)
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    paid_date = fields.Date('Paid Date')
    planned_amount = fields.Float('Planned Amount',digits=0)
    practical_amount = fields.Float(string='Practical Amount', digits=0)
    theoritical_amount = fields.Float(string='Theoretical Amount', digits=0)
    residual = fields.Float(string='Residual Balance', digits=0)
    percentage = fields.Float(string='Achievement',group_operator="avg")
    company_id = fields.Many2one('res.company', string='Company')
    total_operation= fields.Float(string='In/De-crease Amount',digits=0)
    confirm= fields.Float(string='Confirm Amount',digits=0)
    deviation=fields.Float(string="deviation",group_operator="avg")
    debit_practical_amount = fields.Float(string='Debit Practical Amount', digits=0)
    credit_practical_amount = fields.Float(string='Credit Practical Amount', digits=0)
    debit_credit_residual = fields.Float(string='Debit Credit Residual', digits=0)

            


    def _select(self):
        select_str = """
            SELECT l.* , t.tag_id As tags
        """
        return select_str

    def _from(self):
        from_str = """
                FROM crossovered_budget_lines l 
                LEFT JOIN account_analytic_account_tag_rel t ON (l.analytic_account_id = t.account_id) 
        """
        return from_str


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                
            )
        """ % (self._table, self._select(), self._from())
        )
