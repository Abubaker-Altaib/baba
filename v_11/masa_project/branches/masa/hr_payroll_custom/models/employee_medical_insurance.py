# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import fields, models

class InsuranceCategory(models.Model):
    _inherit = "hr.insurance.category"

    level_id = fields.Many2many('hr.payroll.structure',string="Level",domain=[('type','=','level')])
    grade_id = fields.Many2many('hr.payroll.structure',string="Grade",domain=[('type','=','grade')])
    degree_id = fields.Many2many('hr.payroll.structure',string="Degree",domain=[('type','=','degree')])
