# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import UserError, ValidationError


class StrategicPolicy(models.Model):
    _name = "strategic.policy"
    _description = "Strategic Policy"
    _order = "sequence"

    name = fields.Char(string="Name",required=True )
    code = fields.Char(size=64, required=True, index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    sequence=fields.Integer(string='Sequence',required=True, copy=False)
    description=fields.Text(string='Description')
    date_start=fields.Date(string='Start date', index=True,copy=False)
    date_end=fields.Date(string='End date', index=True,copy=False)

    _sql_constraints = [
        ('code_Policy_uniq', 'unique (code,company_id)', _('Policy Code Must Be Unique Per Company.')),
    ]
    
    @api.multi
    @api.constrains('date_start','date_end')
    def _check_date_overlap(self):
        if self.date_start  and self.date_end:
            overlap_ids = self.search([('date_start','>',self.date_end),('date_end','<',self.date_start)])
            if overlap_ids:
                raise ValidationError(_(" End Date must be Greater than Start Date."))
    