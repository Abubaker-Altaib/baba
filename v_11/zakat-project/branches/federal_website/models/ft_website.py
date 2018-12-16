# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models,api, exceptions,_
import re
from odoo.exceptions import ValidationError, AccessError 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

class ft_website(models.Model):
    _name = 'ft.website'

    code = fields.Char(string="Reference Number")
    nationality = fields.Selection([('sudanese' ,'Sudanese') , ('other' ,'Other')])
    name = fields.Char(string='Name')
    first_name = fields.Char()
    second_name = fields.Char()
    third_name = fields.Char()
    forth_name = fields.Char()


    national_number = fields.Char(string="National Number")
    passport = fields.Char(string="passport")
    phone = fields.Char(string="Phone Number")
    birth_date = fields.Date(string='Date of Birth')
    city = fields.Char()

    house_no = fields.Char()
    village = fields.Char()
    job = fields.Char(string="Job")

    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    state_id = fields.Char()
    local_state = fields.Char()
    ft_type = fields.Selection([('it' , 'Internal Treatment') , ('at' ,'Abroad Treatment') ,('drugs', 'Drugs, Treatments And Tests')])

    administrative_unit = fields.Char()
    treatment_amount = fields.Float()
    note = fields.Text()

