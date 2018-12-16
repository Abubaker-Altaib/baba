# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import ValidationError

class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    type=fields.Selection([('holiday', 'Holiday'), ('excuse', 'Excuse'),
    						('public_holiday', 'Public Holiday'),('training','Training'),
    						('out_mission','External Mission'),('in_mission','Internal Mission')],
                            'Type', readonly=True)
    reference = fields.Reference(string='Related Model',
        selection=[('hr.holidays', 'Holiday'),
                 ('hr.mission.employee', 'Mission'),
                 ('resource.calendar.leaves', 'Public Holiday')])