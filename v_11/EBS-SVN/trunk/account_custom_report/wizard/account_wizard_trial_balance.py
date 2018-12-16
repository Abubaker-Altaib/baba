from odoo import fields, models


class Account_Balance_Wizard(models.TransientModel):
    _inherit = "account.balance.report"
    _description = 'Trial Balance wizard'


    parent_account_id = fields.Many2one('account.account', string='Parent Account')

  
    def pre_print_report(self, data):
        data = super(Account_Balance_Wizard,self).pre_print_report(data)
        data['form'].update(self.read(['parent_account_id'])[0])
        print("**********************data*********************",data)
        return data
        
    