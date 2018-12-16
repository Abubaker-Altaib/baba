from odoo import fields, models


class debt_reconstruction_wizard(models.TransientModel):
   
    _name = 'debt.reconstruction.wizard'
    _description = 'Debt Reconstruction wizard'


    account_parent_id = fields.Many2one('account.account', string='Parent Account')
    date_from= fields.Date(string="Start Date")
    date_to= fields.Date(string="End Date")


    def print_report(self, data): 
        self.ensure_one()
        [data] = self.read()
        
        account_code = self.account_parent_id.code
        account_name = self.account_parent_id.name
        account_currency = self.account_parent_id.currency_id.name
        
        datas = {
        'ids': [],
        'model': 'account.move.line',
        'account_parent_id': data['account_parent_id'],
        'account_name':  account_name,
        'account_code':  account_code,
        'account_currency': account_currency,
        'date_from': data['date_from'],
        'date_to': data['date_to'],
        
   
        }
        return self.env.ref('account_custom_report.action_report_debt_reconstruction').report_action(self, data=datas)
 
