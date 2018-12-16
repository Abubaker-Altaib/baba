# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from datetime import date, datetime

class AttendanceWizard(models.TransientModel):
    _name = "attendance.wizard"

    
    start_date=fields.Date('Start Date')
    end_date= fields.Date('End Date')
    employees_ids=fields.Many2many('hr.employee',string='Employees')
   
    @api.multi
    def create_attendance_record(self):
        attendance_record = self.env['hr.attendance']
        start_date = fields.Date.from_string(str(self.start_date))
        end_date = fields.Date.from_string(str(self.end_date))

        process = attendance_record.process_attendance_record(start_date ,end_date,self.employees_ids)
        return process
       






