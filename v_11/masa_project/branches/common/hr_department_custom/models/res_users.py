# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields, models,_
from odoo.exceptions import ValidationError


class ResUsers(models.Model):

	_inherit = 'res.users'

	@api.model
	def _get_department(self):
		return self.env.user.department_id

    
	department_ids = fields.Many2many('hr.department', 'hr_department_users_rel', 'user_id', 'department_id',
	string='Allowed Departments', default=_get_department)

	department_id = fields.Many2one('hr.department','Department')



