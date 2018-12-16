# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models

class HrAttendanceRecord(models.Model):
    _inherit='hr.attendance.record' 

    @api.multi
    def record_scheduler(self):
        time=datetime.now() - relativedelta(days=1)
        date=time.strftime('%Y-%m-%d')
        employee_ids = self.env['hr.employee'].search([])
        record = self.env['hr.attendance.record'].process_attendance_record(date ,date,employee_ids)
        return True
