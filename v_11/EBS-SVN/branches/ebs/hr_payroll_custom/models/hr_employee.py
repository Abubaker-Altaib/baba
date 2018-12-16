# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
import math

    
class Employee(models.Model):
    _inherit = "hr.employee"


    is_suspended =  fields.Boolean(string='Is Salary Suspended', deafult=False )
    tax_exempted = fields.Boolean(string = 'Tax Exempted', default=False)
