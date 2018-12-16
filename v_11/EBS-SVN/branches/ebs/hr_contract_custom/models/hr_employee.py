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


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    contract_state = fields.Selection(related='contract_id.state',string='State', store=True, readonly=True)