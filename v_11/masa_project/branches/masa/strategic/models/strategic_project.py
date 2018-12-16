# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import UserError, ValidationError


class AccountAnalytic(models.Model):
    """
    Inherit analytic object to add 
    """

    _inherit = "account.analytic.account"

    missions_ids=fields.Many2many('strategic.mission', String='Strategic Missions')
    visions_ids=fields.Many2many('strategic.visions', String='Strategic Visions')
    values_ids=fields.Many2many('strategic.values', String='Strategic Values')
    policy_ids=fields.Many2many('strategic.policy', String='Strategic Policys')
    amount= fields.Float(String="Amount")
    date_start=fields.Date(String='Start date',index=True,copy=False)
    date_end=fields.Date(String='End date',index=True,copy=False)
    project=fields.Boolean("Project")
    project_id=fields.Many2one('account.analytic.account', String='Old Project',domain="[('project','=', True)]")
    state=fields.Selection([
            ('draft','Draft'),
            ('open','Open'),
            ('done','Done'),
            ('suspend','Suspend')],default="draft",index=True,required=True,readonly=True,copy=False)
    linked_to_kpi=fields.Boolean("Linked To Kpi")

    @api.constrains('date_start','date_end')
    def _check_date_overlap(self):
        if self.date_start  and self.date_end:
            overlap_ids = self.search([('date_start','>',self.date_end),('date_end','<',self.date_start)])
            if overlap_ids:
                raise ValidationError(_(" End Date must be Greater than Start Date."))

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def set_open(self):
        self.write({'state': 'open'})

    @api.multi
    def set_suspend(self):
        self.write({'state': 'suspend'})
        
    @api.multi
    def set_done(self):
        self.write({'state': 'done'})



class AccountBudgetOperation(models.Model):

    _inherit = "account.budget.operation"

    transfer_to=fields.Selection([
            ('analytic','Analytic'),
            ('project','Project')],default="analytic",index=True,required=True,copy=False,String="Transfer_to")

    @api.onchange('transfer_to')
    def onchange_transfer_to(self):
        if self.transfer_to=="project":
            return {
                'domain': {
                    'to_analytic_account_id': [('project', '=',True)] ,
                }
            }
        if self.transfer_to=="analytic":
            return {
                'domain': {
                    'to_analytic_account_id': [('project', '=',False)] ,
                }
            }


     
