# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
###############################################################################
from odoo import tools
from odoo import models, fields, api, _
import urllib
import json
from odoo.exceptions import UserError


class HrAttendanceServer(models.Model):
    _name = 'hr.attendance.server'
    
    name = fields.Char(string='Name', required=True)
    server_ip = fields.Char(string='Server IP', required=True)
    port_no = fields.Integer(string='Port No', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    date = fields.Datetime(string='Last Fetch Date', readonly=True)
    password = fields.Char('Password', size=40)
    user = fields.Char('User', size=40)
    
    @api.multi
    def clear_attendance(self):
        return True
        
    @api.multi
    def download_attendance(self):
        try:
            url = 'http://'+self.server_ip+':'+str(self.port_no)
            req = urllib.request.Request(url)
            opener = urllib.request.build_opener()
            f = opener.open(req)
            jsons = f.read()
            jsons = jsons.decode('utf8').replace("'", '"')
            jsons = json.loads(jsons)
        except:
            raise UserError(_('Connection Faild!'))

        if jsons:
            last_fetch_date = False
            if self.date:
                last_fetch_date = fields.Datetime.from_string(self.date)
                jsons = filter(lambda x : fields.Datetime.from_string(x['datetime']) > last_fetch_date ,jsons)
            emps = self.env['hr.employee'].search([])
            emps = {int(x.barcode):int(x.id) for x in emps}

            attendance_obj = self.env['hr.attendance.log']
            for i in jsons:
                if last_fetch_date:
                    if fields.Datetime.from_string( i['datetime'] ) > last_fetch_date:
                        last_fetch_date = fields.Datetime.from_string( i['datetime'] )
                if not last_fetch_date:
                    last_fetch_date = fields.Datetime.from_string( i['datetime'] )

                action = i['action'] == "in" and 'check_in' or 'check_out'
                date_time = fields.Datetime.from_string( i['datetime'] )
                finger_id = int(i['id'])

                emp_id = finger_id in emps and emps[finger_id] or False
                if emp_id:
                    attendance_obj.create({'action':action,'action_datetime':date_time,'employee_id':emp_id,'state':'fetched'})
            self.date = last_fetch_date
        return True

    @api.multi
    def test_connection(self):
        flag = True
        try:
            url = 'http://'+self.server_ip+':'+str(self.port_no)
            req = urllib.request.Request(url)
            opener = urllib.request.build_opener()
            f = opener.open(req)
        except:
            flag = False
            
        
        if flag:
            raise UserError(_('Connected Successfully!'))
        else:
            raise UserError(_('Connection Faild!'))



