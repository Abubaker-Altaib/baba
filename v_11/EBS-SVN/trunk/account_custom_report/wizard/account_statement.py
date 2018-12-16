

from odoo import api ,osv, fields,exceptions, models,_
from odoo.exceptions import UserError, ValidationError

class account_statement_wiz(models.TransientModel):
	"""account statement wizard model"""
	_name= 'account.statement.wiz'

	account_id= fields.Many2one('account.account', 'Account', required=True)
	date_from= fields.Date(string="Start Date", required=True)
	date_to= fields.Date(string="End Date", required=True)
	target_moves= fields.Selection([('posted','All Posted Entries'),
									('all','All Entries')], 'Target Moves',
									 default='posted', widget='radio')

	def print_report(self, data):

		self.ensure_one()

		if self.date_from > self.date_to:
			raise ValidationError(_('Start Date must be equal to or less than Date To'))

		[data] = self.read()
		account_code = self.account_id.code
		account_name = self.account_id.name
		account_currency = self.account_id.currency_id.name

		datas = {
			'ids': [],
			'model': 'account.move.line',
			'account_id': data['account_id'],
			'account_code': account_code,
			'account_name': account_name,
			'account_currency': account_currency,
			'date_from': data['date_from'],
			'date_to': data['date_to'],
			'target_moves': data['target_moves'],
		}
		return self.env.ref('account_custom_report.account_statement_report_action').report_action(self, data=datas)