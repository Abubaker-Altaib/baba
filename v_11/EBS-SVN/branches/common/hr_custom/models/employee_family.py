# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit = "hr.employee"

    family_ids = fields.One2many('hr.employee.family','employee_id' ,string ="Employee Family")

class HrEmployeeFamily(models.Model):
    _name = 'hr.employee.family'

    name = fields.Char(string='Name of Sponsor', store=True, required=True)
    image = fields.Binary(string = "Image")
    relation = fields.Selection([('father', 'Father'),
                                 ('mother', 'Mother'),
                                 ('daughter', 'Daughter'),
                                 ('son', 'Son'),
                                 ('husband', 'husband'),
                                 ('wife', 'Wife')], string='Relationship', required=True, help='Relation with employee')
    birthday = fields.Date('Date of Birth')
    insurance_comp = fields.Char(string='Company')
    insurance_contract_no = fields.Char(string='Contract number')
    medical_insurance_no = fields.Char(string='Medical number')
    date_of_start_medical_insurance =fields.Date(string='Start date')
    date_of_end_medical_insurance =fields.Date(string='End date')
    employee_id = fields.Many2one('hr.employee', string="Employee",required=True , help='Select corresponding Employee')

    @api.constrains('date_of_start_medical_insurance','date_of_end_medical_insurance')
    def _greaterThanStartDate(self):
        for record in self:
            if record.date_of_end_medical_insurance:
                if record.date_of_end_medical_insurance < record.date_of_start_medical_insurance:
                    raise Warning(_("Date of end medical insurance must be greater than date of start of medical insurance!"))
