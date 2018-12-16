# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models

class AttendanceWizard(models.TransientModel):
    _name = "attendance.wizard"

    
    start_date=fields.Date('Start Date')
    end_date= fields.Date('End Date')
    employees_ids=fields.Many2many('hr.employee',string='Employees')
   
    @api.multi
    def create_attendance_record(self):
        attendance_record = self.env['hr.attendance.record']
        process = attendance_record.process_attendance_record(self.start_date ,self.end_date,self.employees_ids)
        return process
       






