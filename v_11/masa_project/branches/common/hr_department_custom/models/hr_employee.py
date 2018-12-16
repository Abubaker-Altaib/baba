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

	@api.model
	def create(self,vals):
		#Create Related User When Creating New Employee
		user_data={}
		if vals.get('name'):
			user_data.update({'name':vals.get('name')})
		if vals.get('work_email'):
			user_data.update({'login':vals.get('work_email')})
		else:
			user_data.update({'login':vals.get('name').split()[0]})
		if vals.get('department_id'):
			user_data.update({'department_id':vals.get('department_id')})

		user=self.env['res.users'].create(user_data)
		if user.partner_id:
			user.partner_id.employee=True
			vals.update({'address_home_id':user.partner_id.id})
		vals.update({'user_id':user.id})

		return super(HrEmployee,self).create(vals)


	@api.multi
	def write(self,vals):
		for rec in self:
			#Update Related user's Department when updating Employee Department
			if vals.get('department_id'):
				rec.user_id.write({'department_id':vals.get('department_id')})
			if vals.get('user_id'):
				if vals.get('department_id'):
					department = vals.get('department_id')
				else:
					department = rec.department_id.id
				self.env['res.users'].browse(vals.get('user_id')).department_id = department

		return super(HrEmployee,self).write(vals)


