# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api,fields, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import time

class AccountBudgetOperationInherit(models.Model):
	"""Inherit from Account Budget Operation in account_budget_custom module"""
	_inherit = 'account.budget.operation'

	state= fields.Selection([('draft', 'Draft'), ('complete', 'Waiting for Head of Financial Section Approve'), 
                                    ('confirm', 'Waiting for Head of Financial Manager Approve'), ('approve', 'Waiting for General Manager Approve'),
                                    ('done','Done'), ('cancel', 'Canceled')], 'Status', required=True, readonly=True,default='draft')

	analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

	def action_cancel_complete(self):
		return self.write({'state':'complete'})

	def action_cancel_approve(self):
		return self.write({'state':'confirm'})

	def approve_done(self):
		if self.type == 'transfer':
			return super(AccountBudgetOperationInherit, self).done()
		else:
			return super(AccountBudgetOperationInherit, self).approve()


	@api.model
	def create(self, vals):
		create_id = super(AccountBudgetOperationInherit,self).create(vals)
		if create_id.type == 'transfer':
			for line in create_id.line_ids:
				line.write({'line_ids_analytic_account_id':vals['analytic_account_id']})

		return create_id


	@api.multi
	def write(self, vals):
		write_id = super(AccountBudgetOperationInherit,self).write(vals)
		if self.type == 'transfer':
			for line in self.line_ids:
				line.write({'line_ids_analytic_account_id':self.analytic_account_id.id})
		return write_id


	@api.onchange('analytic_account_id')
	def onchange_type(self):
		self.budget_line = False
		self.line_ids = False
       

class AccountBudgetLineIdsInherit(models.Model):
	"""docstring for ClassName"""
	_inherit = "account.budget.operation.line"
	line_ids_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

