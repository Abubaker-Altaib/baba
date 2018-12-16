# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
import math

class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"
    
    payslip_type = fields.Selection([
        ('paid','Paid') ,
        ('unpaid','Unpaid') ,
        ('percentage','Percentage') ,
        ('addition','Addition') ,
        ('exclusion','Exclusion') ] ,string = "Payslip Type" , default="paid", required=True)
    rule_ids = fields.Many2many('hr.salary.rule',string = "Rules")
    percentage =fields.Float(string='Percentage')
    