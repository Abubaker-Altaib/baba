# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import math
from datetime import timedelta
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError


class Holidays(models.Model):
    _inherit = "hr.holidays"

    place = fields.Selection([
        ('internal','Internal') ,
        ('external','External')], string='Place', default ='internal')
    alter_employee_id = fields.Many2one('hr.employee', string='Alternative Employee')
    cut_date = fields.Datetime(string='Cut Date')

    state = fields.Selection([
    ('draft', 'To Submit'),
    ('cancel', 'Cancelled'),
    ('programming', 'Programming'),
    ('confirm', 'To Approve'),
    ('refuse', 'Refused'),
    ('validate1', 'Second Approval'),
    ('validate', 'Approved'),('cut','Cut')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")
    is_altern_req = fields.Boolean(related="holiday_status_id.required_alternative" , string="Is Required Alternative")

    @api.multi
    def action_programming(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            return self.write({'state': 'draft'})
        else:
            return self.write({'state': 'programming'})

    @api.multi
    def confirm_programming(self):
        return self.write({'state': 'confirm'})

    
