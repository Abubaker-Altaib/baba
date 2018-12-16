# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import ValidationError, UserError

class Employee(models.Model):

    _inherit = 'hr.employee'
    
    struct_id = fields.Many2one(string="Structure", related='contract_id.struct_id', readonly=True)
    level_id = fields.Many2one(string="Level", related='contract_id.level_id', readonly=True)
    grade_id = fields.Many2one(string="Grade", related='contract_id.grade_id', readonly=True)
    degree_id = fields.Many2one(string="Degree", related='contract_id.degree_id', readonly=True)
    last_bonus_date = fields.Date('Last Bonus Date')
    contract_id = fields.Many2one('hr.contract', compute='_compute_contract_id', string='Current Contract', help='Latest permanent contract of the employee',store=True,)

    @api.depends('contract_ids')
    def _compute_contract_id(self):
        """ get employee permanent contract """

        Contract = self.env['hr.contract']
        for employee in self:
            employee.contract_id = Contract.search([('employee_id', '=', employee.id)], order='date_start desc', limit=1)
            # ('type','=','permanent'),
    
    
    


