# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import UserError, ValidationError


class StrategicDomain(models.Model):
    _name = "strategic.domain"
    _description = "Strategic Domain"
    
    name = fields.Char(string="Name",required=True)
    code = fields.Char(size=64, required=True, index=True)
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    
