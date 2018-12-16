
from odoo import api, fields, models, _

class account_statement(models.AbstractModel):
	""" To account statement report """
	_name = 'report.account_custom_report.account_statement_report_tamplate'

	@api.model
	def get_report_values(self, docids, data=None):

		user_name = self.env['res.users'].browse(self._uid).name

		if data['target_moves'] == "posted":
			account_move_line = self.env['account.move.line'].search([
				('account_id','=',data['account_id'][0]),
				('move_id.state','=',data['target_moves']),
				('date_maturity','>=',data['date_from']),
				('date_maturity','<=',data['date_to'])
				])
		else:
			account_move_line = self.env['account.move.line'].search([
				('account_id','=',data['account_id'][0]),
				('date_maturity','>=',data['date_from']),
				('move_id.state','in',('draft','posted')),
				('date_maturity','<=',data['date_to'])
				])

		docargs = {
			'doc_ids': self.ids,
			'doc_model': 'account.move.line',
			'user_name': user_name,
			'account_id': data['account_id'],
			'account_code': data['account_code'],
			'account_name': data['account_name'],
			'account_currency': data['account_currency'],
			'date_from': data['date_from'],
			'date_to': data['date_to'],
			'target_moves': data['target_moves'],
			'docs': account_move_line,
			}
		return  docargs
