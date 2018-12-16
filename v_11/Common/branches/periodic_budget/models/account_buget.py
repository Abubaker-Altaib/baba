from odoo import api, fields, models , _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import time


class CustomBugetaryPosition(models.Model):
    _inherit = 'account.budget.post'
    class_type = fields.Selection([('normal' , 'Normal') , ('view' , 'View')], string='Classification Type')
    view_lines = fields.One2many('account.budget.post.line' ,'bugetary_position_id' )
    @api.model
    def create(self,vals):
        newid = super(CustomBugetaryPosition, self).create(vals)
        accounts = self.env['account.account'].search([('id' , 'in' ,  vals['account_ids'][0][2])])
        for account in accounts:
            self.env['account.budget.post.line'].create(
            {
                'type' : vals['type'],
                'code' : account.code,
                'name': account.name,
                'bugetary_position_id': newid.id
            
            
                })
        return newid
    @api.model
    def write(self, vals,context):
        return super(CustomBugetaryPosition, self).write(vals)
class BudgetPostLines(models.Model):
    _name = 'account.budget.post.line'
    bugetary_position_id = fields.Many2one('account.budget.post',string="")
    type = fields.Char(string="Type")
    code = fields.Char(string='Code')
    name = fields.Char(string="Name")

    
