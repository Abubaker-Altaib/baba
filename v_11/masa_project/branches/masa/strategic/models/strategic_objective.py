# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api , fields,exceptions, tools, models,_
from odoo.exceptions import UserError, ValidationError


class StrategicObjective(models.Model):
    _name = "strategic.objective"
    _description = "Strategic Objective"

    name = fields.Char(string="Name",required=True )
    code = fields.Char(size=64, required=True, index=True)
    active = fields.Boolean(default=True)
    type = fields.Selection([
            ('strategic','Strategic'),
            ('executive','Executive'),],required=True
            )
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    domain_id=fields.Many2one('strategic.domain',ondelete='cascade', index=True, required=True)
    kpi_id=fields.Many2one('strategic.kpi',ondelete='cascade', index=True, required=True,string="Strategic Kpi")
