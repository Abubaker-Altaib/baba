# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models

class AccountApprove(models.Model):
    _name= 'account.approve'

    name= fields.Char(string='Name')
    employee_ids= fields.Many2many("hr.employee", "account_approve_rel_hr_employee", "account_id", "employee_id", required=True, string='Employees')
    min_amount= fields.Float(string='Min Amount')
    max_amount= fields.Float(string='Max amount')
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id)


class ResCompany(models.Model):
    """ Inherit company model to add field auto_budget to be used in the
	create confirmation  as a condition when it is true to automatically
	check budget.
	"""
    _inherit = "res.company"

    auto_budget = fields.Boolean(string='Automatic Budget Check for vouchers.',default=True)

    ## TO DO: Mudither please check : DONE
    account_approve_ids = fields.One2many('account.approve','company_id',string='Approve')

    

