from odoo import api , fields,exceptions, models,_
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError


class add_account_wizard(models.TransientModel):
    _name = "add.account.wizard"
    parent_account_id = fields.Many2one('account.account', string='Parent Account' , required=True  )

    @api.multi
    def search_accounts(self):
        accounts = self.env['account.account'].search([('parent_id','=', self.parent_account_id.id),('user_type_id.type','!=','view')])
        current_dept=self.env['hr.department'].search([('id','=',self.env.context.get('active_id'))])
        for account in accounts :
        	current_dept.write({'account_ids':[(4,account.id)]})
        return True