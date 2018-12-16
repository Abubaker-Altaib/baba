from odoo import api , fields,exceptions, models,_
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError


class add_accounts_and_lines_wizard(models.TransientModel):
	_name = "add.accounts.and.lines.wizard"

	parent_account_ids = fields.Many2many('account.account','account_add_rel','add_id','account_id', string='Parent Account' ,required=True,domain="[('user_type_id.type','=','view')]")
	  
	@api.multi
	def add_accounts_and_lines(self, data):
		#this fuction allows users to select parent accounts to add them in parent_account_budget_ids and generate budget lines for them
		saved_accounts=[]
		current_budget=self.env['crossovered.budget'].search([('id','=',data['active_id'])])

		for current_budget_accounts in current_budget.parent_account_budget_ids:
			saved_accounts.append(current_budget_accounts.account_id.id) 

		for parent_account_id in self.parent_account_ids :
			if parent_account_id.id not in saved_accounts:
				self.env["parent.account.budget"].create({'account_id':parent_account_id.id,
													  'amount' : 0 ,
													  'budget_id' : current_budget.id  })

				budgetary_positions=self.env['account.budget.post'].search([('account_id.parent_id','=',parent_account_id.id)
																   , ('account_id.internal_type', '!=' ,'view') ])
				parent_account_budget = self.env['parent.account.budget'].search([('account_id','=',parent_account_id.id),
					                                                                ('budget_id', '=', current_budget.id)])
				if budgetary_positions :
					for b in budgetary_positions :
						self.env["crossovered.budget.lines"].create({'parent_account_id':parent_account_id.id,
														  'general_budget_id':b.id ,
														  'planned_amount' : 0 ,
														  'crossovered_budget_id' : current_budget.id ,
											  'analytic_account_id':current_budget.analytic_account_id.id ,
											   'date_from':current_budget.date_from ,
												'date_to': current_budget.date_to ,
								  'parent_account_budget_id' : parent_account_budget.id})
				else :
					raise UserError(_("The Account (%s) has no budgetary positions")%parent_account_id.name)
			else :
				raise UserError(_("The Account (%s) has already been selected")%parent_account_id.name)	
						
