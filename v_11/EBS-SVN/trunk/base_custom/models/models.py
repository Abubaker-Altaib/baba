# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class base_custom(models.Model):
#     _name = 'base_custom.base_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class hr_department(models.Model):
	"""docstring for base_custom"""
	_inherit = 'hr.department'
	analytic_account_id = fields.Many2one("account.analytic.account", "Analytic Account")
	account_ids = fields.Many2many("account.account","department_account_rel","dept_id","account_id","Accounts")

