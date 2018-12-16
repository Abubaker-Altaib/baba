# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, models,_
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):

	_inherit = 'hr.employee'

	def _sync_user(self, user):
		# return dict(
		#     name=user.name,
		#     image=user.image,
		#     work_email=user.email,
		# )
		return dict()

	@api.model
	def create(self,vals):
		"""
		Override create method to create a new user for the employee

		@return: super create method
		"""
		create_id = super(HrEmployee,self).create(vals)
		user_obj = self.env['res.users']
		partner_obj = self.env['res.partner']
		user_dict = {
			'name': vals['name'],
		    'login': vals.get('barcode') or vals['name'][:4],
		    'password': vals.get('barcode') or vals['name'][:4],
		    'department_id': vals.get('department_id'),
		    'company_id': vals.get('company_id'),
		}
		if vals.get('user_id',False):
			create_id.user_id.write(user_dict)
			create_id.user_id.partner_id.write({'employee': True})
			create_id.write({'address_home_id':user_id.partner_id.id})

		else:
			user_id = user_obj.create(user_dict)
			create_id.write({'user_id':user_id.id,'address_home_id':user_id.partner_id.id})

		return create_id



	@api.multi
	def write(self,vals):
		for rec in self:
			#Update Related user's Department when updating Employee Department
			super(HrEmployee,rec).write(vals)
			if vals.get('department_id'):
				rec.user_id.write({'department_id':vals.get('department_id')})
			if vals.get('user_id'):
				if vals.get('department_id'):
					department = vals.get('department_id')
				else:
					department = rec.department_id.id
				user = self.env['res.users'].search([('id','=',vals['user_id'])])
				user.write({'department_id':department,
							#'department_ids':[(6, 0, [department])]
							})

		return True


