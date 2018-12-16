# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class hr_department(models.Model):
	"""
	inherit hr.department model
	"""
	_inherit = 'hr.department'

	@api.model
	def create(self,vals):
		'''
		override create function to set resposeble of department's analytic account  
		equals to department's manager
		'''
		ana_id = super(hr_department,self).create(vals)

		if self.manager_id.id != False and self.analytic_account_id.id != False:
			self.analytic_account_id.write({'user_id':self.manager_id.user_id.id})

		return ana_id

	@api.multi
	def write(self, vals):
		'''
		override write function to set resposeble of department's analytic account  
		equals to department's manager
		'''
		ana_id = super(hr_department,self).write(vals)

		if self.manager_id.id != False and self.analytic_account_id.id != False:
			self.analytic_account_id.write({'user_id':self.manager_id.user_id.id})

		return ana_id
		
