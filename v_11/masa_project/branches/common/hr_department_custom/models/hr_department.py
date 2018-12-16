# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import models, fields, api

class hr_department(models.Model):
	_inherit = 'hr.department'

	analytic_account_id = fields.Many2one("account.analytic.account", "Analytic Account")


	@api.model
	def create(self,vals):
		'''
		override create function to set responsible of department's analytic account  
		equals to department's manager
		'''
		ana_id = super(hr_department,self).create(vals)

		if self.manager_id.id != False and self.analytic_account_id.id != False:
			self.analytic_account_id.write({'user_id':self.manager_id.user_id.id})

		return ana_id

	@api.multi
	def write(self, vals):
		'''
		override write function to set responsible of department's analytic account  
		equals to department's manager
		'''
		ana_id = super(hr_department,self).write(vals)

		if self.manager_id.id != False and self.analytic_account_id.id != False:
			self.analytic_account_id.write({'user_id':self.manager_id.user_id.id})

		return ana_id




class AccountAnalytic(models.Model):

    _inherit = "account.analytic.account"


    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    user_id= fields.Many2one('res.users',string='Responsible',required=True ,default=_default_user,readonly=True)


