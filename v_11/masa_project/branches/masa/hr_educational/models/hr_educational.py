# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_

class RecruitmentNeedsGrouping(models.Model):
    _inherit = "hr.recruitment.needs.grouping"

    j_type = fields.Selection([
        ('educational','Educational') ,
        ('general','General Administration')], related='job_id.j_type', string="Type", default="general" )


class RecruitmentNeeds(models.Model):
    _inherit = "hr.recruitment.needs"

    j_type = fields.Selection([
        ('educational','Educational') ,
        ('general','General Administration')], related='department_id.j_type', string="Type", default="general")


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    structure_type = fields.Selection([
        ('educational', 'Educational'),
        ('general', 'General Administration'),
        ('both', 'Both'),
    ], string='Type', index=True, required=False,default='general')


class Job(models.Model):
    _inherit = 'hr.job'

    j_type = fields.Selection([
        ('educational','Educational') ,
        ('general','General Administration')] ,string="Type", default="general", required="True" ,readonly=True, states={'draft':[('readonly',False)]})


class Department(models.Model):
    _inherit = "hr.department"
    
    j_type = fields.Selection([
        ('educational','Educational') ,
        ('general','General Administration')] ,string="Type", default="general", required="True" )
